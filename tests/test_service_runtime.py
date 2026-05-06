from traa_uiautomator.fake_backend import FakeBackend
from traa_uiautomator.models import Point
from traa_uiautomator.service import UiAutomatorService


def test_service_snapshot_returns_agent_friendly_payload() -> None:
    service = UiAutomatorService(FakeBackend())

    result = service.snapshot_result()

    assert result["ok"] is True
    assert result["message"] == "snapshot captured"
    assert result["artifacts"]["snapshot_path"] == "fake.png"
    assert result["observation_summary"] == "Captured source fake-source at 1280x720"
    assert result["next_action_hints"] == ["locate_target", "click", "type_text"]


def test_service_wait_for_change_surfaces_backend_result() -> None:
    service = UiAutomatorService(FakeBackend())

    result = service.wait_for_change(timeout_ms=1500)

    assert result.ok is True
    assert result.message == "change detected within 1500ms"


def test_service_click_and_hotkey_delegate_to_backend() -> None:
    backend = FakeBackend()
    service = UiAutomatorService(backend)

    click_result = service.click(Point(x=7, y=9))
    hotkey_result = service.press_hotkey(("command", "k"))

    assert click_result.ok is True
    assert hotkey_result.ok is True
    assert backend.events[-2:] == ["click:7,9", "hotkey:command+k"]


def test_click_text_then_type_runs_multistep_workflow() -> None:
    backend = FakeBackend()

    class StubOcrEngine:
        def find_text(self, image_path: str, query: str) -> list[dict[str, object]]:
            return [
                {
                    "text": "Login",
                    "confidence": 0.95,
                    "rect": type("Rect", (), {"x": 10, "y": 20, "width": 40, "height": 10})(),
                }
            ]

    service = UiAutomatorService(backend, ocr_engine=StubOcrEngine())

    result = service.click_text_then_type("Login", "hello", timeout_ms=1200)

    assert result["ok"] is True
    assert result["click"]["ok"] is True
    assert result["wait_for_change"]["ok"] is True
    assert result["type_text"]["ok"] is True
    assert result["next_action_hints"] == ["submit", "press_hotkey", "wait_for_change"]
    assert backend.events == [
        "snapshot",
        "click:30,25",
        "wait_for_change:1200",
        "type:hello",
    ]


def test_click_text_then_type_stops_when_click_fails() -> None:
    class FailingBackend(FakeBackend):
        def click(self, point: Point):  # type: ignore[override]
            self.events.append(f"click:{point.x},{point.y}")
            from traa_uiautomator.models import ActionResult

            return ActionResult(ok=False, error_code="CLICK_FAILED", message="click failed")

    backend = FailingBackend()

    class StubOcrEngine:
        def find_text(self, image_path: str, query: str) -> list[dict[str, object]]:
            return [
                {
                    "text": "Login",
                    "confidence": 0.95,
                    "rect": type("Rect", (), {"x": 10, "y": 20, "width": 40, "height": 10})(),
                }
            ]

    service = UiAutomatorService(backend, ocr_engine=StubOcrEngine())

    result = service.click_text_then_type("Login", "hello")

    assert result["ok"] is False
    assert result["error_code"] == "CLICK_FAILED"
    assert result["type_text"] is None
    assert backend.events == ["snapshot", "click:30,25"]
