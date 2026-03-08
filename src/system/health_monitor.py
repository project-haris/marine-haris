#This script acts as the "vital signs" monitor for the device. It checks system resources (CPU temperature, storage), service availability, and VPN connectivity. If critical thresholds are exceeded, it logs alerts for transmission to the MSOC.

#!/usr/bin/env python3
"""
Health Monitor for Marine_Haris

Monitors system vitals (CPU temp, Disk space) and service status.
Acts as a local watchdog to ensure system integrity.
"""

import psutil
import logging
import time
import subprocess
import os
from datetime import datetime
from typing import Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HealthMonitor:
    def __init__(self, 
                 temp_threshold_c: float = 75.0, 
                 disk_threshold_percent: float = 90.0,
                 vpn_interface: str = "wg0"):
        """
        Initialize Health Monitor.
        
        Args:
            temp_threshold_c (float): Max allowed CPU temp before alert.
            disk_threshold_percent (float): Max disk usage % before alert.
            vpn_interface (str): The name of the WireGuard interface to check.
        """
        self.temp_threshold = temp_threshold_c
        self.disk_threshold = disk_threshold_percent
        self.vpn_interface = vpn_interface

    def get_cpu_temp(self) -> Optional[float]:
        """
        Reads the Raspberry Pi CPU temperature.
        Returns None if sensor not found (e.g., running on non-Pi hardware for testing).
        """
        try:
            # Standard path for Raspberry Pi 5 thermal sensor
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp_str = f.read().strip()
                # Convert millidegrees to degrees
                return float(temp_str) / 1000.0
        except FileNotFoundError:
            logger.warning("Thermal zone not found (are you on a Pi?)")
            return None
        except Exception as e:
            logger.error(f"Error reading temp: {e}")
            return None

    def get_disk_usage(self, path: str = "/") -> float:
        """Returns disk usage percentage for the given path."""
        try:
            disk = psutil.disk_usage(path)
            return disk.percent
        except Exception as e:
            logger.error(f"Error reading disk usage: {e}")
            return 0.0

    def check_vpn(self) -> bool:
        """
        Checks if the WireGuard VPN interface is up and has an IP address.
        """
        try:
            # Check if interface exists
            result = subprocess.run(
                ["ip", "link", "show", self.vpn_interface], 
                capture_output=True, text=True
            )
            if result.returncode != 0:
                return False
            
            # Check if it has an IP assigned
            result = subprocess.run(
                ["ip", "addr", "show", self.vpn_interface"], 
                capture_output=True, text=True
            )
            return "inet " in result.stdout
        except Exception as e:
            logger.error(f"VPN check failed: {e}")
            return False

    def check_service(self, service_name: str) -> bool:
        """
        Checks if a systemd service is currently active (running).
        """
        try:
            result = subprocess.run(
                ["systemctl", "is-active", service_name],
                capture_output=True, text=True
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Service check failed for {service_name}: {e}")
            return False

    def run_diagnostics(self) -> Dict:
        """
        Runs all health checks and returns a status report.
        """
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "alerts": [],
            "metrics": {}
        }

        # 1. CPU Temperature
        cpu_temp = self.get_cpu_temp()
        if cpu_temp is not None:
            report["metrics"]["cpu_temp_c"] = cpu_temp
            if cpu_temp > self.temp_threshold:
                msg = f"CPU Overheat Alert: {cpu_temp}°C > {self.temp_threshold}°C"
                report["alerts"].append(msg)
                logger.warning(msg)

        # 2. Disk Usage
        disk_usage = self.get_disk_usage()
        report["metrics"]["disk_usage_percent"] = disk_usage
        if disk_usage > self.disk_threshold:
            msg = f"Disk Space Alert: {disk_usage}% > {self.disk_threshold}%"
            report["alerts"].append(msg)
            logger.warning(msg)

        # 3. VPN Status
        vpn_ok = self.check_vpn()
        report["metrics"]["vpn_connected"] = vpn_ok
        if not vpn_ok:
            report["alerts"].append("VPN Tunnel Down")

        # 4. Critical Services
        services = ["harisd", "signalk"] # Add others if needed
        report["metrics"]["services"] = {}
        for svc in services:
            is_active = self.check_service(svc)
            report["metrics"]["services"][svc] = is_active
            if not is_active:
                report["alerts"].append(f"Service Down: {svc}")

        return report

def main():
    """Main loop for the monitoring daemon."""
    monitor = HealthMonitor()
    
    logger.info("Starting Health Monitor Daemon...")
    
    while True:
        report = monitor.run_diagnostics()
        
        # If there are alerts, we could trigger the webhook sender here
        if report["alerts"]:
            logger.warning(f"System Alerts Detected: {report['alerts']}")
            # TODO: Import WebhookSender and send alert to MSOC if VPN is up
        
        # Log healthy status periodically (every 5 mins)
        logger.info(f"Health Check: Temp {report['metrics'].get('cpu_temp_c')}°C | Disk {report['metrics'].get('disk_usage_percent')}% | VPN {report['metrics'].get('vpn_connected')}")
        
        time.sleep(60) # Check every minute

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Health Monitor stopped.")