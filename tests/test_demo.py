from traa_uiautomator.demo import run_demo


class StubService:
    def snapshot_result(self) -> dict[str, object]:
        return {"ok": True, "message": "snapshot captured"}

    def find_text(self, query: str) -> dict[str, object]:
        return {"ok": True, "matches": [{"text": query}]}

    def click_text(self, query: str) -> dict[str, object]:
        return {"ok": True, "message": f"clicked text match '{query}'"}


def test_run_demo_returns_snapshot_find_and_click_results() -> None:
    result = run_demo(StubService(), "Login")

    assert result["snapshot"]["ok"] is True
    assert result["find_text"]["matches"][0]["text"] == "Login"
    assert result["click_text"]["message"] == "clicked text match 'Login'"
