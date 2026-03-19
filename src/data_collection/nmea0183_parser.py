# This module is designed to be robust, handling the specific quirks of NMEA 0183 (like variable baud rates and checksum validation) and converting the raw string data into a standardized format suitable for your security database.
#!/usr/bin/env python3
"""
NMEA 0183 Parser for Project Haris
Reads serial data from the PiCAN-M screw terminal (ttyS0) and parses standard NMEA sentences.
"""

import serial
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, List
import math

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class NMEAData:
    """Standardized data structure for NMEA 0183 output"""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = "NMEA0183"
    
    # Position Data
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    fix_quality: Optional[int] = None # 0=Invalid, 1=GPS, 2=DGPS, etc.
    satellites: Optional[int] = None
    
    # Navigation Data
    speed_knots: Optional[float] = None
    course_over_ground: Optional[float] = None
    heading: Optional[float] = None
    
    # Environmental/Other
    water_temperature: Optional[float] = None
    depth_meters: Optional[float] = None
    
    # Raw sentence for debugging/audit
    raw_sentence: Optional[str] = None

class NMEA0183Parser:
    def __init__(self, port: str = '/dev/ttyS0', baudrate: int = 4800, timeout: float = 1.0):
        """
        Initialize the NMEA 0183 Parser.
        
        Args:
            port (str): Serial port device (default: /dev/ttyS0 for PiCAN-M)
            baudrate (int): Baud rate (default: 4800, standard NMEA 0183)
            timeout (float): Read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None
        
        # Map talker/sentence types to parsing methods
        self.parsers = {
            'RMC': self._parse_rmc, # Recommended Minimum
            'GGA': self._parse_gga, # GPS Fix Data
            'GLL': self._parse_gll, # Geographic Position
            'VTG': self._parse_vtg, # Track Made Good
            'HDT': self._parse_hdt, # Heading
            'DBT': self._parse_dbt, # Depth Below Transducer
            'MTW': self._parse_mtw, # Water Temperature
        }

    def connect(self) -> bool:
        """Establish connection to the serial port."""
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            logger.info(f"Connected to NMEA 0183 on {self.port} at {self.baudrate} baud.")
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to connect to serial port {self.port}: {e}")
            return False

    def disconnect(self):
        """Close the serial connection."""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            logger.info("NMEA 0183 connection closed.")

    def _calculate_checksum(self, sentence: str) -> str:
        """
        Calculate the NMEA checksum.
        XOR of all characters between '$' and '*'.
        """
        checksum = 0
        for char in sentence:
            checksum ^= ord(char)
        return f"{checksum:02X}"

    def _validate_sentence(self, line: str) -> Optional[List[str]]:
        """
        Validate the NMEA sentence structure and checksum.
        
        Returns:
            List of fields if valid, None otherwise.
        """
        try:
            # Basic format check
            if not line.startswith('$') or '*' not in line:
                return None
            
            # Split data and checksum
            content, checksum_provided = line.strip().split('*', 1)
            content = content[1:] # Remove '$'
            
            # Verify checksum
            calculated_checksum = self._calculate_checksum(content)
            if calculated_checksum != checksum_provided.upper():
                logger.warning(f"Checksum mismatch: Calculated {calculated_checksum}, Received {checksum_provided}")
                return None
            
            return content.split(',')
            
        except ValueError:
            logger.warning(f"Malformed NMEA sentence: {line}")
            return None

    def _parse_coordinate(self, value: str, direction: str) -> Optional[float]:
        """
        Convert NMEA coordinate format (DDMM.MMMM or DDDMM.MMMM) to Decimal Degrees.
        
        Args:
            value: The coordinate string (e.g., "4807.038")
            direction: The direction character (N, S, E, W)
        """
        if not value or not direction:
            return None
            
        try:
            # Determine if latitude (2 digits for degrees) or longitude (3 digits)
            if direction in ['N', 'S']:
                degrees = float(value[:2])
                minutes = float(value[2:])
            else: # E, W
                degrees = float(value[:3])
                minutes = float(value[3:])
            
            decimal_degrees = degrees + (minutes / 60.0)
            
            # Apply direction
            if direction in ['S', 'W']:
                decimal_degrees *= -1
                
            return round(decimal_degrees, 6)
            
        except ValueError:
            return None

    # --- Sentence Parsers ---

    def _parse_rmc(self, fields: List[str]) -> NMEAData:
        """
        Parse RMC (Recommended Minimum) sentence.
        Format: $--RMC,Time,Status,Lat,N,Lon,E,Speed,Course,Date,MagVar,E*CS
        """
        data = NMEAData()
        
        try:
            # Time and Date
            time_str = fields[1]
            date_str = fields[9]
            if time_str and date_str:
                dt = datetime.strptime(f"{date_str}{time_str}", "%d%m%y%H%M%S")
                data.timestamp = dt
            
            # Status (A=Active/Valid, V=Void/Invalid)
            if fields[2] != 'A':
                data.fix_quality = 0
                return data
            
            # Position
            data.latitude = self._parse_coordinate(fields[3], fields[4])
            data.longitude = self._parse_coordinate(fields[5], fields[6])
            
            # Speed and Course
            data.speed_knots = float(fields[7]) if fields[7] else None
            data.course_over_ground = float(fields[8]) if fields[8] else None
            
            data.fix_quality = 1 # Valid GPS fix
            
        except (IndexError, ValueError) as e:
            logger.debug(f"Error parsing RMC sentence: {e}")
            
        return data

    def _parse_gga(self, fields: List[str]) -> NMEAData:
        """
        Parse GGA (GPS Fix Data) sentence.
        Format: $--GGA,Time,Lat,N,Lon,E,Quality,NumSats,HDOP,Alt,M,GeoidSep,M,Age,RefStation*CS
        """
        data = NMEAData()
        
        try:
            # Position
            data.latitude = self._parse_coordinate(fields[2], fields[3])
            data.longitude = self._parse_coordinate(fields[4], fields[5])
            
            # Fix Quality
            data.fix_quality = int(fields[6]) if fields[6] else 0
            
            # Satellites
            data.satellites = int(fields[7]) if fields[7] else None
            
        except (IndexError, ValueError) as e:
            logger.debug(f"Error parsing GGA sentence: {e}")
            
        return data

    def _parse_gll(self, fields: List[str]) -> NMEAData:
        """
        Parse GLL (Geographic Position) sentence.
        Format: $--GLL,Lat,N,Lon,E,Time,Status*CS
        """
        data = NMEAData()
        
        try:
            data.latitude = self._parse_coordinate(fields[1], fields[2])
            data.longitude = self._parse_coordinate(fields[3], fields[4])
            
            # Status
            data.fix_quality = 1 if fields[6] == 'A' else 0
            
        except (IndexError, ValueError) as e:
            logger.debug(f"Error parsing GLL sentence: {e}")
            
        return data

    def _parse_vtg(self, fields: List[str]) -> NMEAData:
        """
        Parse VTG (Track Made Good and Ground Speed) sentence.
        Format: $--VTG,Course,T,Course,M,Speed,N,Speed,K,Mode*CS
        """
        data = NMEAData()
        
        try:
            data.course_over_ground = float(fields[1]) if fields[1] else None
            data.speed_knots = float(fields[5]) if fields[5] else None
        except (IndexError, ValueError) as e:
            logger.debug(f"Error parsing VTG sentence: {e}")
            
        return data

    def _parse_hdt(self, fields: List[str]) -> NMEAData:
        """Parse HDT (Heading) sentence."""
        data = NMEAData()
        try:
            data.heading = float(fields[1]) if fields[1] else None
        except (IndexError, ValueError):
            pass
        return data

    def _parse_dbt(self, fields: List[str]) -> NMEAData:
        """Parse DBT (Depth Below Transducer) sentence."""
        data = NMEAData()
        try:
            # Field 3 is depth in meters
            data.depth_meters = float(fields[3]) if fields[3] else None
        except (IndexError, ValueError):
            pass
        return data

    def _parse_mtw(self, fields: List[str]) -> NMEAData:
        """Parse MTW (Water Temperature) sentence."""
        data = NMEAData()
        try:
            data.water_temperature = float(fields[1]) if fields[1] else None
        except (IndexError, ValueError):
            pass
        return data

    def read_sentence(self) -> Optional[NMEAData]:
        """
        Read a single line from the serial port and parse it.
        
        Returns:
            NMEAData object if a valid sentence is parsed, None otherwise.
        """
        if not self.serial_connection or not self.serial_connection.is_open:
            if not self.connect():
                time.sleep(5) # Wait before retrying
                return None

        try:
            line = self.serial_connection.readline().decode('ascii', errors='replace').strip()
            
            if not line:
                return None
                
            fields = self._validate_sentence(line)
            
            if not fields:
                return None
            
            # Identify sentence type (e.g., GPRMC -> RMC)
            # The first field contains the talker ID + sentence type
            sentence_type = fields[0][2:] if len(fields[0]) > 2 else fields[0]
            
            # Dispatch to specific parser
            parser_func = self.parsers.get(sentence_type)
            
            if parser_func:
                data = parser_func(fields)
                data.raw_sentence = line
                return data
            else:
                # Unhandled sentence type
                return None
                
        except serial.SerialException as e:
            logger.error(f"Serial error: {e}")
            self.disconnect()
            return None
        except Exception as e:
            logger.error(f"Unexpected error reading NMEA data: {e}")
            return None

# --- Main Execution Block (for testing) ---
if __name__ == "__main__":
    parser = NMEA0183Parser(port='/dev/ttyS0')
    
    logger.info("Starting NMEA 0183 Parser Test...")
    
    try:
        while True:
            data = parser.read_sentence()
            if data:
                # Only log meaningful data updates
                if data.latitude or data.speed_knots:
                    logger.info(f"Received: Lat {data.latitude}, Lon {data.longitude}, Speed {data.speed_knots} kts")
    except KeyboardInterrupt:
        logger.info("Stopping parser.")
    finally:
        parser.disconnect()

### Integration Notes

#1.  **Serial Port**: The script defaults to `/dev/ttyS0`, which is typically the serial port exposed by the PiCAN-M HAT on a Raspberry Pi.
#2.  **Baud Rate**: Standard NMEA 0183 operates at **4800 baud**. However, some modern sensors use **38400** or higher (NMEA 0183-HS). You should verify your vessel's sensor settings and initialize the parser with the correct rate:
#    ```python
#    # Example for high-speed serial
#    parser = NMEA0183Parser(port='/dev/ttyS0', baudrate=38400)
#    ```
#3.  **Data Consolidation**: This parser returns individual data objects per sentence. In your main application logic (e.g., inside `harisd`), you will likely want to aggregate these into a single "Vessel State" object before sending it to the M-SOC, as different sensors broadcast at different intervals (e.g., GPS might update once per second, heading 10 times per second).