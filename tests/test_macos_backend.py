from pathlib import Path

from traa_uiautomator.macos_backend import MacOsShellBackend
from traa_uiautomator.models import Point


def test_backend_builds_expected_osascript_commands(tmp_path: Path) -> None:
    commands: list[list[str]] = []

    def runner(command: list[str]) -> None:
        commands.append(command)

    backend = MacOsShellBackend(
        screenshot_dir=tmp_path,
        runner=runner,
        screencapture_runner=runner,
    )

    backend.click(Point(x=11, y=22))
    backend.type_text("hello")
    backend.press_hotkey(("command", "space"))

    assert commands[0][:2] == ["osascript", "-e"]
    assert "cliclick" not in " ".join(" ".join(c) for c in commands)
    assert 'keystroke "hello"' in commands[1][2]
    assert "key down command" in commands[2][2]
