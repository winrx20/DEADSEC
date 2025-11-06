# Windows Privilege Escalation Checker - Native PowerShell
# No Python Required - For authorized penetration testing only

param(
    [string]$OutputFile = ".\privesc_findings.txt",
    [switch]$Silent
)

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    if (-not $Silent) {
        $color = switch ($Level) {
            "HIGH" { "Red" }
            "MEDIUM" { "Yellow" }
            "LOW" { "Cyan" }
            default { "White" }
        }
        Write-Host "[$Level] $Message" -ForegroundColor $color
    }
}

function Add-Finding {
    param(
        [string]$Category,
        [string]$Severity,
        [string]$Description,
        [string]$Details = ""
    )
    
    $finding = @"

[$Severity] $Category
Description: $Description
$(if ($Details) { "Details:`n$Details" })
$("-"*70)
"@
    
    Add-Content -Path $OutputFile -Value $finding
    Write-Log "$Category - $Description" -Level $Severity
}

Write-Log "Windows Privilege Escalation Checker"
Write-Log "Output: $OutputFile"
Write-Log "="*70 "INFO"

# Create output file with header
$header = @"
Windows Privilege Escalation Check Report
Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Computer: $env:COMPUTERNAME
User: $env:USERNAME
Domain: $env:USERDOMAIN
$("="*70)

"@

Set-Content -Path $OutputFile -Value $header

# Check current privileges
Write-Log "Checking current user privileges..."
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

Add-Content -Path $OutputFile -Value @"
Current User: $($currentUser.Name)
Is Administrator: $isAdmin
Authentication Type: $($currentUser.AuthenticationType)
"@

if ($isAdmin) {
    Write-Log "Already running as Administrator" "LOW"
} else {
    Write-Log "Running as standard user - checking for escalation vectors..." "INFO"
}

# Check 1: AlwaysInstallElevated
Write-Log "Checking AlwaysInstallElevated registry keys..."
try {
    $hkcu = Get-ItemProperty -Path "HKCU:\SOFTWARE\Policies\Microsoft\Windows\Installer" -Name AlwaysInstallElevated -ErrorAction SilentlyContinue
    $hklm = Get-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Installer" -Name AlwaysInstallElevated -ErrorAction SilentlyContinue
    
    if ($hkcu.AlwaysInstallElevated -eq 1 -and $hklm.AlwaysInstallElevated -eq 1) {
        Add-Finding -Category "AlwaysInstallElevated" -Severity "HIGH" `
            -Description "AlwaysInstallElevated is enabled in both HKCU and HKLM" `
            -Details "MSI packages can be installed with SYSTEM privileges. Create a malicious MSI to escalate privileges."
    }
} catch { }

# Check 2: Unquoted Service Paths
Write-Log "Checking for unquoted service paths..."
$services = Get-WmiObject -Class Win32_Service | Where-Object { 
    $_.PathName -notmatch '^"' -and 
    $_.PathName -match ' ' -and 
    $_.PathName -notmatch 'system32'
}

if ($services) {
    $details = $services | ForEach-Object { "$($_.Name): $($_.PathName)" } | Out-String
    Add-Finding -Category "Unquoted Service Paths" -Severity "MEDIUM" `
        -Description "Found $($services.Count) services with unquoted paths containing spaces" `
        -Details $details
}

# Check 3: Writable Service Binaries
Write-Log "Checking for writable service binaries..."
Get-WmiObject -Class Win32_Service | ForEach-Object {
    $servicePath = $_.PathName -replace '"', '' -split '\s+' | Select-Object -First 1
    if (Test-Path $servicePath -ErrorAction SilentlyContinue) {
        try {
            $acl = Get-Acl $servicePath -ErrorAction SilentlyContinue
            $writableByUser = $acl.Access | Where-Object {
                $_.IdentityReference -match $env:USERNAME -and 
                ($_.FileSystemRights -match "Write|FullControl|Modify")
            }
            
            if ($writableByUser) {
                Add-Finding -Category "Writable Service Binary" -Severity "HIGH" `
                    -Description "Service binary is writable by current user" `
                    -Details "Service: $($_.Name)`nPath: $servicePath"
            }
        } catch { }
    }
}

