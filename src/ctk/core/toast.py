from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ToastDecision:
    target: str
    options: list[str]
    selection: str
    confidence: float
    reasoning: list[str]
    evidence: list[dict[str, Any]] = field(default_factory=list)
    alternatives: list[str] = field(default_factory=list)
    estimated_cost_usd: float = 0.0
    requires_approval: bool = True

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.target.strip():
            errors.append("target is required")
        if not self.options:
            errors.append("at least one option is required")
        if self.selection not in self.options:
            errors.append("selection must be included in options")
        if not 0.0 <= self.confidence <= 1.0:
            errors.append("confidence must be between 0 and 1")
        if self.estimated_cost_usd < 0:
            errors.append("estimated cost cannot be negative")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
