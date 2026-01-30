import sys
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))


def create_stub_module(name, **attributes):
    module = ModuleType(name)
    for attribute, value in attributes.items():
        setattr(module, attribute, value)
    return module


class DummyDatabase:
    def __init__(self):
        pass


class DummyDetector:
    def __init__(self):
        pass


class DummyMetric:
    def __init__(self, *args, **kwargs):
        pass


class TelegramOptionalStartupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        geopy_module = create_stub_module("geopy")
        geopy_geocoders = create_stub_module(
            "geopy.geocoders",
            Nominatim=lambda **kwargs: object(),
        )
        gps_provider = create_stub_module(
            "gps_provider",
            SimulatedGPS=object,
            RealGPS=object,
        )

        stubs = {
            "cv2": create_stub_module("cv2"),
            "database": create_stub_module(
                "database",
                PotholeDatabase=DummyDatabase,
            ),
            "detector": create_stub_module(
                "detector",
                PotholeDetector=DummyDetector,
            ),
            "geopy": geopy_module,
            "geopy.geocoders": geopy_geocoders,
            "gps_provider": gps_provider,
            "prometheus_client": create_stub_module(
                "prometheus_client",
                start_http_server=lambda *args, **kwargs: None,
                Counter=DummyMetric,
                Summary=DummyMetric,
            ),
            "utils": create_stub_module(
                "utils",
                save_detection_image=lambda *args, **kwargs: "",
            ),
        }

        with patch.dict(sys.modules, stubs):
            import main

        cls.main = main

    def test_video_mode_starts_without_telegram_bot(self):
        detector_stub = create_stub_module(
            "detector",
            PotholeDetector=DummyDetector,
        )
        with patch.dict(sys.modules, {"detector": detector_stub}), patch.object(
            self.main.config, "BOT_ONLY", False
        ), patch.object(self.main.config, "TELEGRAM_BOT_ENABLED", False):
            system = self.main.PotholeDetectionSystem()

        self.assertIsNone(system.bot)

    def test_enabled_bot_requires_token(self):
        with (
            patch.object(self.main.config, "BOT_ONLY", False),
            patch.object(self.main.config, "TELEGRAM_BOT_ENABLED", True),
            patch.object(self.main.config, "BOT_TOKEN", ""),
            self.assertRaisesRegex(ValueError, "BOT_TOKEN is not set"),
        ):
            self.main.PotholeDetectionSystem()


if __name__ == "__main__":
    unittest.main()
