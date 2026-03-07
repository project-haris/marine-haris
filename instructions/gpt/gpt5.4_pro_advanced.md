With the hardware you already have, I would build this as a **passive vessel-data collector** where the **Raspberry Pi is the onboard VPN endpoint** and the **Archer NX200 is only the cellular uplink**. That is the cleanest fit for your gear because TP-Link currently says the Archer NX200 supports **VPN server, not VPN client**, and TP-Link’s own VPN troubleshooting notes that WAN/CGNAT conditions can break externally reachable VPN setups. Your PiCAN‑M is designed for **NMEA 2000 over Micro‑C** and **NMEA 0183 over RS422**, exposing them to Linux as **`can0`** and **`ttyS0`**, and Signal K is designed to act as a vessel data hub. ([TP-Link Community][1])

A good target layout is:

```text
[Vessel NMEA 2000 backbone] ----\
                                 \
[Vessel NMEA 0183 talkers] ------>[Raspberry Pi 5 + PiCAN-M + NVMe]
                                        |  eth0
                                        |
                                 [TP-Link Archer NX200 + SIM]
                                        |
                                     Internet
                                        |
                            [Remote server with public IP]
                             [WireGuard + storage + access]
```

I would keep the CAN side **read-only/passive** at first. Linux SocketCAN supports **`listen-only`** mode, and Microchip describes listen-only as receiving messages without transmitting bits. That is the safest starting point on a live vessel. ([Kernel Documentation][2])

## 1) Recommended network design

Use three separate layers:

1. **Vessel data layer**

   * NMEA 2000 into PiCAN‑M `can0`
   * NMEA 0183 into PiCAN‑M `ttyS0`

2. **Boat uplink layer**

   * NX200 LAN: `192.168.50.0/24`
   * NX200 router IP: `192.168.50.1`
   * Pi LAN IP: `192.168.50.2` (prefer DHCP reservation on the router)

3. **Private VPN layer**

   * WireGuard subnet: `10.44.0.0/24`
   * Server: `10.44.0.1`
   * Pi: `10.44.0.2`

That gives you isolation without depending on inbound connectivity to the cellular router. The Pi initiates the encrypted tunnel outbound to the server, the router exposes no inbound services, and the boat bus itself is not bridged onto the public internet. The NX200’s current VPN limitation is the main reason I’d do it this way. ([TP-Link Community][1])

## 2) Build the remote server first

I’ll assume **Ubuntu Server** on the public-IP machine. Ubuntu documents WireGuard for peer-to-site/site-to-site use, manages `wg-quick` through systemd, and uses `ufw` as the standard firewall front-end. ([Ubuntu][3])

Install the basics:

```bash
sudo apt update
sudo apt install -y wireguard ufw rsync openssh-server
```

Generate server keys:

```bash
sudo umask 077
sudo sh -c 'wg genkey | tee /etc/wireguard/server.key | wg pubkey > /etc/wireguard/server.pub'
sudo cat /etc/wireguard/server.pub
```

WireGuard’s own quick start uses `wg genkey` and `wg pubkey` for key generation. ([wireguard.com][4])

Create `/etc/wireguard/wg0.conf`:

```ini
[Interface]
Address = 10.44.0.1/24
ListenPort = 51820
PrivateKey = <SERVER_PRIVATE_KEY>

[Peer]
# Vessel Raspberry Pi
PublicKey = <PI_PUBLIC_KEY>
AllowedIPs = 10.44.0.2/32
```

Bring it up and open the firewall:

```bash
sudo systemctl enable --now wg-quick@wg0

sudo ufw allow OpenSSH
sudo ufw allow 51820/udp
sudo ufw enable
```

On Ubuntu, `wg-quick` is controlled with the `wg-quick@...` systemd service. ([Ubuntu Documentation][5])

Create a storage location for incoming logs:

```bash
sudo adduser --disabled-password --gecos "" ingest
sudo mkdir -p /srv/vessel-ingest/vessel-01/raw
sudo chown -R ingest:ingest /srv/vessel-ingest
```

## 3) Configure the Archer NX200

On the NX200:

* insert the SIM and verify internet access
* set the LAN to something simple like `192.168.50.1/24`
* reserve `192.168.50.2` for the Pi if the UI allows it
* connect the Pi by **Ethernet**, not Wi‑Fi
* do **not** add any port forwards for the Pi
* disable WAN-side remote admin, WPS, UPnP, and anything else you do not need

With your current hardware, the NX200 should be treated as a **transport box**, not the VPN peer. TP-Link’s own docs/community material are the reason for that choice. ([TP-Link Community][1])

