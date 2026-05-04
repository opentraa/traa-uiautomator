from traa_uiautomator.models import Point
from traa_uiautomator.traa_backend import TraaBackend, TraaSnapshotProvider


class StubProvider(TraaSnapshotProvider):
    def list_sources(self) -> list[dict[str, object]]:
        return [{"id": 1, "is_window": False}]

    def create_snapshot(self, source_id: int) -> tuple[str, int, int]:
        return ("/tmp/traa-snapshot.png", 800, 600)


class StubActionBackend:
    def __init__(self) -> None:
        self.events: list[str] = []

    def click(self, point: Point):
        self.events.append(f"click:{point.x},{point.y}")
        return {"ok": True, "message": "clicked"}

    def type_text(self, text: str):
        self.events.append(f"type:{text}")
        return {"ok": True, "message": "typed"}

    def press_hotkey(self, keys: tuple[str, ...]):
        self.events.append("hotkey:" + "+".join(keys))
        return {"ok": True, "message": "hotkey"}

    def wait_for_change(self, timeout_ms: int):
        self.events.append(f"wait:{timeout_ms}")
        return {"ok": True, "message": "waited"}


def test_traa_backend_delegates_actions_to_action_backend() -> None:
    action_backend = StubActionBackend()
    backend = TraaBackend(provider=StubProvider(), action_backend=action_backend)

    backend.click(Point(x=10, y=20))
    backend.type_text("hello")
    backend.press_hotkey(("command", "space"))
    backend.wait_for_change(2000)

    assert action_backend.events == [
        "click:10,20",
        "type:hello",
        "hotkey:command+space",
        "wait:2000",
    ]
