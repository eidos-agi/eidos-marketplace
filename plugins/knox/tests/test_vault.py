import pytest
import stat

from scripts.knox import vault


def test_provider_name_validation():
    with pytest.raises(vault.VaultError):
        vault.read_provider_secret("bad/provider")


def test_fail_closed_when_keychain_unavailable(monkeypatch):
    def unavailable():
        return False

    monkeypatch.setattr("scripts.knox.keychain.is_available", unavailable)
    with pytest.raises(vault.VaultError):
        vault.ensure_no_plaintext_fallback()


def test_suggest_key_name_includes_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(vault.config, "KNOX_REGISTRY_PATH", tmp_path / "registry.json")
    suggestion = vault.suggest_key_name("github", source="GitHub Actions")
    assert suggestion.startswith("github-github-actions")


def test_register_and_list_secret_metadata(tmp_path, monkeypatch):
    store: dict[str, str] = {}

    monkeypatch.setattr(vault, "store_secret", lambda name, secret: store.__setitem__(name, secret))
    monkeypatch.setattr(vault, "has_secret", lambda name: name in store)
    monkeypatch.setattr(vault, "read_secret", lambda name: store[name])
    monkeypatch.setattr(vault.config, "KNOX_REGISTRY_PATH", tmp_path / "registry.json")

    record = vault.register_provider_secret(
        provider="github",
        secret="abc",
        source="My App",
        project="cli",
        environment="prod",
        notes="rotating key",
    )

    assert record.provider == "github"
    assert record.key_name
    assert record.source == "My App"
    assert record.project == "cli"
    assert record.environment == "prod"
    assert record.notes == "rotating key"

    records = vault.list_secret_records("github")
    assert len(records) == 1
    assert records[0].key_name == record.key_name
    assert vault.read_provider_secret("github") == "abc"
    registry_text = (tmp_path / "registry.json").read_text(encoding="utf-8")
    assert "abc" not in registry_text
    assert stat.S_IMODE((tmp_path / "registry.json").stat().st_mode) == 0o600


def test_overwrite_does_not_delete_old_secret_before_store(tmp_path, monkeypatch):
    store: dict[str, str] = {"github-my-app": "old"}
    deleted = {"called": False}

    monkeypatch.setattr(vault, "store_secret", lambda name, secret: store.__setitem__(name, secret))
    monkeypatch.setattr(vault, "has_secret", lambda name: name in store)
    monkeypatch.setattr(vault, "read_secret", lambda name: store[name])
    monkeypatch.setattr(vault, "delete_secret", lambda name: deleted.__setitem__("called", True))
    monkeypatch.setattr(vault.config, "KNOX_REGISTRY_PATH", tmp_path / "registry.json")

    vault.register_provider_secret(
        provider="github",
        secret="new",
        key_name="github-my-app",
        source="My App",
        overwrite=True,
    )

    assert deleted["called"] is False
    assert store["github-my-app"] == "new"


def test_corrupt_registry_fails_closed(tmp_path, monkeypatch):
    registry = tmp_path / "registry.json"
    registry.write_text("{not-json", encoding="utf-8")
    monkeypatch.setattr(vault.config, "KNOX_REGISTRY_PATH", registry)

    with pytest.raises(vault.VaultError):
        vault.list_secret_records()