## 4) Install Raspberry Pi OS on the NVMe SSD

Use **Raspberry Pi OS Lite 64-bit**. Raspberry Pi Imager can preconfigure the hostname, user, password, and SSH before first boot. Raspberry Pi 5 supports NVMe boot, and current Raspberry Pi OS uses `/boot/firmware/` for boot config. Pimoroni also notes that on an updated Pi 5 firmware/OS stack, the NVMe Base does not need extra config-file tweaks to get started. ([Raspberry Pi][6])

My install path would be:

1. flash Raspberry Pi OS Lite 64-bit
2. in Imager advanced options:

   * hostname: `vessel-edge-01`
   * enable SSH
   * create your admin user
3. boot the Pi
4. update immediately:

```bash
sudo apt update
sudo apt full-upgrade -y
sudo reboot
```

If NVMe does not boot the first time, use the official Pi path: update the system, then use `raspi-config` to set the boot order to include NVMe. Raspberry Pi’s docs show the drive as `/dev/nvme0n1` and describe using `raspi-config` for the boot order. ([Raspberry Pi][7])

For a boat install, give the Pi its **own fused 5V/5A marine DC-DC supply**. Raspberry Pi’s official guidance for Pi 5 is 5V/5A for full power headroom. The PiCAN‑M without SMPS cannot power the Pi from NMEA 2000, and the SMPS version is a 3A design, which is not what I would rely on as the main supply for a Pi 5 plus NVMe in production. ([Raspberry Pi][7])

Install base packages on the Pi:

```bash
sudo apt install -y wireguard can-utils rsync logrotate ufw
sudo timedatectl set-timezone UTC
```

## 5) Bring up WireGuard on the Pi

Generate Pi keys:

```bash
sudo umask 077
sudo sh -c 'wg genkey | tee /etc/wireguard/pi.key | wg pubkey > /etc/wireguard/pi.pub'
sudo cat /etc/wireguard/pi.pub
```

Create `/etc/wireguard/wg0.conf`:

```ini
[Interface]
Address = 10.44.0.2/24
PrivateKey = <PI_PRIVATE_KEY>

[Peer]
PublicKey = <SERVER_PUBLIC_KEY>
Endpoint = <SERVER_PUBLIC_IP_OR_DNS>:51820
AllowedIPs = 10.44.0.1/32
PersistentKeepalive = 25
```

`PersistentKeepalive = 25` is the WireGuard-recommended value for a peer behind NAT/firewall, which is exactly your Pi-behind-cellular-router situation. ([wireguard.com][4])

Start it:

```bash
sudo systemctl enable --now wg-quick@wg0
sudo wg show
ping -c 3 10.44.0.1
```

Once the tunnel works, lock the Pi down so management is only through the VPN:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow in on wg0 to any port 22 proto tcp
sudo ufw enable
```

At that point, your normal management path becomes:

```bash
ssh <pi-user>@10.44.0.2
```

## 6) Enable PiCAN‑M for NMEA 2000 and NMEA 0183

PiCAN‑M is a marine HAT with **Micro‑C NMEA 2000** and **RS422 NMEA 0183**. It appears to Linux as **`can0`** and **`ttyS0`**. SK Pang’s install notes for PiCAN boards use the MCP2515 overlay with SPI enabled; on current Bookworm, edit `/boot/firmware/config.txt` rather than older `/boot/config.txt` examples. ([Copperhill Technologies][8])

Edit `/boot/firmware/config.txt` and add:

```ini
dtparam=spi=on
dtoverlay=mcp2515-can0,oscillator=16000000,interrupt=25
```

Reboot:

```bash
sudo reboot
```

Then test the CAN side in passive mode:

```bash
sudo ip link set can0 up type can bitrate 250000 listen-only on restart-ms 100
ip -details link show can0
candump -L can0
```

NMEA 2000 is a **CAN bus at 250 kbit/s**. Linux SocketCAN exposes CAN controllers as network interfaces, and the kernel’s CAN tooling supports both `listen-only` and `restart-ms`. Signal K’s own NMEA 2000 guidance uses `candump can0` to confirm that the bus is alive. ([canboat.github.io][9])

To bring `can0` up automatically at boot, create `/etc/systemd/system/can0.service`:

```ini
[Unit]
Description=Bring up can0 in passive NMEA 2000 mode
After=multi-user.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/sbin/ip link set can0 up type can bitrate 250000 listen-only on restart-ms 100
ExecStop=/usr/sbin/ip link set can0 down

