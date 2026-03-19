#!/bin/bash
#This shell script is a robust "watchdog" designed to be run via cron. It verifies that critical services are running and attempts to restart them if they have failed. It also handles VPN recovery logic.

# Auto-Restart / Watchdog Script for Project Haris
# 
# Description: Checks critical services and VPN status. 
#              Attempts to restart failed components.
#              Designed to be run via cron every minute.
#
# Usage: Add to crontab:
# * * * * * /opt/marine_haris/src/system/auto_restart.sh >> /var/log/haris/watchdog.log 2>&1
#

# --- Configuration ---
SERVICES=("harisd" "signalk") # List of systemd services to monitor
VPN_INTERFACE="tailscale0"
LOG_TAG="HARIS_WATCHDOG"

# --- Functions ---

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
    logger -t "$LOG_TAG" "$1"
}

check_service() {
    local service=$1
    if systemctl is-active --quiet "$service"; then
        return 0
    else
        return 1
    fi
}

restart_service() {
    local service=$1
    log "WARNING: Service $service is down. Attempting restart..."
    systemctl restart "$service"
    
    # Verify restart
    sleep 5
    if check_service "$service"; then
        log "SUCCESS: Service $service restarted successfully."
    else
        log "CRITICAL: Failed to restart $service."
    fi
}

check_vpn() {
    # Check if interface exists and has an IP
    if ip link show "$VPN_INTERFACE" &> /dev/null; then
        if ip addr show "$VPN_INTERFACE" | grep -q "inet "; then
            return 0
        fi
    fi
    return 1
}

restart_vpn() {
    log "WARNING: Tailscale VPN is down. Attempting restart..."
    
    if command -v tailscale &> /dev/null; then
        systemctl restart tailscaled
        
        sleep 5
        if check_vpn; then
            log "SUCCESS: Tailscale VPN re-established."
        else
            log "CRITICAL: Failed to re-establish Tailscale VPN."
        fi
    else
        log "INFO: Tailscale not installed. Cannot restart locally."
    fi
}

# --- Main Logic ---

# 1. Check Services
for svc in "${SERVICES[@]}"; do
    if ! check_service "$svc"; then
        restart_service "$svc"
    fi
done

# 2. Check VPN
if ! check_vpn; then
    restart_vpn
fi

exit 0