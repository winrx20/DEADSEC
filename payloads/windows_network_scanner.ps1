# Windows Network Scanner - Native PowerShell
# No Python Required - For authorized penetration testing only

param(
    [string]$Network = "",  # e.g., "192.168.1.0/24" (auto-detect if empty)
    [string]$OutputFile = ".\network_scan.txt",
    [int]$Timeout = 1000,   # Ping timeout in milliseconds
    [int[]]$Ports = @(21, 22, 23, 25, 80, 443, 445, 3389, 5985, 8080),  # Common ports
    [switch]$PortScan,
    [switch]$Silent
)

function Write-Log {
    param([string]$Message)
    if (-not $Silent) {
        Write-Host "[*] $Message"
    }
}

Write-Log "Windows PowerShell Network Scanner"
Write-Log "Output: $OutputFile"
Write-Log "="*50

# Function to get local IP and calculate network range
function Get-LocalNetwork {
    try {
        $ipConfig = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { 
            $_.IPAddress -notlike "127.*" -and $_.PrefixLength -eq 24 
        } | Select-Object -First 1
        
        if ($ipConfig) {
            $ip = $ipConfig.IPAddress
            $octets = $ip.Split('.')
            $networkBase = "$($octets[0]).$($octets[1]).$($octets[2])"
            Write-Log "Detected local network: $networkBase.0/24"
            return $networkBase
        }
    }
    catch {
        # Fallback method
        $ip = (Test-Connection -ComputerName $env:COMPUTERNAME -Count 1).IPV4Address.IPAddressToString
        $octets = $ip.Split('.')
        return "$($octets[0]).$($octets[1]).$($octets[2])"
    }
    
    return "192.168.1"
}

# Function to ping a host
function Test-HostAlive {
    param(
        [string]$IPAddress,
        [int]$TimeoutMs = 1000
    )
    
    $ping = New-Object System.Net.NetworkInformation.Ping
    try {
        $result = $ping.Send($IPAddress, $TimeoutMs)
        return $result.Status -eq 'Success'
    }
    catch {
        return $false
    }
}

