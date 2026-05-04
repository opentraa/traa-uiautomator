from pathlib import Path
import pytest

from traa_uiautomator.traa_backend import RealTraaSnapshotProvider, resolve_traa_library_path


def test_real_traa_provider_can_create_png_snapshot_when_screen_source_available(tmp_path: Path) -> None:
    pytest.skip("manual integration test: real traa snapshot requires macOS capture permission and interactive validation")
    library_path = resolve_traa_library_path()
    if not library_path:
        raise AssertionError('expected a built traa dylib path for this test')

    provider = RealTraaSnapshotProvider(library_path, output_dir=tmp_path)
    sources = [item for item in provider.list_sources() if not item.get('is_window', False)]
    if not sources:
        return

    path, width, height = provider.create_snapshot(int(sources[0]['id']))

    assert Path(path).exists() is True
    assert width > 0
    assert height > 0
    assert path.endswith('.png')
