#!/usr/bin/env python3
# This script tests the transmission components (Webhook and Sync) by mocking network calls and file system operations. This ensures the logic is sound without requiring a live server.
"""
Unit Tests for Project Haris Transmission Modules
Tests Compression, Webhook sending, and Sync logic.
"""

import unittest
from unittest.mock import patch, MagicMock, call
import os
import sys
import tempfile
import gzip

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/transmission')))

from compression_manager import CompressionManager
from webhook_sender import WebhookSender
from sync_to_server import SyncManager

class TestCompressionManager(unittest.TestCase):
    
    def test_compress_file(self):
        """Test that a file is successfully compressed into a .gz file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a dummy file
            original_path = os.path.join(tmpdir, "test.txt")
            with open(original_path, 'w') as f:
                f.write("Hello World" * 100)

            manager = CompressionManager()
            compressed_path = manager.compress_file(original_path)
            
            # Assertions
            self.assertTrue(os.path.exists(compressed_path))
            self.assertTrue(compressed_path.endswith('.gz'))
            self.assertLess(os.path.getsize(compressed_path), os.path.getsize(original_path))

    def test_decompress_file(self):
        """Test decompression returns original content."""
        content = "Secret Data"
        with tempfile.TemporaryDirectory() as tmpdir:
            original_path = os.path.join(tmpdir, "orig.txt")
            with open(original_path, 'w') as f:
                f.write(content)
            
            manager = CompressionManager()
            compressed_path = manager.compress_file(original_path)
            
            restored_path = os.path.join(tmpdir, "restored.txt")
            success = manager.decompress_file(compressed_path, restored_path)
            
            self.assertTrue(success)
            with open(restored_path, 'r') as f:
                self.assertEqual(f.read(), content)

class TestWebhookSender(unittest.TestCase):
    
    @patch('webhook_sender.requests.post')
    def test_send_success(self, mock_post):
        """Test successful webhook transmission."""
        # Configure the mock to return a success response
        mock_post.return_value.status_code = 200
        
        sender = WebhookSender(endpoint_url="http://fake.url/api")
        payload = {"status": "ok"}
        
        result = sender.send(payload, retry_count=1)
        
        self.assertTrue(result)
        mock_post.assert_called_once()

    @patch('webhook_sender.requests.post')
    def test_send_failure_with_retries(self, mock_post):
        """Test that retries happen on network failure."""
        # Configure mock to raise an exception (simulating network error)
        mock_post.side_effect = Exception("Network Error")
        
        sender = WebhookSender(endpoint_url="http://fake.url/api")
        payload = {"status": "fail"}
        
        result = sender.send(payload, retry_count=3)
        
        self.assertFalse(result)
        # Assert it tried 3 times
        self.assertEqual(mock_post.call_count, 3)

class TestSyncManager(unittest.TestCase):
    
    @patch('sync_to_server.subprocess.run')
    def test_sync_success(self, mock_run):
        """Test rsync command construction for successful sync."""
        # Simulate successful rsync
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "sent 100 bytes"
        
        syncer = SyncManager(
            remote_user="user", 
            remote_host="10.0.0.1", 
            remote_path="/data"
        )
        
        result = syncer.sync_directory("/local/data")
        
        self.assertTrue(result)
        # Verify rsync was called with correct args
        args = mock_run.call_args[0][0]
        self.assertIn('rsync', args)
        self.assertIn('user@10.0.0.1:/data/', args)

if __name__ == '__main__':
    unittest.main()