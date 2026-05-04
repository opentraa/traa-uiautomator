from __future__ import annotations

from .service import UiAutomatorService


def run_controlled_demo(backend: object, ocr_engine: object, query: str, dry_run: bool) -> dict[str, object]:
    service = UiAutomatorService(backend, ocr_engine=ocr_engine)
    return {
        "snapshot": service.snapshot_result(),
        "find_text": service.find_text(query),
        "click_text": service.click_text(query, dry_run=dry_run),
    }
