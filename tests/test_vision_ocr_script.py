from pathlib import Path


def test_vision_ocr_swift_script_exists() -> None:
    script = Path("scripts/vision_ocr.swift")
    assert script.exists() is True
