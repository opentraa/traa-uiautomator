from pathlib import Path

from PIL import Image

from traa_uiautomator.vision_ocr import VisionOcrEngine


def test_vision_ocr_engine_parses_json_lines_from_runner(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"
    Image.new("RGB", (20, 20), color="white").save(image_path)

    def runner(path: str, query: str) -> str:
        assert path == str(image_path)
        assert query == "Login"
        return '{"text":"Login","confidence":0.93,"rect":{"x":1,"y":2,"width":30,"height":12}}\n'

    engine = VisionOcrEngine(runner=runner)
    matches = engine.find_text(str(image_path), "Login")

    assert len(matches) == 1
    assert matches[0]["text"] == "Login"
    assert matches[0]["rect"].x == 1
    assert matches[0]["rect"].height == 12
