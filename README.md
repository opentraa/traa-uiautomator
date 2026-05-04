# traa-uiautomator

Python middleware foundation for computer observation and input automation.

## Current Scope

This repository currently contains the first executable foundation slice for the larger
`traa -> traa-uiautomator -> traa-uiautomator-skill` architecture.

Implemented today:

- Python package skeleton managed by `uv`
- common result and geometry models
- backend protocol for observation and action primitives
- fake backend for deterministic tests
- macOS shell-backed adapter for:
  - `snapshot`
  - `click`
  - `type_text`
  - `press_hotkey`
- static image backend for controlled OCR/click demos
- Vision OCR integration path through `scripts/vision_ocr.swift`
- service layer that delegates to a chosen backend
- controlled demo helpers and demo asset generator
- `traa` snapshot backend wiring through ctypes
- exact-match-first text targeting
- dry-run and real-click validation flows

## Notes

- Real `traa` native integration is not wired yet.
- Real `traa` snapshot integration is wired; input still delegates to macOS shell actions.
- This repository is focused on deterministic middleware behavior, not agent reasoning.

## Development

Run tests with:

```bash
uv run pytest -v
```

Generate a controlled OCR demo asset:

```bash
uv run python scripts/generate_demo_asset.py demo-assets/ocr-login.png Login
```

The higher-level skill repository contains the end-to-end validation commands and a documented real
dialog validation flow.
