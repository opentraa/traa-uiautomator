from traa_uiautomator.vision_ocr import VisionOcrEngine


def test_default_runner_uses_repo_script_path() -> None:
    command = VisionOcrEngine.build_command("/tmp/a.png", "Login")
    assert command[0] == "swift"
    assert command[1].endswith("scripts/vision_ocr.swift")
    assert command[2:] == ["/tmp/a.png", "Login"]
