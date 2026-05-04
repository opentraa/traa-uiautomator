from traa_uiautomator.traa_backend import TraaBackend


def test_traa_backend_is_explicitly_not_implemented_yet() -> None:
    backend = TraaBackend()
    result = backend.snapshot_result()

    assert result["ok"] is False
    assert result["error_code"] == "NOT_IMPLEMENTED"
