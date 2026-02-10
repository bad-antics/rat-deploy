import unittest, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from rat_deploy.core import RATDetector

class TestDetector(unittest.TestCase):
    def test_indicators(self):
        d = RATDetector()
        self.assertIn(4444, d.INDICATORS["suspicious_ports"])
    def test_scan(self):
        d = RATDetector()
        r = d.scan_connections()
        self.assertIsInstance(r, list)

if __name__ == "__main__": unittest.main()
