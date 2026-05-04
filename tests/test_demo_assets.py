from pathlib import Path


def test_demo_assets_directory_exists() -> None:
    assert Path('demo-assets').exists() is True
