from traa_uiautomator.fake_backend import FakeBackend
from traa_uiautomator.models import Point
from traa_uiautomator.service import UiAutomatorService


def test_service_delegates_to_backend_and_returns_structured_result() -> None:
    backend = FakeBackend()
    service = UiAutomatorService(backend)

    snapshot = service.snapshot()
    click_result = service.click(Point(x=10, y=20))
    type_result = service.type_text("hello")

    assert snapshot.source_id == "fake-source"
    assert click_result.ok is True
    assert click_result.message == "clicked at (10, 20)"
    assert type_result.ok is True
    assert backend.events == [
        "snapshot",
        "click:10,20",
        "type:hello",
    ]
