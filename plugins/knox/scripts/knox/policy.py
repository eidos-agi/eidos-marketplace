from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .config import DEFAULT_POLICY_PATH


def _default_policy() -> dict[str, Any]:
    return {
        "providers": {
            "github": {
                "operations": {
                    "list_repos": {"risk": "low", "summary": "List authenticated GitHub repositories."},
                    "get_user": {"risk": "low", "summary": "Read public identity for authenticated account."},
                    "create_issue": {"risk": "high", "summary": "Create an issue in a repository."},
                }
            },
            "openrouter": {
                "operations": {
                    "list_models": {"risk": "low", "summary": "List available model metadata."},
                    "list_credits": {"risk": "low", "summary": "Read credit metadata."},
                    "run_query": {"risk": "high", "summary": "Run a model request through OpenRouter."},
                }
            },
            "local": {
                "operations": {
                    "time": {"risk": "low", "summary": "Return UTC timestamp metadata."},
                    "echo": {"risk": "low", "summary": "Echo request metadata for smoke testing."},
                }
            },
            "knox": {
                "operations": {
                    "store_secret": {"risk": "high", "summary": "Store or replace a Keychain-backed provider secret."},
                    "list_secrets": {"risk": "medium", "summary": "List stored secret metadata without secret values."},
                }
            },
        }
    }


@dataclass(frozen=True)
class OperationPolicy:
    provider: str
    name: str
    risk: str
    summary: str


def load_policy() -> dict[str, Any]:
    if DEFAULT_POLICY_PATH.exists():
        try:
            payload = json.loads(DEFAULT_POLICY_PATH.read_text(encoding="utf-8"))
            policy = _default_policy()
            policy.update(payload)
            return policy
        except (OSError, json.JSONDecodeError):
            return _default_policy()
    return _default_policy()


def is_operation_allowed(policy: dict[str, Any], provider: str, operation: str) -> bool:
    provider_cfg = policy.get("providers", {}).get(provider)
    if not isinstance(provider_cfg, dict):
        return False
    return operation in (provider_cfg.get("operations", {}) or {})


def list_supported_operations(policy: dict[str, Any], provider: str | None = None) -> list[str]:
    operations: list[str] = []
    providers = policy.get("providers", {})
    if provider is not None:
        providers = {provider: providers.get(provider, {})}
    for name, cfg in providers.items():
        for op in (cfg.get("operations", {}) or {}):
            operations.append(f"{name}:{op}")
    return sorted(operations)


def operation_policy(policy: dict[str, Any], provider: str, operation: str) -> OperationPolicy:
    cfg = policy["providers"].get(provider, {}).get("operations", {}).get(operation)
    if not isinstance(cfg, dict):
        raise KeyError(f"unknown operation {provider}:{operation}")
    return OperationPolicy(
        provider=provider,
        name=operation,
        risk=cfg.get("risk", "low"),
        summary=cfg.get("summary", ""),
    )
