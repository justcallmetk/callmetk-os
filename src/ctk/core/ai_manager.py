from __future__ import annotations

from ctk.core.config import CoreConfig
from ctk.core.providers import enabled_providers, provider_is_allowed
from ctk.core.toast import ToastDecision


TASK_PREFERENCES = {
    "coding": ["ollama", "gemini", "openrouter", "openai"],
    "caption": ["gemini", "openrouter", "ollama", "openai"],
    "vision": ["gemini", "openrouter", "openai"],
    "music-explanation": ["ollama", "gemini", "openrouter", "openai"],
}


def recommend_provider(
    config: CoreConfig,
    task: str,
    estimated_costs: dict[str, float] | None = None,
) -> ToastDecision:
    costs = estimated_costs or {}
    preferences = TASK_PREFERENCES.get(task, ["ollama", "gemini", "openrouter", "openai"])
    enabled = enabled_providers(config)
    options = [name for name in preferences if name in enabled]
    allowed = [name for name in options if provider_is_allowed(config, name, costs.get(name, 0.0))]

    if not allowed:
        return ToastDecision(
            target=f"Select an AI provider for {task}",
            options=options or ["none"],
            selection=(options or ["none"])[0],
            confidence=0.25,
            reasoning=["No configured provider satisfies the current cost and availability rules."],
            alternatives=options[1:] if len(options) > 1 else [],
            estimated_cost_usd=costs.get((options or ["none"])[0], 0.0),
            requires_approval=True,
        )

    selected = allowed[0]
    cost = costs.get(selected, 0.0)
    requires_approval = cost > 0 and config.ai.require_cost_approval
    confidence = 0.95 if selected == "ollama" and cost == 0 else 0.88
    reasoning = [
        f"{selected} is enabled and permitted in {config.ai.cost_mode} mode.",
        "The provider matches the configured task preference order.",
    ]
    if cost == 0:
        reasoning.append("Estimated provider cost is $0.00.")
    return ToastDecision(
        target=f"Select an AI provider for {task}",
        options=options,
        selection=selected,
        confidence=confidence,
        reasoning=reasoning,
        alternatives=[name for name in allowed[1:]],
        estimated_cost_usd=cost,
        requires_approval=requires_approval,
    )
