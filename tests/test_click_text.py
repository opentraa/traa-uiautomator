from traa_uiautomator.fake_backend import FakeBackend
from traa_uiautomator.models import Rect
from traa_uiautomator.service import UiAutomatorService


class StubOcrEngine:
    def find_text(self, image_path: str, query: str) -> list[dict[str, object]]:
        return [
            {
                "text": query,
                "confidence": 0.98,
                "rect": Rect(x=10, y=20, width=40, height=20),
            }
        ]


def test_click_text_finds_match_and_clicks_rect_center() -> None:
    backend = FakeBackend()
    service = UiAutomatorService(backend, ocr_engine=StubOcrEngine())

    result = service.click_text("Login")

    assert result["ok"] is True
    assert result["message"] == "clicked text match 'Login'"
    assert backend.events[-1] == "click:30,30"