# Check 4: Writable Service Registry Keys
Write-Log "Checking for writable service registry keys..."
try {
    $serviceKeys = Get-ChildItem -Path "HKLM:\SYSTEM\CurrentControlSet\Services" -ErrorAction SilentlyContinue
    foreach ($key in $serviceKeys) {
        try {
            $acl = Get-Acl -Path "Registry::$($key.Name)" -ErrorAction SilentlyContinue
            $writable = $acl.Access | Where-Object {
                $_.IdentityReference -match "Users|Everyone|$env:USERNAME" -and
                ($_.RegistryRights -match "WriteKey|FullControl")
            }
            
            if ($writable) {
                Add-Finding -Category "Writable Service Registry" -Severity "HIGH" `
                    -Description "Service registry key is writable" `
                    -Details "Service: $($key.PSChildName)"
            }
        } catch { }
    }
} catch { }

# Check 5: Scheduled Tasks with Writable Binaries
Write-Log "Checking scheduled tasks..."
try {
    $tasks = Get-ScheduledTask -ErrorAction SilentlyContinue | Where-Object { $_.TaskPath -notmatch "Microsoft" }
    foreach ($task in $tasks) {
        $action = $task.Actions | Select-Object -First 1
        if ($action.Execute) {
            $taskPath = $action.Execute
            if (Test-Path $taskPath -ErrorAction SilentlyContinue) {
                try {
                    $acl = Get-Acl $taskPath -ErrorAction SilentlyContinue
                    $writable = $acl.Access | Where-Object {
                        $_.IdentityReference -match "Users|Everyone|$env:USERNAME" -and
                        ($_.FileSystemRights -match "Write|FullControl|Modify")
                    }
                    
                    if ($writable) {
                        Add-Finding -Category "Writable Scheduled Task Binary" -Severity "MEDIUM" `
                            -Description "Scheduled task binary is writable" `
                            -Details "Task: $($task.TaskName)`nPath: $taskPath"
                    }
                } catch { }
            }
        }
    }
} catch { }

# Check 6: DLL Hijacking - Writable System32 Directories
Write-Log "Checking for writable directories in PATH..."
$paths = $env:PATH -split ';'
foreach ($path in $paths) {
    if (Test-Path $path -ErrorAction SilentlyContinue) {
        try {
            $acl = Get-Acl $path -ErrorAction SilentlyContinue
            $writable = $acl.Access | Where-Object {
                $_.IdentityReference -match "Users|Everyone|$env:USERNAME" -and
                ($_.FileSystemRights -match "Write|FullControl|Modify")
            }
            
            if ($writable) {
                Add-Finding -Category "Writable PATH Directory" -Severity "MEDIUM" `
                    -Description "Directory in PATH is writable (potential DLL hijacking)" `
                    -Details "Path: $path"
            }
        } catch { }
    }
}

# Check 7: SeImpersonatePrivilege (Potato attacks)
Write-Log "Checking for dangerous privileges..."
$privs = whoami /priv
if ($privs -match "SeImpersonatePrivilege.*Enabled") {
    Add-Finding -Category "SeImpersonatePrivilege" -Severity "HIGH" `
        -Description "SeImpersonatePrivilege is enabled" `
        -Details "Can use Potato exploits (JuicyPotato, RoguePotato, PrintSpoofer) to escalate to SYSTEM"
}
if ($privs -match "SeAssignPrimaryTokenPrivilege.*Enabled") {
    Add-Finding -Category "SeAssignPrimaryTokenPrivilege" -Severity "HIGH" `
        -Description "SeAssignPrimaryTokenPrivilege is enabled" `
        -Details "Can create processes with arbitrary tokens"
}
if ($privs -match "SeBackupPrivilege.*Enabled") {
    Add-Finding -Category "SeBackupPrivilege" -Severity "MEDIUM" `
        -Description "SeBackupPrivilege is enabled" `
        -Details "Can read any file on the system (including SAM database)"
}

# Check 8: Password in Registry
Write-Log "Searching for passwords in registry..."
$regKeys = @(
    "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon",
    "HKCU:\Software\ORL\WinVNC3\Password",
    "HKCU:\Software\TightVNC\Server",
    "HKLM:\SYSTEM\CurrentControlSet\Services\SNMP"
)

foreach ($key in $regKeys) {
    if (Test-Path $key) {
        try {
            $props = Get-ItemProperty -Path $key -ErrorAction SilentlyContinue
            $passwordProps = $props.PSObject.Properties | Where-Object { $_.Name -match "password|pwd" }
            
            if ($passwordProps) {
                $details = $passwordProps | ForEach-Object { "$($_.Name): $($_.Value)" } | Out-String
                Add-Finding -Category "Password in Registry" -Severity "MEDIUM" `
                    -Description "Found password-related values in registry" `
                    -Details "Key: $key`n$details"
            }
        } catch { }
    }
}

