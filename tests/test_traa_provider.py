from traa_uiautomator.traa_backend import TraaBackend


class StubProvider:
    def list_sources(self) -> list[dict[str, object]]:
        return [{"id": 1, "is_window": False}]

    def create_snapshot(self, source_id: int) -> tuple[str, int, int]:
        assert source_id == 1
        return ("/tmp/traa-snapshot.png", 800, 600)


def test_traa_backend_can_use_provider_for_snapshot() -> None:
    backend = TraaBackend(provider=StubProvider())
    result = backend.snapshot_result()

    assert result["ok"] is True
    assert result["source_id"] == "traa-provider:1"
    assert result["width"] == 800
    assert result["height"] == 600
