from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

VALID_COST_MODES = {"free", "balanced", "quality"}


@dataclass
class ProviderConfig:
    enabled: bool = False
    model: str = ""
    free_only: bool = False


@dataclass
class AIConfig:
    cost_mode: str = "free"
    allow_paid_fallback: bool = False
    monthly_budget_usd: float = 0.0
    require_cost_approval: bool = True
    providers: dict[str, ProviderConfig] = field(
        default_factory=lambda: {
            "ollama": ProviderConfig(enabled=True, model="qwen2.5-coder:7b", free_only=True),
            "gemini": ProviderConfig(enabled=False, model="gemini-flash", free_only=True),
            "openrouter": ProviderConfig(enabled=False, model="openrouter/free", free_only=True),
            "openai": ProviderConfig(enabled=False, model="", free_only=False),
        }
    )


@dataclass
class CoreConfig:
    ai: AIConfig = field(default_factory=AIConfig)
    workspace_path: str = ""
    library_path: str = ""


def default_config_path() -> Path:
    return Path.home() / ".callmetk-os" / "config.json"


def _provider_from_dict(value: dict[str, Any]) -> ProviderConfig:
    return ProviderConfig(
        enabled=bool(value.get("enabled", False)),
        model=str(value.get("model", "")),
        free_only=bool(value.get("free_only", False)),
    )


def config_from_dict(data: dict[str, Any]) -> CoreConfig:
    ai_data = data.get("ai", {})
    providers_data = ai_data.get("providers", {})
    providers = AIConfig().providers
    for name, value in providers_data.items():
        if isinstance(value, dict):
            providers[name] = _provider_from_dict(value)
    ai = AIConfig(
        cost_mode=str(ai_data.get("cost_mode", "free")),
        allow_paid_fallback=bool(ai_data.get("allow_paid_fallback", False)),
        monthly_budget_usd=float(ai_data.get("monthly_budget_usd", 0.0)),
        require_cost_approval=bool(ai_data.get("require_cost_approval", True)),
        providers=providers,
    )
    if ai.cost_mode not in VALID_COST_MODES:
        ai.cost_mode = "free"
    return CoreConfig(
        ai=ai,
        workspace_path=str(data.get("workspace_path", "")),
        library_path=str(data.get("library_path", "")),
    )


def load_config(path: Path | None = None) -> CoreConfig:
    config_path = (path or default_config_path()).expanduser().resolve()
    if not config_path.exists():
        return CoreConfig()
    data = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("CTK Core config must contain a JSON object.")
    return config_from_dict(data)


def save_config(config: CoreConfig, path: Path | None = None) -> Path:
    config_path = (path or default_config_path()).expanduser().resolve()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(asdict(config), indent=2) + "\n", encoding="utf-8")
    return config_path
