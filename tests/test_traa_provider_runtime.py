from traa_uiautomator.traa_backend import TraaBackend, TraaSnapshotProvider


class StubTraaProvider(TraaSnapshotProvider):
    def list_sources(self) -> list[dict[str, object]]:
        return [{"id": 42, "is_window": False}]

    def create_snapshot(self, source_id: int) -> tuple[str, int, int]:
        assert source_id == 42
        return ("/tmp/traa-snapshot.png", 1024, 768)


def test_traa_backend_uses_first_non_window_source_from_provider() -> None:
    backend = TraaBackend(provider=StubTraaProvider())
    result = backend.snapshot_result()

    assert result["ok"] is True
    assert result["source_id"] == "traa-provider:42"
    assert result["width"] == 1024
    assert result["height"] == 768
