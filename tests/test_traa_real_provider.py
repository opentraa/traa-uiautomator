import pytest

from traa_uiautomator.traa_backend import resolve_traa_library_path, RealTraaSnapshotProvider


def test_real_traa_provider_can_be_constructed_when_library_exists() -> None:
    library_path = resolve_traa_library_path()
    if not library_path:
        pytest.skip("real traa library is not available in this workspace")

    provider = RealTraaSnapshotProvider(library_path)
    assert provider is not None
