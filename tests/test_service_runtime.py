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