[Install]
WantedBy=multi-user.target
```

Enable it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now can0.service
```

### How to connect the PiCAN‑M to the vessel

For an existing NMEA 2000 network, connect the Pi as a **drop** using a proper **T-connector**, not inline in the backbone. Garmin’s NMEA 2000 reference says the backbone is linear, devices connect via T-connectors, and the network is terminated only at the opposite ends. Because the PiCAN‑M is only “120Ω terminator ready,” the normal installation inference is to **leave its terminator off** when joining an existing vessel backbone and use that terminator only on a separate bench network or if the HAT is actually at a backbone end. Garmin also states a drop cable is limited to **6 m**. ([Garmin][10])

That means, in practice:

* use a spare NMEA 2000 tee on the vessel backbone
* run a drop cable from that tee to the PiCAN‑M Micro‑C
* do not disturb the vessel’s existing backbone termination
* do not add power to the backbone unless you understand the existing network power design

If the vessel also has NMEA 0183 talkers, wire those into the PiCAN‑M RS422 side and use `/dev/ttyS0`. Signal K documents **4800 baud** as the standard NMEA 0183 default and **38400** for AIS and many multiplexers. ([Copperhill Technologies][8])

This guide intentionally stays **passive**. I would not inject traffic, use `cansend`, or actively query live steering/propulsion/control networks on a working vessel unless the owner and OEM documentation explicitly allow it.

## 7) Install Signal K on the Pi

Signal K is designed to collect vessel data and present it via web/API; its Raspberry Pi prerequisites call for **Node.js 20+**, and the project recommends a **Pi 4 or Pi 5**. The `signalk-server-setup` script can enable login security and start the service automatically at boot. ([demo.signalk.org][11])

Install it like this:

```bash
# install Node.js 20+ using a supported method for your current Raspberry Pi OS release
sudo apt install -y libnss-mdns avahi-utils libavahi-compat-libdnssd-dev
sudo npm install -g signalk-server
sudo signalk-server-setup
```

Then access it over the VPN at:

```text
http://10.44.0.2:3000/
```

Signal K’s own install docs reference the web UI on port 3000. Its NMEA 2000 support is via canboatjs. ([demo.signalk.org][12])

Inside Signal K, add:

* a **SocketCAN / NMEA 2000** input for `can0`
* a **serial NMEA 0183** input for `/dev/ttyS0` if you wired RS422

If native Node installation on your current image becomes annoying, Signal K also documents a Docker path, but native install is usually simpler for direct hardware access on a Pi. ([demo.signalk.io][13])

## 8) Capture raw data and push it to the remote server

To get as much value as possible, do **both** of these:

* keep a **raw CAN log** on the Pi
* run **Signal K** in parallel for normalized live data

That way you preserve everything the bus emitted, but you also get easy remote consumption. Signal K is the “live vessel data hub”; `candump` is your raw recorder. ([demo.signalk.org][11])

Create a raw logger service on the Pi.

`/etc/systemd/system/vessel-can-log.service`:

```ini
[Unit]
Description=Raw CAN capture
After=can0.service
Wants=can0.service

[Service]
Type=simple
ExecStart=/bin/bash -lc 'mkdir -p /var/log/vessel && exec /usr/bin/candump -L can0 >> /var/log/vessel/can.log'
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target
```

Enable it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now vessel-can-log.service
```

Rotate the file daily with `/etc/logrotate.d/vessel-can`:

```conf
/var/log/vessel/can.log {
  daily
  rotate 30
  compress
  missingok
  notifempty
  copytruncate
}
```

Now set up shipping to the server.

On the Pi, create an SSH key for the ingest account:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_vessel_ingest -N ""
ssh-copy-id -i ~/.ssh/id_vessel_ingest.pub ingest@10.44.0.1
```

Create `/usr/local/bin/push-vessel-logs.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
/usr/bin/rsync -az -e "ssh -i /home/<pi-user>/.ssh/id_vessel_ingest" \
  /var/log/vessel/ \
  ingest@10.44.0.1:/srv/vessel-ingest/vessel-01/raw/
```

Make it executable:

```bash
sudo chmod +x /usr/local/bin/push-vessel-logs.sh
```

Create `/etc/systemd/system/push-vessel-logs.service`:

```ini
[Unit]
Description=Push vessel logs to remote server
After=wg-quick@wg0.service
Wants=wg-quick@wg0.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/push-vessel-logs.sh
```

Create `/etc/systemd/system/push-vessel-logs.timer`:

