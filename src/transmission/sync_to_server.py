#This module handles the bulk synchronization of historical data logs. It uses rsync over SSH for efficient, delta-based transfers, which is critical for intermittent marine connectivity.
#!/usr/bin/env python3
"""
Sync to Server for Project Haris

Handles batch synchronization of data logs to the remote M-SOC server.
Uses rsync over SSH for efficient, resumable transfers inside the VPN tunnel.
"""

import subprocess
import logging
import os
from typing import List, Optional

logger = logging.getLogger(__name__)

class SyncManager:
    def __init__(self, 
                 remote_user: str, 
                 remote_host: str, 
                 remote_path: str, 
                 ssh_key_path: str = '/home/haris/.ssh/id_rsa'):
        """
        Initialize Sync Manager.
        
        Args:
            remote_user (str): SSH username on the M-SOC server.
            remote_host (str): M-SOC server IP (VPN IP, e.g., 10.0.0.1).
            remote_path (str): Destination directory on the server.
            ssh_key_path (str): Path to the SSH private key for passwordless login.
        """
        self.remote_user = remote_user
        self.remote_host = remote_host
        self.remote_path = remote_path
        self.ssh_key_path = ssh_key_path

    def sync_directory(self, local_path: str, delete_after_sync: bool = False) -> bool:
        """
        Syncs a local directory to the remote server using rsync.
        
        Args:
            local_path (str): Path to local data directory.
            delete_after_sync (bool): If True, deletes local files after successful sync.
            
        Returns:
            bool: True if sync successful, False otherwise.
        """
        if not os.path.exists(local_path):
            logger.error(f"Local path does not exist: {local_path}")
            return False

        # Construct rsync command
        # -a: archive mode (preserves permissions, times, etc.)
        # -v: verbose
        # -z: compress during transfer
        # --remove-source-files: delete local files on success (safer than rm -rf)
        
        cmd = [
            'rsync',
            '-avz',
            f'-e', f'ssh -i {self.ssh_key_path} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null',
            '--remove-source-files' if delete_after_sync else '',
            f'{local_path}/',
            f'{self.remote_user}@{self.remote_host}:{self.remote_path}/'
        ]
        
        # Filter empty args
        cmd = [x for x in cmd if x]

        logger.info(f"Starting sync: {local_path} -> {self.remote_host}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("Sync completed successfully.")
                logger.debug(f"Rsync output:\n{result.stdout}")
                return True
            else:
                logger.error(f"Sync failed with code {result.returncode}")
                logger.error(f"Rsync error:\n{result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Sync timed out after 300 seconds.")
            return False
        except FileNotFoundError:
            logger.error("rsync command not found. Please install rsync.")
            return False
        except Exception as e:
            logger.error(f"Unexpected sync error: {e}")
            return False

    def check_connectivity(self) -> bool:
        """Checks if the remote server is reachable via SSH."""
        cmd = [
            'ssh', 
            '-i', self.ssh_key_path,
            '-o', 'BatchMode=yes',
            '-o', 'ConnectTimeout=5',
            f'{self.remote_user}@{self.remote_host}',
            'echo ok'
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=10)
            return result.returncode == 0
        except:
            return False

# --- Usage Example ---
if __name__ == "__main__":
    # Configure based on your VPN settings
    syncer = SyncManager(
        remote_user="M-SOC_admin",
        remote_host="10.0.0.1", # VPN IP of the server
        remote_path="/data/vessel_logs"
    )
    
    if syncer.check_connectivity():
        # Sync local buffer and delete files on success
        success = syncer.sync_directory("/var/log/haris/buffer", delete_after_sync=True)
        print(f"Sync Success: {success}")
    else:
        print("Server unreachable via VPN.")