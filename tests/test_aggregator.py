"""Tests for the Signal K polling aggregator (data_aggregator.py).

Covers the freshness filter — the core fix that keeps stale values out of ES.
"""
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "data_collection"))
import data_aggregator as agg


def node(value, ts):
    """Helper: a Signal K-style node with value + timestamp."""
    return {"value": value, "timestamp": ts, "$source": "sim-tcp.GP"}


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class TestBlankStaleValues(unittest.TestCase):
    def test_fresh_value_kept(self):
        payload = {"navigation": {"position": node({"latitude": 58.4, "longitude": 24.5}, now_iso())}}
        out = agg.blank_stale_values(payload, 30)
        self.assertIsNotNone(out["navigation"]["position"]["value"])

    def test_stale_value_blanked(self):
        stale = "2025-12-10T10:07:21.000Z"  # the classic hardcoded sim date
        payload = {"navigation": {"position": node({"latitude": 55.0, "longitude": 14.2}, stale)}}
        out = agg.blank_stale_values(payload, 30)
        self.assertIsNone(out["navigation"]["position"]["value"])
        # timestamp/meta survive — only the value is blanked
        self.assertEqual(out["navigation"]["position"]["timestamp"], stale)

    def test_stale_nested_and_fresh_sibling(self):
        fresh = now_iso()
        stale = "2025-12-10T10:07:21.000Z"
        payload = {
            "navigation": {
                "headingTrue": node(4.28, fresh),
                "position": node({"latitude": 55.0, "longitude": 14.2}, stale),
            }
        }
        out = agg.blank_stale_values(payload, 30)
        self.assertIsNotNone(out["navigation"]["headingTrue"]["value"])
        self.assertIsNone(out["navigation"]["position"]["value"])

    def test_non_signal_nodes_untouched(self):
        payload = {"environment": {"mode": {"value": "auto"}}}
        out = agg.blank_stale_values(payload, 30)
        self.assertEqual(out["environment"]["mode"]["value"], "auto")


class TestBuildEvent(unittest.TestCase):
    def test_event_shape(self):
        payload = {"navigation": {"headingTrue": node(4.28, now_iso())}}
        event = agg.build_event(payload)
        self.assertIn("@timestamp", event)
        self.assertEqual(event["source"], "haris_signalk")
        self.assertIn("haris_host", event)
        self.assertIn("vessel_id", event)
        self.assertIn("vessel_name", event)
        self.assertIn("signalk", event)


if __name__ == "__main__":
    unittest.main()
