from pathlib import Path

from PIL import Image, ImageDraw

from traa_uiautomator.vision_ocr import VisionOcrEngine


def test_vision_ocr_engine_returns_list_for_real_swift_run(tmp_path: Path) -> None:
    image_path = tmp_path / "ocr-sample.png"
    image = Image.new("RGB", (400, 120), color="white")
    draw = ImageDraw.Draw(image)
    draw.text((20, 40), "Login", fill="black")
    image.save(image_path)

    engine = VisionOcrEngine()
    matches = engine.find_text(str(image_path), "Login")

    assert isinstance(matches, list)
