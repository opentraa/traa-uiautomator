from pathlib import Path

from traa_uiautomator.fake_backend import FakeBackend
from traa_uiautomator.models import Rect
from traa_uiautomator.service import UiAutomatorService


class StubOcrEngine:
    def find_text(self, image_path: str, query: str) -> list[dict[str, object]]:
        assert image_path == "fake.png"
        assert query == "Login"
        return [
            {
                "text": "Login",
                "confidence": 0.97,
                "rect": Rect(x=10, y=20, width=40, height=18),
            }
        ]


def test_service_find_text_uses_snapshot_and_returns_structured_candidates() -> None:
    service = UiAutomatorService(FakeBackend(), ocr_engine=StubOcrEngine())

    result = service.find_text("Login")

    assert result["ok"] is True
    assert result["message"] == "1 text match found"
    assert result["matches"][0]["text"] == "Login"
    assert result["matches"][0]["rect"] == {"x": 10, "y": 20, "width": 40, "height": 18}
