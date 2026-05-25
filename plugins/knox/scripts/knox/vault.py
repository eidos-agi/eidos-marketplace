from __future__ import annotations

from contextlib import contextmanager
import fcntl
import os
import time
from dataclasses import dataclass
from pathlib import Path
import json
import re
import tempfile
from typing import Any

from . import config
from .keychain import KnoxKeychainError, KnoxKeychainUnavailable, has_secret, read_secret, store_secret, delete_secret


@dataclass
class VaultSecretState:
    provider: str
    available: bool


@dataclass
class VaultSecretRecord:
    key_name: str
    provider: str
    source: str | None
    project: str | None
    environment: str | None
    notes: str | None
    is_default: bool
    created_at: int
    updated_at: int


class VaultError(RuntimeError):
    pass


def _normalize_identifier(value: str) -> str:
    lowered = value.strip().lower()
    normalized = re.sub(r"[^a-z0-9._-]+", "-", lowered)
    normalized = normalized.strip("-._")
    return normalized or "key"


def _registry_path() -> Path:
    return config.KNOX_REGISTRY_PATH


@contextmanager
def _registry_lock():
    lock_path = _registry_path().with_suffix(".lock")
    config.ensure_directory(lock_path.parent)
    with lock_path.open("a", encoding="utf-8") as lock_file:
        try:
            lock_path.chmod(0o600)
        except OSError:
            pass
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def _validate_provider(provider: str) -> None:
    if not provider or "/" in provider or ":" in provider:
        raise VaultError("provider must be a simple identifier")


def _validate_key_name(key_name: str) -> None:
    if not key_name or "/" in key_name or ":" in key_name:
        raise VaultError("key_name must be a non-empty simple identifier")


def has_provider_secret(provider: str) -> bool:
    _validate_provider(provider)
    if has_secret(provider):
        return True
    alias = _resolve_provider_alias(provider)
    return bool(alias and has_secret(alias))


