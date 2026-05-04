from traa_uiautomator.fake_backend import FakeBackend
from traa_uiautomator.models import Rect
from traa_uiautomator.service import UiAutomatorService


class StubOcrEngine:
    def find_text(self, image_path: str, query: str) -> list[dict[str, object]]:
        return [{"text": query, "confidence": 1.0, "rect": Rect(x=10, y=20, width=40, height=20)}]


def test_click_text_dry_run_returns_target_without_clicking() -> None:
    backend = FakeBackend()
    service = UiAutomatorService(backend, ocr_engine=StubOcrEngine())

    result = service.click_text("Login", dry_run=True)

    assert result["ok"] is True
    assert result["message"] == "resolved text match 'Login'"
    assert result["target_point"] == {"x": 30, "y": 30}
    assert backend.events == ["snapshot"]
