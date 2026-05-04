from pathlib import Path

from PIL import Image, ImageDraw

from traa_uiautomator.demo_controlled import run_controlled_demo
from traa_uiautomator.static_image_backend import StaticImageBackend
from traa_uiautomator.vision_ocr import VisionOcrEngine


def test_controlled_demo_supports_dry_run(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"
    image = Image.new("RGB", (400, 120), color="white")
    draw = ImageDraw.Draw(image)
    draw.text((20, 40), "Login", fill="black")
    image.save(image_path)

    backend = StaticImageBackend(image_path)
    result = run_controlled_demo(backend=backend, ocr_engine=VisionOcrEngine(), query="Login", dry_run=True)

    assert result["click_text"]["ok"] is True
    assert result["click_text"]["target_point"]["x"] >= 0
    assert backend.clicks == []
