from traa_uiautomator.fake_backend import FakeBackend
from traa_uiautomator.models import Rect
from traa_uiautomator.service import UiAutomatorService


class RankedOcrEngine:
    def find_text(self, image_path: str, query: str) -> list[dict[str, object]]:
        return [
            {
                "text": "Login Later",
                "confidence": 0.99,
                "rect": Rect(x=100, y=20, width=80, height=18),
            },
            {
                "text": "Login",
                "confidence": 0.90,
                "rect": Rect(x=10, y=20, width=40, height=18),
            },
        ]


def test_click_text_prefers_exact_match_over_higher_confidence_partial_match() -> None:
    backend = FakeBackend()
    service = UiAutomatorService(backend, ocr_engine=RankedOcrEngine())

    result = service.click_text("Login", dry_run=True)

    assert result["ok"] is True
    assert result["target_point"] == {"x": 30, "y": 29}
