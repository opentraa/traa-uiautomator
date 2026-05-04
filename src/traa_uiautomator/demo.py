from __future__ import annotations


def run_demo(service: object, query: str) -> dict[str, object]:
    snapshot = service.snapshot_result()
    find_text = service.find_text(query)
    click_text = service.click_text(query)
    return {
        "snapshot": snapshot,
        "find_text": find_text,
        "click_text": click_text,
    }
