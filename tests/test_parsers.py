#!/usr/bin/env python3
#This script provides unit tests for the NMEA 0183 and NMEA 2000 parsing logic to ensure data integrity and correct interpretation of sensor data.
"""
Unit Tests for Marine_Haris Parsers
Tests the logic of NMEA0183 and NMEA2000 parsing without requiring physical hardware.
"""

import unittest
import sys
import os
from unittest.mock import MagicMock

# Add the src directory to the path so we can import the modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/data_collection')))

# Mock the 'can' library for NMEA 2000 tests if not installed
try:
    import can
except ImportError:
    sys.modules['can'] = MagicMock()

from nmea0183_parser import NMEA0183Parser, NMEAData
from nmea2000_parser import NMEA2000Parser, NMEA2000Message

class TestNMEA0183Parser(unittest.TestCase):
    
    def setUp(self):
        self.parser = NMEA0183Parser()

    def test_checksum_validation(self):
        """Test valid and invalid checksums."""
        # Valid sentence (GPRMC)
        valid_line = "$GPRMC,092751.000,A,5321.6802,N,00606.9042,W,0.02,31.66,280511,,,A*45"
        fields = self.parser._validate_sentence(valid_line)
        self.assertIsNotNone(fields, "Valid checksum failed validation")

        # Invalid sentence (Corrupted checksum)
        invalid_line = "$GPRMC,092751.000,A,5321.6802,N,00606.9042,W,0.02,31.66,280511,,,A*99"
        fields = self.parser._validate_sentence(invalid_line)
        self.assertIsNone(fields, "Invalid checksum passed validation incorrectly")

    def test_coordinate_conversion(self):
        """Test conversion of NMEA lat/lon format to decimal degrees."""
        # 5321.6802,N -> 53.361337
        lat = self.parser._parse_coordinate("5321.6802", "N")
        self.assertAlmostEqual(lat, 53.361337, places=4)

        # 00606.9042,W -> -6.115070
        lon = self.parser._parse_coordinate("00606.9042", "W")
        self.assertAlmostEqual(lon, -6.115070, places=4)

    def test_rmc_parsing(self):
        """Test full parsing of an RMC sentence."""
        line = "$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A"
        fields = self.parser._validate_sentence(line)
        data = self.parser._parse_rmc(fields)
        
        self.assertEqual(data.latitude, 48.117300)
        self.assertEqual(data.longitude, 11.516667)
        self.assertEqual(data.speed_knots, 22.4)
        self.assertEqual(data.fix_quality, 1) # Status A

class TestNMEA2000Parser(unittest.TestCase):
    
    def test_position_pgn_parsing(self):
        """Test parsing of PGN 129025 (Position)."""
        parser = NMEA2000Parser()
        
        # Simulate a CAN message for PGN 129025
        # Note: In a real scenario, we would mock can.Message
        mock_msg = MagicMock()
        mock_msg.arbitration_id = (2 << 26) | (129025 << 8) | 50 # Priority 2, PGN 129025, Source 50
        mock_msg.data = b'\x00\x00\x00\x00\x00\x00\x00\x00' # Dummy data
        mock_msg.timestamp = 0

        # The parser logic should extract the PGN
        parsed = parser.parse_message(mock_msg)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.pgn, 129025)

if __name__ == '__main__':
    unittest.main()