# Check 9: Saved Credentials
Write-Log "Checking for saved credentials..."
$savedCreds = cmdkey /list
if ($savedCreds -match "Target:") {
    Add-Finding -Category "Saved Credentials" -Severity "MEDIUM" `
        -Description "Found saved credentials in Windows Credential Manager" `
        -Details $savedCreds
}

# Check 10: Installed Software (vulnerable versions)
Write-Log "Checking for potentially vulnerable installed software..."
$vulnerableSoftware = @(
    "FileZilla",
    "WinSCP",
    "VNC",
    "TeamViewer"
)

$installed = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue |
    Where-Object { $_.DisplayName -match ($vulnerableSoftware -join '|') } |
    Select-Object DisplayName, DisplayVersion

if ($installed) {
    $details = $installed | ForEach-Object { "$($_.DisplayName) - $($_.DisplayVersion)" } | Out-String
    Add-Finding -Category "Potentially Vulnerable Software" -Severity "LOW" `
        -Description "Found software that may store credentials or have vulnerabilities" `
        -Details $details
}

# Check 11: Startup Folder Permissions
Write-Log "Checking startup folder permissions..."
$startupFolders = @(
    "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup",
    "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"
)

foreach ($folder in $startupFolders) {
    if (Test-Path $folder) {
        try {
            $acl = Get-Acl $folder -ErrorAction SilentlyContinue
            $writable = $acl.Access | Where-Object {
                $_.IdentityReference -match "Users|Everyone|$env:USERNAME" -and
                ($_.FileSystemRights -match "Write|FullControl|Modify")
            }
            
            if ($writable) {
                Add-Finding -Category "Writable Startup Folder" -Severity "LOW" `
                    -Description "Startup folder is writable" `
                    -Details "Folder: $folder`nCan place malicious executables for persistence/privilege escalation"
            }
        } catch { }
    }
}

# Check 12: Weak Folder Permissions in Program Files
Write-Log "Checking Program Files folder permissions..."
$programDirs = @("$env:ProgramFiles", "${env:ProgramFiles(x86)}")
foreach ($dir in $programDirs) {
    if (Test-Path $dir) {
        Get-ChildItem -Path $dir -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            try {
                $acl = Get-Acl $_.FullName -ErrorAction SilentlyContinue
                $writable = $acl.Access | Where-Object {
                    $_.IdentityReference -match "Users|Everyone|$env:USERNAME" -and
                    ($_.FileSystemRights -match "Write|FullControl|Modify")
                }
                
                if ($writable) {
                    Add-Finding -Category "Writable Program Folder" -Severity "MEDIUM" `
                        -Description "Program folder has weak permissions" `
                        -Details "Folder: $($_.FullName)"
                }
            } catch { }
        }
    }
}

# Summary
Write-Log "Generating summary..." "INFO"

$summary = @"

$("="*70)
PRIVILEGE ESCALATION CHECK COMPLETE
$("="*70)

Review the findings above and prioritize by severity:
- HIGH: Direct privilege escalation vectors
- MEDIUM: Potential escalation with additional steps
- LOW: Informational / lower priority

Completed: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
$("="*70)
"@

Add-Content -Path $OutputFile -Value $summary

Write-Log "`nPrivilege escalation check complete!" "INFO"
Write-Log "Report saved to: $OutputFile" "INFO"

# Display summary of findings
if (-not $Silent) {
    Write-Host "`n[+] Finding Summary:" -ForegroundColor Green
    
    $content = Get-Content $OutputFile -Raw
    $highCount = ([regex]::Matches($content, "\[HIGH\]")).Count
    $mediumCount = ([regex]::Matches($content, "\[MEDIUM\]")).Count
    $lowCount = ([regex]::Matches($content, "\[LOW\]")).Count
    
    Write-Host "  HIGH Severity: $highCount" -ForegroundColor Red
    Write-Host "  MEDIUM Severity: $mediumCount" -ForegroundColor Yellow
    Write-Host "  LOW Severity: $lowCount" -ForegroundColor Cyan
    Write-Host "`n  Full report: $OutputFile" -ForegroundColor White
}
