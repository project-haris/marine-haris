#This module serves as the bridge between your custom NMEA parsers and the Signal K ecosystem. It converts the standardized NMEAData objects into Signal K JSON deltas and transmits them to the Signal K server running on the vessel.
#It also includes a listener component, allowing Marine_Haris to consume aggregated data back from Signal K if needed (useful for accessing data from other sources like weather or AIS).

#!/usr/bin/env python3
"""
Signal K Ingestor for Marine_Haris

This script acts as a bridge between the custom NMEA parsers and the Signal K server.
1.  **Producer Mode**: Converts NMEAData objects into Signal K Delta format and pushes them to the server.
2.  **Consumer Mode**: (Optional) Subscribes to the Signal K stream for normalized data logging.
"""

import json
import logging
import asyncio
import websockets
import requests
from typing import Optional, Dict, List
from dataclasses import asdict

# Import the data structure from the NMEA parser
# Ensure nmea0183_parser.py is in the same directory
try:
    from nmea0183_parser import NMEAData
except ImportError:
    # Fallback for standalone testing/usage
    from dataclasses import dataclass, field
    from datetime import datetime
    @dataclass
    class NMEAData:
        timestamp: datetime = field(default_factory=datetime.utcnow)
        latitude: Optional[float] = None
        longitude: Optional[float] = None
        speed_knots: Optional[float] = None
        course_over_ground: Optional[float] = None
        heading: Optional[float] = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SignalKPaths:
    """Standard Signal K path definitions"""
    NAVIGATION_POSITION = "navigation.position"
    NAVIGATION_SPEED = "navigation.speedOverGround"
    NAVIGATION_COURSE = "navigation.courseOverGroundTrue"
    NAVIGATION_HEADING = "navigation.headingTrue"
    ENVIRONMENT_DEPTH = "environment.depth.belowTransducer"
    ENVIRONMENT_WATER_TEMP = "environment.water.temperature"

class SignalKMapper:
    """Maps internal NMEAData objects to Signal K Delta format"""
    
    @staticmethod
    def map_to_delta(data: NMEAData, context: str = "vessels.self") -> Dict:
        """
        Converts a NMEAData object into a Signal K delta dictionary.
        
        Args:
            data (NMEAData): The parsed data object.
            context (str): The Signal K context (usually 'vessels.self').
        
        Returns:
            Dict: A valid Signal K delta JSON object.
        """
        updates = []
        
        # Helper to create a single update value
        def make_value(path, value):
            if value is not None:
                return {"path": path, "value": value}
            return None

        # Map Position
        if data.latitude is not None and data.longitude is not None:
            updates.append({
                "path": SignalKPaths.NAVIGATION_POSITION,
                "value": {
                    "latitude": data.latitude,
                    "longitude": data.longitude
                }
            })

        # Map Speed (convert knots to m/s for Signal K standard)
        if data.speed_knots is not None:
            updates.append({
                "path": SignalKPaths.NAVIGATION_SPEED,
                "value": data.speed_knots * 0.514444 
            })

        # Map Course (Radians)
        if data.course_over_ground is not None:
            updates.append({
                "path": SignalKPaths.NAVIGATION_COURSE,
                "value": round(data.course_over_ground * (3.14159 / 180), 6)
            })
            
        # Map Heading (Radians)
        if data.heading is not None:
            updates.append({
                "path": SignalKPaths.NAVIGATION_HEADING,
                "value": round(data.heading * (3.14159 / 180), 6)
            })
            
        # Map Depth (Meters)
        if data.depth_meters is not None:
            updates.append({
                "path": SignalKPaths.ENVIRONMENT_DEPTH,
                "value": data.depth_meters
            })

        if not updates:
            return {}

        return {
            "context": context,
            "updates": [{
                "source": {
                    "label": "Marine_Haris",
                    "type": "NMEA0183"
                },
                "timestamp": data.timestamp.isoformat() + "Z",
                "values": updates
            }]
        }

