from traa_uiautomator.models import ActionResult, Point, Rect


def test_action_result_to_dict_contains_expected_fields() -> None:
    result = ActionResult(
        ok=True,
        error_code=None,
        message="clicked",
        artifacts={"before": "a.png"},
        observation_summary="button visible",
        next_action_hints=["continue"],
    )

    assert result.to_dict() == {
        "ok": True,
        "error_code": None,
        "message": "clicked",
        "artifacts": {"before": "a.png"},
        "observation_summary": "button visible",
        "next_action_hints": ["continue"],
    }


def test_rect_contains_point() -> None:
    rect = Rect(x=10, y=20, width=100, height=50)
    point = Point(x=15, y=25)
    assert rect.contains(point) is True
