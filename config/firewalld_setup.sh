#!/bin/bash
# Firewalld Setup Script for Project Haris
# Policy: Deny All Incoming, Allow Outgoing, Allow Tailscale Only
# This script automates the setup of firewalld. It implements the Fail-Closed security policy: 
# denying all incoming traffic by default and only allowing connections from the trusted Tailscale interface.

set -e

echo "--- Project Haris Firewalld Setup ---"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root."
    exit 1
fi

# Install firewalld if not present
if ! command -v firewall-cmd &> /dev/null; then
    echo "Installing firewalld..."
    apt update
    apt install -y firewalld
fi

# Stop and disable UFW if present
if command -v ufw &> /dev/null; then
    echo "Disabling UFW (firewalld will replace it)..."
    ufw --force disable || true
    systemctl stop ufw || true
    systemctl disable ufw || true
fi

# Start and enable firewalld
echo "Starting firewalld..."
systemctl enable firewalld
systemctl start firewalld

# Wait for firewalld to be ready
sleep 2

# Set default zone
echo "Configuring default zone..."
firewall-cmd --set-default-zone=drop

# Create trusted zone for Tailscale
echo "Creating Tailscale trusted zone..."
firewall-cmd --permanent --new-zone=tailscale

# Add Tailscale interface to the zone
firewall-cmd --permanent --zone=tailscale --add-interface=tailscale0

# Allow all traffic from Tailscale interface (trusted)
firewall-cmd --permanent --zone=tailscale --add-service=ssh
firewall-cmd --permanent --zone=tailscale --add-port=3000/tcp    # Signal K
firewall-cmd --permanent --zone=tailscale --add-port=5601/tcp    # Kibana
firewall-cmd --permanent --zone=tailscale --add-port=9200/tcp    # Elasticsearch

# Set target to ACCEPT for the tailscale zone (trust all from this interface)
firewall-cmd --permanent --zone=tailscale --set-target=ACCEPT

# Configure drop zone (default)
# All incoming is dropped by default, outgoing allowed
echo "Configuring drop zone..."

# Allow loopback traffic
firewall-cmd --permanent --zone=trusted --add-interface=lo

# Allow essential outbound traffic
# Allow DNS
firewall-cmd --permanent --zone=public --add-service=dns

# Allow HTTP/HTTPS for package updates (outbound only - handled by default)
# Tailscale needs specific ports for NAT traversal
firewall-cmd --permanent --zone=public --add-port=41641/udp  # Tailscale default port

# Apply changes
echo "Applying firewall rules..."
firewall-cmd --reload

# Display status
echo ""
echo "Firewall Configuration Complete."
echo ""
echo "Active zones:"
firewall-cmd --get-active-zones
echo ""
echo "Tailscale zone services:"
firewall-cmd --zone=tailscale --list-all
echo ""
echo "Default zone (drop):"
firewall-cmd --zone=drop --list-all
echo ""
echo "Firewall is now active with fail-closed policy."
echo "Only Tailscale interface traffic is trusted."