def _load_registry() -> dict[str, Any]:
    path = _registry_path()
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise VaultError(f"failed to read Knox registry: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise VaultError(f"Knox registry is corrupt: {path}") from exc
    return payload if isinstance(payload, dict) else {}


def _save_registry(payload: dict[str, Any]) -> None:
    path = _registry_path()
    config.ensure_directory(path.parent)
    raw = json.dumps(payload, sort_keys=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as tmp:
        tmp.write(raw)
        tmp_path = Path(tmp.name)
    try:
        tmp_path.chmod(0o600)
        os.replace(tmp_path, path)
    finally:
        tmp_path.unlink(missing_ok=True)


def _record_from_dict(payload: dict[str, Any]) -> VaultSecretRecord:
    return VaultSecretRecord(
        key_name=str(payload.get("key_name", "")),
        provider=str(payload.get("provider", "")),
        source=payload.get("source"),
        project=payload.get("project"),
        environment=payload.get("environment"),
        notes=payload.get("notes"),
        is_default=bool(payload.get("is_default", True)),
        created_at=int(payload.get("created_at", 0)),
        updated_at=int(payload.get("updated_at", 0)),
    )


def _records() -> dict[str, VaultSecretRecord]:
    return {
        key_name: _record_from_dict(entry) for key_name, entry in _load_registry().items() if isinstance(key_name, str) and isinstance(entry, dict)
    }


def _resolve_provider_alias(provider: str) -> str | None:
    _validate_provider(provider)
    candidates = [record for record in _records().values() if record.provider == provider]
    if not candidates:
        return None
    default = [item for item in candidates if item.is_default]
    if default:
        return sorted(default, key=lambda item: item.key_name)[0].key_name
    return sorted(candidates, key=lambda item: item.updated_at, reverse=True)[0].key_name


def list_secret_records(provider: str | None = None) -> list[VaultSecretRecord]:
    records = _records().values()
    filtered = [record for record in records if provider is None or record.provider == provider]
    return sorted(filtered, key=lambda item: (item.provider, item.key_name))


def read_provider_secret(provider: str) -> str:
    _validate_provider(provider)
    alias = provider
    if not has_secret(alias):
        alias = _resolve_provider_alias(provider)
        if alias is None:
            raise VaultError(f"no stored key for provider '{provider}'")
        if not has_secret(alias):
            raise VaultError(f"stored key '{alias}' not found for provider '{provider}'")
    try:
        return read_secret(alias)
    except KnoxKeychainUnavailable as exc:
        raise VaultError(str(exc))
    except KnoxKeychainError as exc:
        raise VaultError(str(exc))


def read_named_secret(alias: str) -> str:
    if not alias:
        raise VaultError("secret alias is required")
    _validate_key_name(alias)
    if not has_secret(alias):
        raise VaultError(f"no secret found for alias '{alias}'")
    try:
        return read_secret(alias)
    except KnoxKeychainUnavailable as exc:
        raise VaultError(str(exc))
    except KnoxKeychainError as exc:
        raise VaultError(str(exc))


def suggest_key_name(provider: str, source: str | None = None, project: str | None = None) -> str:
    _validate_provider(provider)
    base = provider
    if source:
        base = f"{base}-{_normalize_identifier(source)}"
    if project and not source:
        base = f"{base}-{_normalize_identifier(project)}"
    candidate = _normalize_identifier(base)
    base = candidate or provider

    records = _records()
    if base not in records:
        return base

    now_suffix = time.strftime("%Y%m%d")
    for idx in range(2, 20):
        candidate = f"{base}-{now_suffix}-{idx}"
        if candidate not in records:
            return candidate
    return f"{base}-{time.time_ns()}"


def store_provider_secret(provider: str, secret: str) -> None:
    _validate_provider(provider)
    if not secret:
        raise VaultError("secret is required")
    try:
        store_secret(provider, secret)
    except KnoxKeychainUnavailable as exc:
        raise VaultError(str(exc))
    except KnoxKeychainError as exc:
        raise VaultError(str(exc))


def register_provider_secret(
    provider: str,
    secret: str,
    key_name: str | None = None,
    source: str | None = None,
    project: str | None = None,
    environment: str | None = None,
    notes: str | None = None,
    overwrite: bool = False,
) -> VaultSecretRecord:
    _validate_provider(provider)
    if not secret:
        raise VaultError("secret is required")

    with _registry_lock():
        chosen_name = _validate_and_maybe_generate_key_name(provider, key_name, source, project)
        try:
            existing = has_secret(chosen_name)
            if existing and not overwrite:
                raise VaultError(f"key_name '{chosen_name}' already exists")
            store_secret(chosen_name, secret)
        except KnoxKeychainUnavailable as exc:
            raise VaultError(str(exc))
        except KnoxKeychainError as exc:
            raise VaultError(str(exc))

        now = int(time.time())
        key_records = _records()

        if overwrite:
            key_records = {name: existing for name, existing in key_records.items() if name != chosen_name}

        # Make the new key default for its provider and preserve existing entries.
        for name in list(key_records):
            if key_records[name].provider == provider:
                key_records[name].is_default = False

        record = VaultSecretRecord(
            key_name=chosen_name,
            provider=provider,
            source=source,
            project=project,
            environment=environment,
            notes=notes,
            is_default=True,
            created_at=key_records.get(chosen_name).created_at if chosen_name in key_records else now,
            updated_at=now,
        )
        if not record.created_at:
            record.created_at = now
        key_records[chosen_name] = record

        payload: dict[str, Any] = {}
        for record_name, item in key_records.items():
            payload[record_name] = {
                "key_name": item.key_name,
                "provider": item.provider,
                "source": item.source,
                "project": item.project,
                "environment": item.environment,
                "notes": item.notes,
                "is_default": item.is_default,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
            }
        _save_registry(payload)
        return record


def _validate_and_maybe_generate_key_name(
    provider: str,
    key_name: str | None = None,
    source: str | None = None,
    project: str | None = None,
) -> str:
    _validate_provider(provider)
    if key_name:
        _validate_key_name(key_name)
        return key_name
    return suggest_key_name(provider=provider, source=source, project=project)


def delete_provider_secret(provider: str) -> None:
    _validate_provider(provider)
    with _registry_lock():
        registry = _load_registry()
        providers = []
        for key_name, entry in list(registry.items()):
            if isinstance(entry, dict) and str(entry.get("provider", "")) == provider:
                providers.append(key_name)
                delete_secret(key_name)
                registry.pop(key_name, None)
        if not providers:
            delete_secret(provider)
        _save_registry(registry)


def list_provider_states() -> list[VaultSecretState]:
    config_state = {"github", "openrouter", "local"}
    records = list_secret_records()
    for item in records:
        config_state.add(item.provider)
    states: list[VaultSecretState] = []
    for provider in sorted(config_state):
        alias_exists = has_secret(provider)
        resolved_alias = _resolve_provider_alias(provider) if not alias_exists else None
        states.append(VaultSecretState(provider=provider, available=alias_exists or bool(resolved_alias and has_secret(resolved_alias))))
    return states


def ensure_no_plaintext_fallback() -> None:
    # Explicitly fail closed when keychain is unavailable.
    from .keychain import is_available

    if not is_available():
        raise VaultError("Knox keychain backend unavailable. Configure macOS Keychain or disable v1 operations.")


def bootstrap_defaults() -> None:
    config.ensure_directory(config.KNOX_ROOT)
    if not config.KNOX_STATE_DB.exists():
        config.KNOX_STATE_DB.touch(exist_ok=True)
