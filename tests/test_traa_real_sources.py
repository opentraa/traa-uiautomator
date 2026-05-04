import pytest

from traa_uiautomator.traa_backend import RealTraaSnapshotProvider, resolve_traa_library_path


def test_real_traa_provider_list_sources_returns_structured_items_or_empty_when_permission_denied() -> None:
    pytest.skip("manual integration test: real traa source enumeration may block on macOS permission flow")
    library_path = resolve_traa_library_path()
    if not library_path:
        raise AssertionError('expected a built traa dylib path for this test')

    provider = RealTraaSnapshotProvider(library_path)
    sources = provider.list_sources()

    assert isinstance(sources, list)
    if sources:
        assert 'id' in sources[0]
        assert 'is_window' in sources[0]
