from traa_uiautomator.models import ActionResult, Rect
from traa_uiautomator.service import UiAutomatorService


class StubOcrEngine:
    def find_text(self, image_path: str, query: str) -> list[dict[str, object]]:
        return [{"text": query, "confidence": 1.0, "rect": Rect(x=10, y=20, width=40, height=20)}]


class DeniedClickBackend:
    def snapshot(self):
        from traa_uiautomator.backend import Snapshot
        return Snapshot(path="/tmp/fake.png", width=100, height=100, source_id="fake")

    def click(self, point):
        return ActionResult(
            ok=False,
            error_code="ASSISTIVE_ACCESS_DENIED",
            message="assistive access denied",
        )

    def type_text(self, text):
        return ActionResult(ok=True, error_code=None, message="typed")

    def press_hotkey(self, keys):
        return ActionResult(ok=True, error_code=None, message="hotkey")

    def wait_for_change(self, timeout_ms):
        return ActionResult(ok=True, error_code=None, message="waited")


def test_click_text_surfaces_click_failure_without_overwriting_error() -> None:
    service = UiAutomatorService(DeniedClickBackend(), ocr_engine=StubOcrEngine())

    result = service.click_text("Login", dry_run=False)

    assert result["ok"] is False
    assert result["error_code"] == "ASSISTIVE_ACCESS_DENIED"
    assert result["message"] == "failed to click text match 'Login'"
    assert result["artifacts"]["target_point"] == {"x": 30, "y": 30}