# Function to scan a port
function Test-Port {
    param(
        [string]$IPAddress,
        [int]$Port,
        [int]$TimeoutMs = 1000
    )
    
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    try {
        $asyncResult = $tcpClient.BeginConnect($IPAddress, $Port, $null, $null)
        $wait = $asyncResult.AsyncWaitHandle.WaitOne($TimeoutMs, $false)
        
        if ($wait) {
            try {
                $tcpClient.EndConnect($asyncResult)
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

# Function to get hostname
function Get-HostnameFromIP {
    param([string]$IPAddress)
    
    try {
        $hostname = [System.Net.Dns]::GetHostEntry($IPAddress).HostName
        return $hostname
    }
    catch {
        return "N/A"
    }
}

# Function to get MAC address
function Get-MACAddress {
    param([string]$IPAddress)
    
    try {
        $arp = arp -a $IPAddress
        $mac = ($arp | Select-String "([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})").Matches.Value
        return $mac
    }
    catch {
        return "N/A"
    }
}

# Determine network to scan
if ($Network -eq "") {
    $networkBase = Get-LocalNetwork
}
else {
    # Parse CIDR notation if provided
    if ($Network -match "(.+)/\d+") {
        $networkBase = $Matches[1] -replace "\.\d+$", ""
    }
    else {
        $networkBase = $Network -replace "\.\d+$", ""
    }
}

Write-Log "Scanning network: $networkBase.0/24"
Write-Log "Timeout: $Timeout ms"

# Initialize results
$results = @()
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Header for output file
$header = @"
Network Scan Report
Generated: $timestamp
Computer: $env:COMPUTERNAME
User: $env:USERNAME
Network: $networkBase.0/24
Port Scan: $(if ($PortScan) { "Enabled" } else { "Disabled" })
Ports Scanned: $($Ports -join ', ')
$("="*70)

"@

Set-Content -Path $OutputFile -Value $header

# Scan all IPs in range
Write-Log "Scanning hosts (this may take a while)..."

$aliveHosts = @()

1..254 | ForEach-Object -Parallel {
    $ip = "$using:networkBase.$_"
    $timeout = $using:Timeout
    
    $ping = New-Object System.Net.NetworkInformation.Ping
    try {
        $result = $ping.Send($ip, $timeout)
        if ($result.Status -eq 'Success') {
            [PSCustomObject]@{
                IP = $ip
                ResponseTime = $result.RoundtripTime
            }
        }
    }
    catch { }
} -ThrottleLimit 50 | ForEach-Object {
    $aliveHosts += $_
    Write-Log "Host found: $($_.IP) ($($_.ResponseTime)ms)"
}

Write-Log "Found $($aliveHosts.Count) alive hosts"

# Get details for each alive host
foreach ($aliveHost in $aliveHosts) {
    $ip = $aliveHost.IP
    Write-Log "Gathering info for $ip..."
    
    $hostname = Get-HostnameFromIP -IPAddress $ip
    $mac = Get-MACAddress -IPAddress $ip
    
    $hostInfo = [PSCustomObject]@{
        IP = $ip
        Hostname = $hostname
        MAC = $mac
        ResponseTime = $aliveHost.ResponseTime
        OpenPorts = @()
    }
    
    # Port scan if enabled
    if ($PortScan) {
        Write-Log "  Scanning ports on $ip..."
        foreach ($port in $Ports) {
            if (Test-Port -IPAddress $ip -Port $port -TimeoutMs $Timeout) {
                $hostInfo.OpenPorts += $port
                Write-Log "    Port $port OPEN"
            }
        }
    }
    
    $results += $hostInfo
    
    # Write to file
    $output = @"

Host: $ip
Hostname: $hostname
MAC Address: $mac
Response Time: $($aliveHost.ResponseTime) ms
"@
    
    if ($PortScan -and $hostInfo.OpenPorts.Count -gt 0) {
        $output += "`nOpen Ports: $($hostInfo.OpenPorts -join ', ')"
    }
    elseif ($PortScan) {
        $output += "`nOpen Ports: None detected"
    }
    
    Add-Content -Path $OutputFile -Value $output
}

# Summary
$summary = @"

$("="*70)
SUMMARY
$("="*70)
Total Hosts Found: $($aliveHosts.Count)
Hosts with Open Ports: $(($results | Where-Object { $_.OpenPorts.Count -gt 0 }).Count)

"@

Add-Content -Path $OutputFile -Value $summary

# Port summary
if ($PortScan) {
    $portSummary = "`nPort Summary:`n"
    foreach ($port in $Ports) {
        $count = ($results | Where-Object { $_.OpenPorts -contains $port }).Count
        if ($count -gt 0) {
            $portSummary += "  Port $port : $count host(s)`n"
        }
    }
    Add-Content -Path $OutputFile -Value $portSummary
}

Write-Log "`nScan complete!"
Write-Log "Results saved to: $OutputFile"

# Display results
if (-not $Silent) {
    Write-Host "`n[+] Scan Results:" -ForegroundColor Green
    Write-Host "  Total Hosts: $($aliveHosts.Count)" -ForegroundColor Cyan
    
    if ($PortScan) {
        $hostsWithPorts = ($results | Where-Object { $_.OpenPorts.Count -gt 0 }).Count
        Write-Host "  Hosts with Open Ports: $hostsWithPorts" -ForegroundColor Cyan
    }
    
    Write-Host "`n  Discovered Hosts:" -ForegroundColor Yellow
    foreach ($result in $results) {
        Write-Host "    $($result.IP) - $($result.Hostname)" -ForegroundColor White
        if ($PortScan -and $result.OpenPorts.Count -gt 0) {
            Write-Host "      Open Ports: $($result.OpenPorts -join ', ')" -ForegroundColor Green
        }
    }
}