```ini
[Unit]
Description=Run vessel log upload every 15 minutes

[Timer]
OnBootSec=5min
OnUnitActiveSec=15min
Persistent=true

[Install]
WantedBy=timers.target
```

Enable the timer:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now push-vessel-logs.timer
```

Now the Pi buffers locally on NVMe and pushes over the VPN to the public server.

## 9) What data you can realistically expect

With your current hardware, your best passive coverage is:

* **NMEA 2000 backbone traffic**
* **NMEA 0183 talkers you can wire into RS422**

If those devices publish them onto NMEA 2000, canboatjs/Signal K can commonly decode things like **rudder (127245)**, **heading (127250)**, **engine rapid/dynamic data (127488/127489)**, **speed (128259)**, **depth (128267)**, **GPS position/course (129025/129026/129029)**, and **environmental data (130311)**. On NMEA 0183, you typically see GPS, AIS, autopilot, wind, and depth sentences depending on what the boat exposes. ([GitHub][14])

What this will **not** automatically give you is every proprietary engine-room or control-network value on the vessel. Your PiCAN‑M is ideal for NMEA 2000 and NMEA 0183. If propulsion/steering/PLC data is not already bridged onto those marine data networks, the right path is usually an OEM-approved gateway or documentation, not tapping a live control CAN directly.

## 10) Boat installation checklist

Before you leave the dock, verify these in order:

* NX200 has stable internet with the SIM
* Pi gets `192.168.50.2`
* `wg show` on the Pi shows a recent handshake
* you can `ssh` from the server to `10.44.0.2`
* `candump -L can0` shows traffic when plugged into the vessel backbone
* Signal K opens at `http://10.44.0.2:3000/` across the VPN
* `/var/log/vessel/can.log` is growing
* files arrive on `/srv/vessel-ingest/vessel-01/raw/`
* reboot the Pi and confirm the tunnel, CAN interface, logging, and uploads all return automatically

The one thing I would not compromise on is this: **start passive, collect everything raw, then decode higher-level data on top**. That will give you the most useful result with the least risk to the vessel.

A good next step would be a ready-to-paste config pack with your exact server OS, domain/IP, vessel ID, and usernames filled in.

[1]: https://community.tp-link.com/en/smart-home/forum/topic/842728 "https://community.tp-link.com/en/smart-home/forum/topic/842728"
[2]: https://docs.kernel.org/networking/can.html "https://docs.kernel.org/networking/can.html"
[3]: https://ubuntu.com/server/docs/how-to/wireguard-vpn/on-an-internal-system/ "https://ubuntu.com/server/docs/how-to/wireguard-vpn/on-an-internal-system/"
[4]: https://www.wireguard.com/quickstart/ "https://www.wireguard.com/quickstart/"
[5]: https://documentation.ubuntu.com/server/how-to/wireguard-vpn/common-tasks/ "https://documentation.ubuntu.com/server/how-to/wireguard-vpn/common-tasks/"
[6]: https://www.raspberrypi.com/documentation/configuration/ssh/ "https://www.raspberrypi.com/documentation/configuration/ssh/"
[7]: https://www.raspberrypi.com/documentation/hardware/raspberrypi/bootmodes/nvme.md "https://www.raspberrypi.com/documentation/hardware/raspberrypi/bootmodes/nvme.md"
[8]: https://copperhilltech.com/pican-m-nmea-0183-nmea-2000-hat-for-raspberry-pi/ "https://copperhilltech.com/pican-m-nmea-0183-nmea-2000-hat-for-raspberry-pi/"
[9]: https://canboat.github.io/canboat/canboat.html "https://canboat.github.io/canboat/canboat.html"
[10]: https://www8.garmin.com/manuals/webhelp/GUID-1415AAD0-FE63-42A6-8F8D-DB713D616122/EN-US/GUID-BE4F5395-A9B1-4A50-A028-CC0D77AFB288.html "https://www8.garmin.com/manuals/webhelp/GUID-1415AAD0-FE63-42A6-8F8D-DB713D616122/EN-US/GUID-BE4F5395-A9B1-4A50-A028-CC0D77AFB288.html"
[11]: https://demo.signalk.org/documentation/ "https://demo.signalk.org/documentation/"
[12]: https://demo.signalk.org/documentation/Installation/Raspberry_Pi.html "https://demo.signalk.org/documentation/Installation/Raspberry_Pi.html"
[13]: https://demo.signalk.io/documentation/Installation/Docker.html "https://demo.signalk.io/documentation/Installation/Docker.html"
[14]: https://github.com/canboat/canboatjs "https://github.com/canboat/canboatjs"