class SignalKIngestor:
    def __init__(self, host: str = "localhost", port: int = 3000, use_http: bool = False):
        """
        Initialize the Signal K Ingestor.
        
        Args:
            host (str): Signal K server IP.
            port (int): Signal K server port.
            use_http (bool): If True, uses HTTP POST. If False, uses WebSocket.
        """
        self.host = host
        self.port = port
        self.use_http = use_http
        self.ws_url = f"ws://{host}:{port}/signalk/v1/stream"
        self.http_url = f"http://{host}:{port}/signalk/v1/api/vessels/self"
        
        self.ws = None
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    async def _connect_ws(self):
        """Establish WebSocket connection."""
        try:
            self.ws = await websockets.connect(self.ws_url)
            logger.info(f"WebSocket connected to {self.ws_url}")
        except Exception as e:
            logger.error(f"Failed to connect WebSocket: {e}")

    async def _send_ws(self, delta: Dict):
        """Send delta via WebSocket."""
        if not self.ws:
            await self._connect_ws()
        
        if self.ws:
            try:
                await self.ws.send(json.dumps(delta))
            except Exception as e:
                logger.error(f"WebSocket send error: {e}")
                self.ws = None # Force reconnect on next attempt

    def _send_http(self, delta: Dict):
        """Send delta via HTTP POST."""
        try:
            # HTTP update is slightly different structure for some SK implementations
            # Usually requires updating specific paths
            # This is a simplified implementation for demonstration
            resp = requests.post(self.http_url, json=delta, timeout=2)
            if resp.status_code != 200:
                logger.warning(f"HTTP POST failed: {resp.status_code}")
        except requests.RequestException as e:
            logger.error(f"HTTP connection error: {e}")

    def update(self, data: NMEAData):
        """
        Public method to ingest data into Signal K.
        Handles the conversion and transmission logic.
        
        Args:
            data (NMEAData): The parsed data to send.
        """
        delta = SignalKMapper.map_to_delta(data)
        if not delta:
            return

        if self.use_http:
            self._send_http(delta)
        else:
            # Run async send in the event loop
            self.loop.run_until_complete(self._send_ws(delta))

    async def listen(self, callback):
        """
        (Consumer Mode)
        Connects to Signal K stream and passes received messages to a callback.
        
        Args:
            callback (function): Function to handle received JSON data.
        """
        logger.info("Starting Signal K Consumer...")
        await self._connect_ws()
        
        while True:
            try:
                if self.ws:
                    message = await self.ws.recv()
                    data = json.loads(message)
                    callback(data)
                else:
                    await asyncio.sleep(5)
                    await self._connect_ws()
            except websockets.exceptions.ConnectionClosed:
                logger.warning("WebSocket connection closed. Reconnecting...")
                self.ws = None
                await asyncio.sleep(5)
                await self._connect_ws()
            except Exception as e:
                logger.error(f"Error in listener loop: {e}")
                await asyncio.sleep(5)

# --- Main Execution Block (Example Usage) ---
if __name__ == "__main__":
    # Example of how to use this ingestor with the NMEA parser
    
    # 1. Setup the Ingestor (Use HTTP for simple fire-and-forget in this example)
    ingestor = SignalKIngestor(use_http=False) # Use WebSocket for bidirectional
    
    # 2. Simulate receiving data from NMEA parser
    test_data = NMEAData(
        latitude=25.1234,
        longitude=-80.5678,
        speed_knots=12.5,
        heading=180.0
    )
    
    logger.info("Sending test data to Signal K...")
    
    # 3. Send the data
    ingestor.update(test_data)
    
    logger.info("Data sent. Check Signal K dashboard for updates.")

### **Integration Guide**

# To integrate this into your main `harisd` service:

# 1.  **Configuration**: In your `harisd` service, import both `NMEA0183Parser` and `SignalKIngestor`.
# 2.  **Data Flow Loop**:
#     ```python
#     # Pseudo-code for harisd
    
#     parser = NMEA0183Parser(port='/dev/ttyS0')
#     ingestor = SignalKIngestor(host='localhost', port=3000)
    
#     while True:
#         # 1. Read raw NMEA data
#         data = parser.read_sentence()
        
#         if data:
#             # 2. Push to Signal K for normalization and local display
#             ingestor.update(data)
            
#             # 3. Save to local Security Database (NVMe)
#             db.save(data)
#     ```
# 3.  **Dependencies**: Ensure the `websockets` library is installed in your environment:
#     ```bash
#     pip3 install websockets requests
#     ```