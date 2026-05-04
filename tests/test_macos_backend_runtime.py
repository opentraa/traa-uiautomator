from pathlib import Path

from PIL import Image

from traa_uiautomator.macos_backend import MacOsShellBackend


def test_snapshot_reads_image_dimensions_from_captured_file(tmp_path: Path) -> None:
    def screencapture_runner(command: list[str]) -> None:
        Image.new("RGB", (40, 25), color="white").save(command[-1])

    backend = MacOsShellBackend(
        screenshot_dir=tmp_path,
        screencapture_runner=screencapture_runner,
    )

    snapshot = backend.snapshot()

    assert snapshot.width == 40
    assert snapshot.height == 25
    assert snapshot.path.endswith('.png')


def test_wait_for_change_detects_changed_snapshot(tmp_path: Path) -> None:
    counter = {"value": 0}

    def screencapture_runner(command: list[str]) -> None:
        size = (20, 20) if counter["value"] == 0 else (21, 20)
        Image.new("RGB", size, color="white").save(command[-1])
        counter["value"] += 1

    backend = MacOsShellBackend(
        screenshot_dir=tmp_path,
        screencapture_runner=screencapture_runner,
    )

    result = backend.wait_for_change(timeout_ms=50, poll_interval_ms=1)

    assert result.ok is True
    assert result.message == "change detected"
