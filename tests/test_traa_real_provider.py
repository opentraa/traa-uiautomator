from traa_uiautomator.traa_backend import resolve_traa_library_path, RealTraaSnapshotProvider


def test_real_traa_provider_can_be_constructed_when_library_exists() -> None:
    library_path = resolve_traa_library_path()
    if not library_path:
        raise AssertionError('expected a built traa dylib path for this test')

    provider = RealTraaSnapshotProvider(library_path)
    assert provider is not None
