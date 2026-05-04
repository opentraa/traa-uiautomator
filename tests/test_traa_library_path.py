from traa_uiautomator.traa_backend import resolve_traa_library_path


def test_resolve_traa_library_path_prefers_explicit_env(monkeypatch) -> None:
    monkeypatch.setenv("TRAA_LIBRARY_PATH", "/tmp/libtraa.dylib")
    assert resolve_traa_library_path() == "/tmp/libtraa.dylib"
