from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class Point:
    x: int
    y: int


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    width: int
    height: int

    def contains(self, point: Point) -> bool:
        return self.x <= point.x < self.x + self.width and self.y <= point.y < self.y + self.height


@dataclass
class ActionResult:
    ok: bool
    error_code: str | None
    message: str
    artifacts: dict[str, str] = field(default_factory=dict)
    observation_summary: str | None = None
    next_action_hints: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
