#This module handles data compression. Given the repetitive nature of NMEA data, compression significantly reduces bandwidth usage and storage costs.
#!/usr/bin/env python3
"""
Compression Manager for Marine_Haris

Handles the compression of data logs before transmission to minimize bandwidth usage.
Uses standard GZIP compression for a balance of speed and efficiency.
"""

import gzip
import shutil
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class CompressionManager:
    def __init__(self, compression_level: int = 6):
        """
        Initialize Compression Manager.
        
        Args:
            compression_level (int): Level 0-9. 0=no compression, 9=max compression.
                                     Default 6 is a good balance for CPU-constrained devices.
        """
        self.compression_level = compression_level

    def compress_file(self, input_path: str, output_path: Optional[str] = None, delete_original: bool = False) -> Optional[str]:
        """
        Compresses a file using GZIP.
        
        Args:
            input_path (str): Path to the source file.
            output_path (str, optional): Path for the compressed file. 
                                         Defaults to input_path + '.gz'.
            delete_original (bool): Whether to remove the source file after compression.
            
        Returns:
            str: Path to the compressed file, or None if failed.
        """
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            return None

        if output_path is None:
            output_path = f"{input_path}.gz"

        try:
            with open(input_path, 'rb') as f_in:
                with gzip.open(output_path, 'wb', compresslevel=self.compression_level) as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            logger.info(f"Compressed {input_path} -> {output_path}")
            
            if delete_original:
                os.remove(input_path)
                logger.debug(f"Removed original file: {input_path}")
                
            return output_path

        except Exception as e:
            logger.error(f"Compression failed for {input_path}: {e}")
            return None

    def decompress_file(self, input_path: str, output_path: str) -> bool:
        """
        Decompresses a GZIP file (utility for testing/recovery).
        """
        try:
            with gzip.open(input_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            return True
        except Exception as e:
            logger.error(f"Decompression failed: {e}")
            return False

# --- Usage Example ---
if __name__ == "__main__":
    manager = CompressionManager()
    
    # Create a dummy file
    with open("test_log.json", "w") as f:
        f.write('{"data": "example nmea data repeated many times..."}' * 100)
    
    # Compress it
    compressed_file = manager.compress_file("test_log.json", delete_original=True)
    
    if compressed_file:
        original_size = os.path.getsize("test_log.json") if os.path.exists("test_log.json") else 0
        compressed_size = os.path.getsize(compressed_file)
        print(f"Compression Ratio: {compressed_size}/{original_size}")