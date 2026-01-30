import atexit
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

_test_data_dir = tempfile.TemporaryDirectory(prefix="pothole-tests-")
atexit.register(_test_data_dir.cleanup)
os.environ["DATA_DIR"] = str(Path(_test_data_dir.name) / "data")
os.environ["DB_PATH"] = str(Path(_test_data_dir.name) / "potholes.db")

from utils import calculate_distance, create_depth_report


class CalculateDistanceTests(unittest.TestCase):
    def test_same_point_has_zero_distance(self):
        self.assertEqual(calculate_distance(42.0, 19.0, 42.0, 19.0), 0.0)

    def test_one_degree_of_longitude_at_equator(self):
        distance = calculate_distance(0.0, 0.0, 0.0, 1.0)
        self.assertAlmostEqual(distance, 111_195, delta=100)

    def test_distance_is_symmetric(self):
        forward = calculate_distance(42.0, 19.0, 43.0, 20.0)
        reverse = calculate_distance(43.0, 20.0, 42.0, 19.0)
        self.assertAlmostEqual(forward, reverse, places=6)


class CreateDepthReportTests(unittest.TestCase):
    def test_empty_input_returns_empty_report(self):
        self.assertEqual(create_depth_report([]), {})

    def test_report_summarizes_depth_values(self):
        potholes = [
            SimpleNamespace(depth=0.01),
            SimpleNamespace(depth=0.04),
            SimpleNamespace(depth=0.08),
            SimpleNamespace(depth=0.12),
        ]

        report = create_depth_report(potholes)

        self.assertAlmostEqual(report["average_depth"], 0.0625)
        self.assertEqual(report["min_depth"], 0.01)
        self.assertEqual(report["max_depth"], 0.12)
        self.assertEqual(
            report["depth_distribution"],
            {"shallow": 1, "moderate": 1, "deep": 1, "very_deep": 1},
        )


if __name__ == "__main__":
    unittest.main()
