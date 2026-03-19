#!/usr/bin/env python3
"""
NMEA 2000 Parser for Project Haris
Parses CAN bus data from PiCAN-M HAT
"""

import can
import time
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class NMEA2000Message:
    """NMEA 2000 message structure"""
    timestamp: float
    pgn: int
    priority: int
    source: int
    destination: int
    data: bytes
    parsed_data: Dict

class NMEA2000Parser:
    def __init__(self, interface: str = 'can0', bitrate: int = 250000):
        """Initialize NMEA 2000 parser
        
        Args:
            interface: CAN interface (default: can0)
            bitrate: CAN bus speed (default: 250000)
        """
        self.interface = interface
        self.bitrate = bitrate
        self.bus = None
        self.pgn_handlers = {
            127251: self._parse_rate_of_turn,
            127258: self._parse_variation,
            128259: self._parse_speed,
            128267: self._parse_water_depth,
            129025: self._parse_position,
            129026: self._parse_cog_sog,
            129029: self._parse_gps_data,
            130306: self._parse_wind_data,
            130311: self._parse_environmental,
        }
        
    def connect(self) -> bool:
        """Connect to CAN interface
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Bring up CAN interface
            import subprocess
            subprocess.run(['sudo', 'ip', 'link', 'set', self.interface, 'up', 
                          'type', 'can', 'bitrate', str(self.bitrate)], check=True)
            
            # Initialize CAN bus
            self.bus = can.interface.Bus(channel=self.interface, bustype='socketcan')
            logger.info(f"Connected to {self.interface} at {self.bitrate} bps")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to CAN interface: {e}")
            return False
    
    def _parse_rate_of_turn(self, data: bytes) -> Dict:
        """Parse Rate of Turn (PGN 127251)"""
        # Implementation for rate of turn parsing
        return {
            'type': 'rate_of_turn',
            'value': int.from_bytes(data[1:3], byteorder='little', signed=True) / 32,
            'unit': 'deg/sec'
        }
    
    def _parse_position(self, data: bytes) -> Dict:
        """Parse Position, Rapid Update (PGN 129025)"""
        # Implementation for position parsing
        return {
            'type': 'position',
            'latitude': int.from_bytes(data[1:5], byteorder='little', signed=True) * 1e-7,
            'longitude': int.from_bytes(data[5:9], byteorder='little', signed=True) * 1e-7,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _parse_cog_sog(self, data: bytes) -> Dict:
        """Parse Course Over Ground & Speed Over Ground (PGN 129026)"""
        # Implementation for COG/SOG parsing
        return {
            'type': 'cog_sog',
            'cog': int.from_bytes(data[1:3], byteorder='little') * 0.0001,
            'sog': int.from_bytes(data[3:5], byteorder='little') * 0.01,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def parse_message(self, msg: can.Message) -> Optional[NMEA2000Message]:
        """Parse a CAN message into NMEA 2000 format
        
        Args:
            msg: CAN message to parse
            
        Returns:
            NMEA2000Message if successful, None otherwise
        """
        try:
            # Extract NMEA 2000 fields
            priority = msg.arbitration_id >> 26
            pgn = (msg.arbitration_id >> 8) & 0x3FFFF
            source = msg.arbitration_id & 0xFF
            destination = (msg.arbitration_id >> 8) & 0xFF
            
            # Create message object
            nmea_msg = NMEA2000Message(
                timestamp=msg.timestamp,
                pgn=pgn,
                priority=priority,
                source=source,
                destination=destination,
                data=msg.data,
                parsed_data={}
            )
            
            # Parse with specific handler
            if pgn in self.pgn_handlers:
                nmea_msg.parsed_data = self.pgn_handlers[pgn](msg.data)
            
            return nmea_msg
            
        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            return None
    
    def start_collection(self, callback=None, duration: Optional[float] = None):
        """Start collecting NMEA 2000 data
        
        Args:
            callback: Function to call with parsed messages
            duration: Duration in seconds (None for continuous)
        """
        if not self.connect():
            return
        
        logger.info("Starting NMEA 2000 data collection")
        start_time = time.time()
        
        try:
            while True:
                # Check duration
                if duration and (time.time() - start_time) >= duration:
                    break
                
                # Receive message
                msg = self.bus.recv(timeout=1.0)
                if msg:
                    parsed = self.parse_message(msg)
                    if parsed and callback:
                        callback(parsed)
                        
        except KeyboardInterrupt:
            logger.info("Stopping collection by user")
        except Exception as e:
            logger.error(f"Collection error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop collection and cleanup"""
        if self.bus:
            self.bus.shutdown()
            logger.info("NMEA 2000 collection stopped")

# Example usage
if __name__ == "__main__":
    def process_message(msg: NMEA2000Message):
        print(f"PGN: {msg.pgn} | Source: {msg.source}")
        if msg.parsed_data:
            print(f"Data: {json.dumps(msg.parsed_data, indent=2)}")
    
    parser = NMEA2000Parser()
    parser.start_collection(callback=process_message)
