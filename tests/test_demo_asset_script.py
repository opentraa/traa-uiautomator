from pathlib import Path
import subprocess


def test_generate_demo_asset_script_creates_output(tmp_path: Path) -> None:
    output = tmp_path / "ocr-demo.png"
    subprocess.run([
        "uv", "run", "python", "scripts/generate_demo_asset.py", str(output), "Login"
    ], check=True)
    assert output.exists() is True
