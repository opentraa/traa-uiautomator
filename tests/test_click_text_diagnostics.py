from traa_uiautomator.fake_backend import FakeBackend
from traa_uiautomator.service import UiAutomatorService


class EmptyOcrEngine:
    def find_text(self, image_path: str, query: str) -> list[dict[str, object]]:
        return []


def test_click_text_failure_includes_diagnostic_artifacts() -> None:
    service = UiAutomatorService(FakeBackend(), ocr_engine=EmptyOcrEngine())

    result = service.click_text("Login")

    assert result["ok"] is False
    assert result["error_code"] == "TEXT_NOT_FOUND"
    assert "snapshot_path" in result["artifacts"]
    assert result["artifacts"]["query"] == "Login"
    assert result["artifacts"]["matches"] == []
