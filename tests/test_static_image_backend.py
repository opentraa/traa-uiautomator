from pathlib import Path

from PIL import Image

from traa_uiautomator.static_image_backend import StaticImageBackend


def test_static_image_backend_returns_fixed_snapshot_and_records_clicks(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"
    Image.new("RGB", (320, 120), color="white").save(image_path)

    backend = StaticImageBackend(image_path)
    snapshot = backend.snapshot()
    click_result = backend.click_at(30, 40)

    assert snapshot.width == 320
    assert snapshot.height == 120
    assert snapshot.path == str(image_path)
    assert click_result["ok"] is True
    assert backend.clicks == [(30, 40)]
