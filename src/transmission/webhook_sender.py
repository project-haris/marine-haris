#This module handles real-time, event-driven transmission of critical data (like alerts or high-frequency state updates) via HTTP POST over the VPN.
#!/usr/bin/env python3
"""
Webhook Sender for Project Haris

Sends real-time JSON payloads to the M-SOC via HTTP POST.
Used for alerts, status updates, or small data packets that shouldn't wait for batch sync.
"""

import requests
import logging
import time
from typing import Dict, Optional, Any
import json

logger = logging.getLogger(__name__)

class WebhookSender:
    def __init__(self, endpoint_url: str, auth_token: Optional[str] = None, timeout: int = 10):
        """
        Initialize Webhook Sender.
        
        Args:
            endpoint_url (str): The M-SOC API endpoint (e.g., https://M-SOC.internal/api/ingest).
            auth_token (str): Optional Bearer token for authentication.
            timeout (int): Request timeout in seconds.
        """
        self.endpoint_url = endpoint_url
        self.timeout = timeout
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Marine-Haris/1.0'
        }
        if auth_token:
            self.headers['Authorization'] = f'Bearer {auth_token}'

    def send(self, payload: Dict[str, Any], retry_count: int = 3) -> bool:
        """
        Sends a JSON payload to the endpoint with retry logic.
        
        Args:
            payload (Dict): The data to send.
            retry_count (int): Number of retries on failure.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        attempt = 0
        while attempt < retry_count:
            try:
                response = requests.post(
                    self.endpoint_url,
                    data=json.dumps(payload),
                    headers=self.headers,
                    timeout=self.timeout
                )
                
                if response.status_code in [200, 201, 202]:
                    logger.debug(f"Webhook success: {response.status_code}")
                    return True
                else:
                    logger.warning(f"Webhook failed: HTTP {response.status_code} - {response.text}")
                    # Don't retry client errors (4xx)
                    if 400 <= response.status_code < 500:
                        return False
                        
            except requests.exceptions.Timeout:
                logger.warning("Webhook timeout.")
            except requests.exceptions.ConnectionError:
                logger.warning("Webhook connection error (VPN down?).")
            except Exception as e:
                logger.error(f"Unexpected webhook error: {e}")
            
            attempt += 1
            if attempt < retry_count:
                sleep_time = 2 ** attempt # Exponential backoff
                logger.info(f"Retrying webhook in {sleep_time}s...")
                time.sleep(sleep_time)
        
        return False

# --- Usage Example ---
if __name__ == "__main__":
    # Inside the VPN, this would be the internal IP or domain of the M-SOC
    sender = WebhookSender(
        endpoint_url="http://10.0.0.1:8080/api/v1/events",
        auth_token="super_secret_token"
    )
    
    alert_data = {
        "vessel_id": "HARIS-001",
        "event": "GEOFENCE_BREACH",
        "coordinates": {"lat": 25.123, "lon": -80.456}
    }
    
    success = sender.send(alert_data)
    print(f"Alert sent: {success}")