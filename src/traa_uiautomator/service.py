from __future__ import annotations

from .backend import Backend, Snapshot
from .models import ActionResult, Point
from .ocr import NullOcrEngine, OcrEngine


class UiAutomatorService:
    def __init__(self, backend: Backend, ocr_engine: OcrEngine | None = None) -> None:
        self._backend = backend
        self._ocr_engine = ocr_engine or NullOcrEngine()

    def snapshot(self) -> Snapshot:
        return self._backend.snapshot()

    def snapshot_result(self) -> dict[str, object]:
        snapshot = self.snapshot()
        return {
            "ok": True,
            "error_code": None,
            "message": "snapshot captured",
            "artifacts": {"snapshot_path": snapshot.path},
            "observation_summary": (
                f"Captured source {snapshot.source_id} at {snapshot.width}x{snapshot.height}"
            ),
            "next_action_hints": ["locate_target", "click", "type_text"],
            "source_id": snapshot.source_id,
            "width": snapshot.width,
            "height": snapshot.height,
        }

    def click(self, point: Point) -> ActionResult:
        return self._backend.click(point)

    def click_at(self, x: int, y: int) -> dict[str, object]:
        return self.click(Point(x=x, y=y)).to_dict()

    def type_text(self, text: str) -> ActionResult:
        return self._backend.type_text(text)

    def type_text_result(self, text: str) -> dict[str, object]:
        return self.type_text(text).to_dict()

    def press_hotkey(self, keys: tuple[str, ...]) -> ActionResult:
        return self._backend.press_hotkey(keys)

    def press_hotkey_list(self, keys: list[str]) -> dict[str, object]:
        return self.press_hotkey(tuple(keys)).to_dict()

    def wait_for_change(self, timeout_ms: int) -> ActionResult:
        return self._backend.wait_for_change(timeout_ms)

    def wait_for_change_result(self, timeout_ms: int) -> dict[str, object]:
        return self.wait_for_change(timeout_ms).to_dict()

    @staticmethod
    def _rank_matches(query: str, matches: list[dict[str, object]]) -> list[dict[str, object]]:
        query_lower = query.lower()

        def sort_key(match: dict[str, object]) -> tuple[int, float]:
            text = str(match["text"]).lower()
            exact = 0 if text == query_lower else 1
            confidence = -float(match["confidence"])
            return (exact, confidence)

        return sorted(matches, key=sort_key)

    def find_text(self, query: str) -> dict[str, object]:
        snapshot = self.snapshot()
        matches = []
        for match in self._ocr_engine.find_text(snapshot.path, query):
            rect = match["rect"]
            matches.append(
                {
                    "text": match["text"],
                    "confidence": match["confidence"],
                    "rect": {
                        "x": rect.x,
                        "y": rect.y,
                        "width": rect.width,
                        "height": rect.height,
                    },
                }
            )
        matches = self._rank_matches(query, matches)

        return {
            "ok": True,
            "error_code": None,
            "message": f"{len(matches)} text match found" if len(matches) == 1 else f"{len(matches)} text matches found",
            "artifacts": {"snapshot_path": snapshot.path},
            "observation_summary": f"Searched snapshot for text '{query}'",
            "next_action_hints": ["click_target"] if matches else ["retry_with_new_snapshot"],
            "matches": matches,
        }

    def click_text(self, query: str, dry_run: bool = False) -> dict[str, object]:
        result = self.find_text(query)
        matches = result["matches"]
        if not matches:
            return {
                "ok": False,
                "error_code": "TEXT_NOT_FOUND",
                "message": f"no text match found for '{query}'",
                "artifacts": {
                    **result["artifacts"],
                    "query": query,
                    "matches": matches,
                },
                "observation_summary": result["observation_summary"],
                "next_action_hints": ["retry_with_new_snapshot", "find_text"],
            }

        rect = matches[0]["rect"]
        center_x = rect["x"] + rect["width"] // 2
        center_y = rect["y"] + rect["height"] // 2
        if dry_run:
            return {
                "ok": True,
                "error_code": None,
                "message": f"resolved text match '{query}'",
                "artifacts": {
                    **result["artifacts"],
                    "query": query,
                    "matches": matches,
                },
                "observation_summary": result["observation_summary"],
                "next_action_hints": ["click_at"],
                "target_point": {"x": center_x, "y": center_y},
            }
        click_result = self.click_at(center_x, center_y)
        click_result["artifacts"] = {
            **click_result.get("artifacts", {}),
            **result["artifacts"],
            "query": query,
            "matches": matches,
            "target_point": {"x": center_x, "y": center_y},
        }
        click_result["message"] = (
            f"clicked text match '{query}'"
            if click_result.get("ok")
            else f"failed to click text match '{query}'"
        )
        return click_result

    def click_text_then_type(
        self,
        query: str,
        text: str,
        timeout_ms: int = 2000,
    ) -> dict[str, object]:
        click_result = self.click_text(query, dry_run=False)
        if not click_result.get("ok"):
            return {
                "ok": False,
                "error_code": click_result.get("error_code"),
                "message": f"failed during click_text step for '{query}'",
                "artifacts": click_result.get("artifacts", {}),
                "observation_summary": click_result.get("observation_summary"),
                "next_action_hints": ["find_text", "retry_with_new_snapshot"],
                "click": click_result,
                "wait_for_change": None,
                "type_text": None,
            }

        wait_result = self.wait_for_change_result(timeout_ms)
        if not wait_result.get("ok"):
            return {
                "ok": False,
                "error_code": wait_result.get("error_code"),
                "message": "failed during wait_for_change step",
                "artifacts": {
                    **click_result.get("artifacts", {}),
                    **wait_result.get("artifacts", {}),
                },
                "observation_summary": wait_result.get("observation_summary"),
                "next_action_hints": ["retry_with_new_snapshot", "wait_for_change"],
                "click": click_result,
                "wait_for_change": wait_result,
                "type_text": None,
            }

        type_result = self.type_text_result(text)
        ok = bool(type_result.get("ok"))
        return {
            "ok": ok,
            "error_code": type_result.get("error_code"),
            "message": (
                f"clicked text '{query}', observed a change, and typed input"
                if ok
                else f"failed during type_text step after clicking '{query}'"
            ),
            "artifacts": {
                **click_result.get("artifacts", {}),
                **wait_result.get("artifacts", {}),
                **type_result.get("artifacts", {}),
            },
            "observation_summary": f"Completed multi-step workflow for text target '{query}'",
            "next_action_hints": ["submit", "press_hotkey", "wait_for_change"] if ok else ["type_text", "retry"],
            "click": click_result,
            "wait_for_change": wait_result,
            "type_text": type_result,
        }
