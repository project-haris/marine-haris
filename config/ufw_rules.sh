#!/bin/bash
# UFW Firewall Setup for Marine_Haris
# Policy: Deny All Incoming, Allow Outgoing, Allow VPN Only
# This script automates the setup of the Uncomplicated Firewall (UFW). It implements the Fail-Closed security policy: denying all incoming traffic by default and only allowing connections from the trusted VPN subnet.

# Reset UFW to defaults (Careful in production)
echo "Resetting UFW rules..."
sudo ufw --force reset

# Set Default Policies
echo "Setting default policies..."
sudo ufw default deny incoming
sudo ufw default allow outgoing

# -------------------
# Trusted VPN Subnet
# -------------------
# Adjust this to match your WireGuard subnet (e.g., 10.0.0.0/24)
VPN_SUBNET="10.0.0.0/24"

# Allow SSH access ONLY from VPN
# This prevents direct access from the vessel's local network
echo "Allowing SSH from VPN subnet..."
sudo ufw allow from $VPN_SUBNET to any port 22 proto tcp comment 'SSH via VPN'

# Allow Signal K access ONLY from VPN
echo "Allowing Signal K from VPN subnet..."
sudo ufw allow from $VPN_SUBNET to any port 3000 proto tcp comment 'Signal K via VPN'

# Allow WireGuard Traffic (UDP 51820)
# Essential for the VPN tunnel to establish connection
echo "Allowing WireGuard traffic..."
sudo ufw allow 51820/udp comment 'WireGuard'

# -------------------
# Local/Management
# -------------------
# Allow all traffic on the loopback interface
sudo ufw allow in on lo

# Enable Logging
sudo ufw logging on

# Enable the Firewall
echo "Enabling UFW..."
sudo ufw --force enable

echo "Firewall Configuration Complete."
sudo ufw status verbose