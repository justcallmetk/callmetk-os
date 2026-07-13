from __future__ import annotations

from dataclasses import dataclass

from ctk.core.config import CoreConfig


@dataclass(frozen=True)
class ProviderCapability:
    name: str
    is_local: bool
    can_be_free: bool
    supports_text: bool = True
    supports_vision: bool = False


PROVIDER_CAPABILITIES = {
    "ollama": ProviderCapability("ollama", is_local=True, can_be_free=True),
    "gemini": ProviderCapability("gemini", is_local=False, can_be_free=True, supports_vision=True),
    "openrouter": ProviderCapability("openrouter", is_local=False, can_be_free=True, supports_vision=True),
    "openai": ProviderCapability("openai", is_local=False, can_be_free=False, supports_vision=True),
}


def enabled_providers(config: CoreConfig) -> list[str]:
    return [name for name, value in config.ai.providers.items() if value.enabled]


def provider_is_allowed(config: CoreConfig, provider: str, estimated_cost_usd: float) -> bool:
    item = config.ai.providers.get(provider)
    if item is None or not item.enabled:
        return False
    capability = PROVIDER_CAPABILITIES.get(provider)
    if capability is None:
        return False
    if config.ai.cost_mode == "free":
        return estimated_cost_usd == 0 and (capability.can_be_free or capability.is_local)
    if estimated_cost_usd > config.ai.monthly_budget_usd and config.ai.monthly_budget_usd >= 0:
        return False
    return True
