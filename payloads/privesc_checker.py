#!/usr/bin/env python3
"""
Privilege Escalation Helper - Post-Exploitation Module
Checks for common privilege escalation vectors
For authorized penetration testing only
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

class PrivEscChecker:
    def __init__(self):
        self.os_type = platform.system()
        self.findings = []
        
    def check_all(self):
        """Run all privilege escalation checks"""
        print("="*60)
        print("Privilege Escalation Checker")
        print("="*60 + "\n")
        
        if self.os_type == "Linux":
            self.check_linux()
        elif self.os_type == "Windows":
            self.check_windows()
        elif self.os_type == "Darwin":
            self.check_macos()
        
        self.print_summary()
        return self.findings
    
    def add_finding(self, category, severity, description, details=""):
        """Add a finding"""
        self.findings.append({
            'category': category,
            'severity': severity,
            'description': description,
            'details': details
        })
        
        severity_colors = {'HIGH': '+', 'MEDIUM': '*', 'LOW': '-'}
        symbol = severity_colors.get(severity, '*')
        print(f"  [{symbol}] [{severity}] {description}")
        if details:
            for line in details.split('\n'):
                if line.strip():
                    print(f"      {line}")
    
    def check_linux(self):
        """Check for Linux privilege escalation vectors"""
        print("[*] Running Linux privilege escalation checks...\n")
        
        # Check if root
        if os.geteuid() == 0:
            self.add_finding('User', 'HIGH', 'Already running as root!')
            return
        
        # SUID binaries
        print("[*] Checking for SUID binaries...")
        try:
            result = subprocess.run(
                ['find', '/', '-perm', '-4000', '-type', 'f', '2>/dev/null'],
                capture_output=True,
                text=True,
                timeout=30,
                shell=True
            )
            suid_files = result.stdout.strip().split('\n')
            
            dangerous_suid = ['nmap', 'vim', 'nano', 'find', 'python', 'perl', 'ruby', 
                            'gcc', 'docker', 'mount', 'umount']
            
            for suid in suid_files:
                if any(dangerous in suid for dangerous in dangerous_suid):
                    self.add_finding('SUID', 'HIGH', f'Dangerous SUID binary: {suid}')
        except:
            pass
        
        # Sudo permissions
        print("\n[*] Checking sudo permissions...")
        try:
            result = subprocess.run(['sudo', '-l'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.add_finding('Sudo', 'HIGH', 'User has sudo permissions', result.stdout)
        except:
            pass
        
        # Writable /etc/passwd
        print("\n[*] Checking /etc/passwd permissions...")
        if os.access('/etc/passwd', os.W_OK):
            self.add_finding('File Permissions', 'HIGH', '/etc/passwd is writable!')
        
        # Writable /etc/shadow
        if os.access('/etc/shadow', os.W_OK):
            self.add_finding('File Permissions', 'HIGH', '/etc/shadow is writable!')
        
        # Cron jobs
        print("\n[*] Checking cron jobs...")
        cron_dirs = ['/etc/cron.d', '/etc/cron.daily', '/etc/cron.hourly', '/etc/cron.monthly', '/etc/cron.weekly']
        for cron_dir in cron_dirs:
            if os.path.exists(cron_dir):
                try:
                    for item in os.listdir(cron_dir):
                        item_path = os.path.join(cron_dir, item)
                        if os.access(item_path, os.W_OK):
                            self.add_finding('Cron', 'MEDIUM', f'Writable cron job: {item_path}')
                except:
                    pass
        
        # Check for docker group
        print("\n[*] Checking group memberships...")
        try:
            result = subprocess.run(['groups'], capture_output=True, text=True)
            groups = result.stdout
            if 'docker' in groups:
                self.add_finding('Groups', 'HIGH', 'User is in docker group (can escalate to root)')
            if 'lxd' in groups:
                self.add_finding('Groups', 'HIGH', 'User is in lxd group (can escalate to root)')
        except:
            pass
        
        # Writable systemd services
        print("\n[*] Checking systemd services...")
        systemd_dirs = ['/etc/systemd/system', '/usr/lib/systemd/system']
        for systemd_dir in systemd_dirs:
            if os.path.exists(systemd_dir) and os.access(systemd_dir, os.W_OK):
                self.add_finding('Systemd', 'HIGH', f'Writable systemd directory: {systemd_dir}')
        
        # Kernel version
        print("\n[*] Checking kernel version...")
        try:
            result = subprocess.run(['uname', '-r'], capture_output=True, text=True)
            kernel = result.stdout.strip()
            self.add_finding('Kernel', 'LOW', f'Kernel version: {kernel}', 'Check for kernel exploits')
        except:
            pass
    
    def check_windows(self):
        """Check for Windows privilege escalation vectors"""
        print("[*] Running Windows privilege escalation checks...\n")
        
        # Check if admin
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if is_admin:
                self.add_finding('User', 'HIGH', 'Already running as Administrator!')
                return
        except:
            pass
        
        # Check for AlwaysInstallElevated
        print("[*] Checking AlwaysInstallElevated...")
        try:
            import winreg
            
            keys_to_check = [
                (winreg.HKEY_CURRENT_USER, r'SOFTWARE\Policies\Microsoft\Windows\Installer'),
                (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Policies\Microsoft\Windows\Installer')
            ]
            
            always_install_elevated = True
            for hive, path in keys_to_check:
                try:
                    key = winreg.OpenKey(hive, path)
                    value, _ = winreg.QueryValueEx(key, 'AlwaysInstallElevated')
                    if value != 1:
                        always_install_elevated = False
                    winreg.CloseKey(key)
                except:
                    always_install_elevated = False
            
            if always_install_elevated:
                self.add_finding('Registry', 'HIGH', 'AlwaysInstallElevated is enabled!')
        except:
            pass
        
        # Check for unquoted service paths
        print("\n[*] Checking for unquoted service paths...")
        try:
            result = subprocess.run(
                ['wmic', 'service', 'get', 'name,displayname,pathname,startmode'],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.split('\n'):
                if 'Auto' in line and 'C:\\' in line:
                    path = line.split('C:\\')[1].split()[0]
                    if ' ' in path and not path.startswith('"'):
                        self.add_finding('Services', 'MEDIUM', f'Unquoted service path: C:\\{path}')
        except:
            pass
        
        # Check for weak service permissions
        print("\n[*] Checking service permissions...")
        try:
            result = subprocess.run(['sc', 'query'], capture_output=True, text=True)
            # This would require more detailed checking with accesschk.exe
            self.add_finding('Services', 'LOW', 'Check service permissions manually with accesschk.exe')
        except:
            pass
        
        # Check scheduled tasks
        print("\n[*] Checking scheduled tasks...")
        try:
            result = subprocess.run(
                ['schtasks', '/query', '/fo', 'LIST', '/v'],
                capture_output=True,
                text=True
            )
            self.add_finding('Tasks', 'LOW', 'Review scheduled tasks for writable paths')
        except:
            pass
        
        # Check for saved credentials
        print("\n[*] Checking for saved credentials...")
        try:
            result = subprocess.run(['cmdkey', '/list'], capture_output=True, text=True)
            if 'Target:' in result.stdout:
                self.add_finding('Credentials', 'MEDIUM', 'Saved credentials found', result.stdout)
        except:
            pass
    
    def check_macos(self):
        """Check for macOS privilege escalation vectors"""
        print("[*] Running macOS privilege escalation checks...\n")
        
        # Check if root
        if os.geteuid() == 0:
            self.add_finding('User', 'HIGH', 'Already running as root!')
            return
        
        # Check sudo permissions
        print("[*] Checking sudo permissions...")
        try:
            result = subprocess.run(['sudo', '-l'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.add_finding('Sudo', 'HIGH', 'User has sudo permissions', result.stdout)
        except:
            pass
        
        # Check for writable applications
        print("\n[*] Checking application permissions...")
        apps_dir = '/Applications'
        if os.path.exists(apps_dir):
            for app in os.listdir(apps_dir):
                app_path = os.path.join(apps_dir, app)
                if os.access(app_path, os.W_OK):
                    self.add_finding('Applications', 'MEDIUM', f'Writable application: {app_path}')
    
    def print_summary(self):
        """Print summary of findings"""
        print("\n" + "="*60)
        print("Summary")
        print("="*60 + "\n")
        
        high = sum(1 for f in self.findings if f['severity'] == 'HIGH')
        medium = sum(1 for f in self.findings if f['severity'] == 'MEDIUM')
        low = sum(1 for f in self.findings if f['severity'] == 'LOW')
        
        print(f"Total findings: {len(self.findings)}")
        print(f"  HIGH:   {high}")
        print(f"  MEDIUM: {medium}")
        print(f"  LOW:    {low}")
        
        if high > 0:
            print("\n[!] High severity findings detected!")
            print("[!] Investigate these vectors for privilege escalation")
    
    def save_report(self, output_file='privesc_report.txt'):
        """Save report to file"""
        with open(output_file, 'w') as f:
            f.write("Privilege Escalation Check Report\n")
            f.write("="*60 + "\n\n")
            
            for finding in self.findings:
                f.write(f"[{finding['severity']}] {finding['category']}\n")
                f.write(f"  {finding['description']}\n")
                if finding['details']:
                    f.write(f"  Details:\n")
                    for line in finding['details'].split('\n'):
                        if line.strip():
                            f.write(f"    {line}\n")
                f.write("\n")
        
        print(f"\n[+] Report saved to: {output_file}")

def main():
    print("="*60)
    print("Privilege Escalation Checker - Red Team Tool")
    print("For Authorized Penetration Testing Only")
    print("="*60 + "\n")
    
    checker = PrivEscChecker()
    checker.check_all()
    checker.save_report()

if __name__ == '__main__':
    main()
