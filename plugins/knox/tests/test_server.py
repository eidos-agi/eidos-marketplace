import json
from typing import Optional
from pathlib import Path

import pytest

from scripts.knox.session import SessionStore
from scripts.knox.server import KnoxMCPServer


def _call(server: KnoxMCPServer, method: str, **params):
    message = {
        "jsonrpc": "2.0",
        "id": "id",
        "method": method,
        "params": params,
    }
    response = server.handle(message)
    if "error" in response:
        raise AssertionError(response)
    content = response["result"]["content"][0]["text"]
    return json.loads(content)


def _tool_call(server: KnoxMCPServer, name: str, **arguments):
    message = {
        "jsonrpc": "2.0",
        "id": "id",
        "method": "tools/call",
        "params": {"name": name, "arguments": arguments},
    }
    response = server.handle(message)
    assert "error" not in response, response
    payload = json.loads(response["result"]["content"][0]["text"])
    assert response["result"]["isError"] is False
    return payload


def test_initialize_and_tools_list(tmp_path: Path):
    server = KnoxMCPServer(strict_keychain=False, store=SessionStore(tmp_path / "state.sqlite"))
    response = server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert response["result"]["protocolVersion"] == "2024-11-05"
    tools = server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})["result"]["tools"]
    names = {tool["name"] for tool in tools}
    assert "knox_issue_session" in names
    assert "knox_invoke" in names
    assert "knox_pairing_status" in names
    assert "knox_pair_device" in names
    assert "knox_store_secret" in names
    assert "knox_list_secrets" in names


def test_session_workflow_and_invoke(monkeypatch, tmp_path: Path):
    server = KnoxMCPServer(strict_keychain=False, store=SessionStore(tmp_path / "state.sqlite"))
    monkeypatch.setattr("scripts.knox.server.authorize_human", lambda reason: None)
    monkeypatch.setattr("scripts.knox.server.invoke_provider", lambda provider, operation, payload: {"success": True, "summary": f"{provider}:{operation}", "result": {"ok": True}})

    session_data = _tool_call(
        server,
        "knox_issue_session",
        ttl_minutes=15,
        request_label="ci",
        scopes=["github:list_repos"],
    )
    assert session_data["status"] == "issued"
    token = session_data["session_token"]

    status = _tool_call(server, "knox_session_status", session_token=token)
    assert status["active"] is True
    assert status["token"] == token

    invoke_ok = _tool_call(server, "knox_invoke", session_token=token, provider="github", operation="list_repos", payload={})
    assert invoke_ok["status"] == "ok"

    revoked = _tool_call(server, "knox_revoke_session", session_token=token)
    assert revoked["revoked"] is True

    response = _tool_call(server, "knox_session_status", session_token=token)
    assert response["active"] is False


def test_scope_gate_and_idempotency(monkeypatch, tmp_path: Path):
    server = KnoxMCPServer(strict_keychain=False, store=SessionStore(tmp_path / "state.sqlite"))
    monkeypatch_called = {}

    def fake_authorize(reason: str) -> None:
        monkeypatch_called["reason"] = reason

    def fake_invoke(provider: str, operation: str, payload: dict) -> dict:
        return {"success": True, "summary": "ok", "result": {"provider": provider, "operation": operation}}

    # this import path is inside the module under test
    import scripts.knox.server as srv

    monkeypatch.setattr(srv, "authorize_human", fake_authorize)
    monkeypatch.setattr(srv, "invoke_provider", fake_invoke)

    session_data = _tool_call(
        server,
        "knox_issue_session",
        ttl_minutes=15,
        request_label="scope",
        scopes=["github:list_repos"],
    )
    token = session_data["session_token"]

    # idempotent cache
    first = _tool_call(
        server,
        "knox_invoke",
        session_token=token,
        provider="github",
        operation="list_repos",
        payload={"foo": "bar"},
        idempotency_key="same-key",
    )
    second = _tool_call(
        server,
        "knox_invoke",
        session_token=token,
        provider="github",
        operation="list_repos",
        payload={"foo": "baz"},
        idempotency_key="same-key",
    )
    assert second["status"] == "replayed"
    assert second["result"] == {
        "provider": "github",
        "operation": "list_repos",
        "result_status": "ok",
        "risk": "low",
        "result": {"provider": "github", "operation": "list_repos"},
        "summary": "ok",
    }

    denied = server.handle(
        {
            "jsonrpc": "2.0",
            "id": "id",
            "method": "tools/call",
            "params": {
                "name": "knox_invoke",
                "arguments": {
                    "session_token": token,
                    "provider": "github",
                    "operation": "create_issue",
                    "payload": {"repo": "owner/repo", "title": "hello"},
                },
            },
        }
    )
    assert denied["error"]["code"] == -32001


def test_strict_startup_blocked_when_keychain_missing(monkeypatch):
    def fail():
        raise RuntimeError("keychain unavailable")

    monkeypatch.setattr("scripts.knox.server.ensure_no_plaintext_fallback", fail)
    with pytest.raises(RuntimeError):
        KnoxMCPServer(strict_keychain=True)


def test_pairing_status_and_setup_gate(monkeypatch, tmp_path: Path):
    from scripts.knox import config

    monkeypatch.setattr(config, "KNOX_PAIRING_PATH", tmp_path / "pairing.json")
    server = KnoxMCPServer(
        strict_keychain=False,
        store=SessionStore(tmp_path / "state.sqlite"),
        require_pairing=True,
    )

    status = _tool_call(server, "knox_pairing_status")
    assert status["paired"] is False
    assert status["pairing_required"] is True

    denied = server.handle(
        {
            "jsonrpc": "2.0",
            "id": "id",
            "method": "tools/call",
            "params": {
                "name": "knox_issue_session",
                "arguments": {
                    "ttl_minutes": 15,
                    "request_label": "no pair",
                    "scopes": ["github:list_repos"],
                },
            },
        }
    )
    assert denied["error"]["code"] == -32001
    assert "setup required" in denied["error"]["message"]


def test_pair_device_requires_challenge_and_unblocks_tools(monkeypatch, tmp_path: Path):
    from scripts.knox import config

    monkeypatch.setattr(config, "KNOX_PAIRING_PATH", tmp_path / "pairing.json")
    server = KnoxMCPServer(
        strict_keychain=False,
        store=SessionStore(tmp_path / "state.sqlite"),
        require_pairing=True,
    )
    import scripts.knox.server as srv

    delivered: dict[str, str] = {}

    def fake_deliver(code: str, request_label: str) -> None:
        delivered["code"] = code
        delivered["request_label"] = request_label

    monkeypatch.setattr(srv, "_deliver_challenge_code", fake_deliver)
    monkeypatch.setattr(srv, "authorize_human", lambda reason: None)

    challenge = _tool_call(
        server,
        "knox_pair_device",
        challenge_code_setup="123456",
    )
    assert challenge["status"] == "challenge_issued"
    token = challenge["challenge_token"]
    assert delivered == {}

    complete = _tool_call(
        server,
        "knox_pair_device",
        challenge_token=token,
        challenge_code="123456",
    )
    assert complete["status"] == "paired"

    pairing_status = _tool_call(server, "knox_pairing_status")
    assert pairing_status["paired"] is True

    issued = _tool_call(
        server,
        "knox_issue_session",
        ttl_minutes=15,
        request_label="paired-session",
        scopes=["github:list_repos"],
    )
    assert issued["status"] == "issued"


def test_pair_device_rejects_invalid_code(monkeypatch, tmp_path: Path):
    from scripts.knox import config

    monkeypatch.setattr(config, "KNOX_PAIRING_PATH", tmp_path / "pairing.json")
    server = KnoxMCPServer(
        strict_keychain=False,
        store=SessionStore(tmp_path / "state.sqlite"),
        require_pairing=True,
    )
    import scripts.knox.server as srv

    def fake_deliver(code: str, request_label: str) -> None:
        assert code == "123456"

    monkeypatch.setattr(srv, "_deliver_challenge_code", fake_deliver)

    challenge = _tool_call(
        server,
        "knox_pair_device",
        challenge_code_setup="123456",
    )
    invalid = server.handle(
        {
            "jsonrpc": "2.0",
            "id": "id",
            "method": "tools/call",
            "params": {
                "name": "knox_pair_device",
                "arguments": {
                    "challenge_token": challenge["challenge_token"],
                    "challenge_code": "654321",
                },
            },
        }
    )
    assert invalid["error"]["code"] == -32001


def test_audit_log_redacts_payload(monkeypatch, tmp_path: Path):
    from scripts.knox import audit, config
    from scripts.knox.server import log_event

    monkeypatch.setattr(config, "KNOX_AUDIT_PATH", tmp_path / "audit.log")
    log_event(
        "knox_invoke",
        {
            "provider": "github",
            "operation": "create_issue",
            "request_label": "audit",
            "payload": {"token": "super-secret"},
            "result_status": "ok",
        },
    )
    text = (tmp_path / "audit.log").read_text(encoding="utf-8")
    assert "super-secret" not in text
    assert "operation" in text
    first = json.loads((tmp_path / "audit.log").read_text(encoding="utf-8").splitlines()[0])
    assert "hash" in first
    assert "prev_hash" not in first

    log_event(
        "knox_session_status",
        {"provider": "github", "operation": "list_repos", "result_status": "ok"},
    )
    lines = (tmp_path / "audit.log").read_text(encoding="utf-8").splitlines()
    second = json.loads(lines[1])
    assert second["prev_hash"] == first["hash"]


def test_optional_challenge_flow(monkeypatch, tmp_path: Path):
    server = KnoxMCPServer(strict_keychain=False, store=SessionStore(tmp_path / "state.sqlite"))
    delivered = {}

    import scripts.knox.server as srv

    def fake_deliver(code: str, request_label: str) -> None:
        delivered["code"] = code
        delivered["request_label"] = request_label

    monkeypatch.setattr(srv, "_deliver_challenge_code", fake_deliver)

    challenge = _tool_call(
        server,
        "knox_issue_session",
        ttl_minutes=15,
        request_label="fallback",
        scopes=["github:list_repos"],
        challenge_compat_mode=True,
    )
    assert challenge["status"] == "challenge_issued"
    token = challenge["challenge_token"]
    assert "challenge_code" not in challenge
    code = delivered["code"]

    issued = _tool_call(
        server,
        "knox_issue_session",
        ttl_minutes=15,
        request_label="fallback-exchange",
        scopes=["github:list_repos"],
        challenge_token=token,
        challenge_code=code,
    )
    assert issued["status"] == "issued"


def test_manual_challenge_setup_and_redeem(monkeypatch, tmp_path: Path):
    server = KnoxMCPServer(strict_keychain=False, store=SessionStore(tmp_path / "state.sqlite"))
    delivered = {}

    import scripts.knox.server as srv

    def fake_deliver(code: str, request_label: str) -> None:
        delivered["code"] = code
        delivered["request_label"] = request_label

    monkeypatch.setattr(srv, "_deliver_challenge_code", fake_deliver)

    challenge = _tool_call(
        server,
        "knox_issue_session",
        ttl_minutes=15,
        request_label="manual-code",
        scopes=["github:list_repos"],
        challenge_compat_mode=True,
        challenge_code_setup="123456",
    )
    assert challenge["status"] == "challenge_issued"
    assert "challenge_token" in challenge
    assert "challenge_code" not in challenge
    assert delivered == {}

    issued = _tool_call(
        server,
        "knox_issue_session",
        ttl_minutes=15,
        request_label="manual-code-exchange",
        scopes=["github:list_repos"],
        challenge_token=challenge["challenge_token"],
        challenge_code="123456",
    )
    assert issued["status"] == "issued"
    assert "session_token" in issued


def test_manual_challenge_code_validation(monkeypatch, tmp_path: Path):
    server = KnoxMCPServer(strict_keychain=False, store=SessionStore(tmp_path / "state.sqlite"))
    response = server.handle(
        {
            "jsonrpc": "2.0",
            "id": "id",
            "method": "tools/call",
            "params": {
                "name": "knox_issue_session",
                "arguments": {
                    "ttl_minutes": 15,
                    "request_label": "bad-code",
                    "scopes": ["github:list_repos"],
                    "challenge_compat_mode": True,
                    "challenge_code_setup": "12ab56",
                },
            },
        }
    )
    assert response["error"]["code"] == -32602


def test_invoke_does_not_echo_payload(monkeypatch, tmp_path: Path):
    server = KnoxMCPServer(strict_keychain=False, store=SessionStore(tmp_path / "state.sqlite"))
    monkeypatch_called = {"value": False}

    def fake_authorize(reason: str) -> None:
        monkeypatch_called["value"] = True

    import scripts.knox.server as srv

    monkeypatch.setattr(srv, "authorize_human", fake_authorize)

    session_data = _tool_call(
        server,
        "knox_issue_session",
        ttl_minutes=15,
        request_label="x",
        scopes=["local:echo"],
    )
    assert monkeypatch_called["value"]
    token = session_data["session_token"]

    out = _tool_call(
        server,
        "knox_invoke",
        session_token=token,
        provider="local",
        operation="echo",
        payload={"api_key": "abc123", "prompt": "hello"},
    )
    dumped = json.dumps(out)
    assert "api_key" not in dumped
    assert out["status"] == "ok"


def test_proxy_token_workflow(monkeypatch, tmp_path: Path):
    server = KnoxMCPServer(strict_keychain=False, store=SessionStore(tmp_path / "state.sqlite"))
    monkeypatch.setattr("scripts.knox.server.authorize_human", lambda reason: None)

    captured: dict[str, Optional[str]] = {}

    def fake_invoke(provider: str, operation: str, payload: dict, secret_alias: Optional[str] = None) -> dict[str, str]:
        captured["secret_alias"] = secret_alias
        return {"success": True, "summary": f"{provider}:{operation}", "result": {"provider": provider, "operation": operation}}

    import scripts.knox.server as srv
    monkeypatch.setattr(srv, "invoke_provider", fake_invoke)

    proxy = _tool_call(
        server,
        "knox_issue_proxy_token",
        agent_id="agent-test",
        ttl_minutes=15,
        request_label="agent session",
        scopes=["github:list_repos"],
        secret_bindings={"github": "github-ci-key"},
    )
    assert proxy["status"] == "issued"
    assert proxy["proxy_token"]

    out = _tool_call(
        server,
        "knox_invoke",
        proxy_token=proxy["proxy_token"],
        provider="github",
        operation="list_repos",
        payload={},
    )
    assert out["status"] == "ok"
    assert out["summary"] == "github:list_repos"
    assert captured["secret_alias"] == "github-ci-key"

    status = _tool_call(server, "knox_proxy_token_status", proxy_token=proxy["proxy_token"])
    assert status["active"] is True

    revoked = _tool_call(server, "knox_revoke_proxy_token", proxy_token=proxy["proxy_token"])
    assert revoked["revoked"] is True

    response = server.handle(
        {
            "jsonrpc": "2.0",
            "id": "id",
            "method": "tools/call",
            "params": {
                "name": "knox_invoke",
                "arguments": {
                    "proxy_token": proxy["proxy_token"],
                    "provider": "github",
                    "operation": "list_repos",
                    "payload": {},
                },
            },
        }
    )
    assert response["error"]["code"] == -32001


def test_store_secret_supports_suggest_and_store(monkeypatch, tmp_path: Path):
    from scripts.knox import vault as vault_module

    secrets_store: dict[str, str] = {}

    monkeypatch.setattr(vault_module, "store_secret", lambda name, secret: secrets_store.__setitem__(name, secret))
    monkeypatch.setattr(vault_module, "has_secret", lambda name: name in secrets_store)
    monkeypatch.setattr(vault_module, "read_secret", lambda name: secrets_store[name])
    monkeypatch.setattr(vault_module.config, "KNOX_REGISTRY_PATH", tmp_path / "registry.json")

    server = KnoxMCPServer(strict_keychain=False, store=SessionStore(tmp_path / "state.sqlite"))

    suggested = _tool_call(
        server,
        "knox_store_secret",
        provider="github",
        source="GitHub Actions",
        project="alpha",
        environment="staging",
        dry_run=True,
    )
    assert suggested["status"] == "name_suggested"
    assert suggested["suggested_key_name"].startswith("github-github-actions")

    monkeypatch.setattr("scripts.knox.server.authorize_human", lambda reason: None)
    store_session = _tool_call(
        server,
        "knox_issue_session",
        ttl_minutes=15,
        request_label="store",
        scopes=["knox:store_secret"],
    )

    stored = _tool_call(
        server,
        "knox_store_secret",
        session_token=store_session["session_token"],
        provider="github",
        secret="abc",
        source="GitHub Actions",
        project="alpha",
        environment="staging",
        notes="ci key",
    )
    assert stored["status"] == "stored"
    assert stored["provider"] == "github"
    assert stored["is_default"] is True
    assert stored["metadata"]["source"] == "GitHub Actions"
    assert stored["metadata"]["environment"] == "staging"

    list_session = _tool_call(
        server,
        "knox_issue_session",
        ttl_minutes=15,
        request_label="list",
        scopes=["knox:list_secrets"],
    )
    records = _tool_call(server, "knox_list_secrets", session_token=list_session["session_token"], provider="github")
    assert records["count"] == 1
    assert records["secrets"][0]["notes"] == "ci key"


def test_store_and_list_require_scoped_sessions(monkeypatch, tmp_path: Path):
    from scripts.knox import vault as vault_module

    monkeypatch.setattr(vault_module.config, "KNOX_REGISTRY_PATH", tmp_path / "registry.json")
    monkeypatch.setattr("scripts.knox.server.authorize_human", lambda reason: None)
    server = KnoxMCPServer(strict_keychain=False, store=SessionStore(tmp_path / "state.sqlite"))

    denied_store = server.handle(
        {
            "jsonrpc": "2.0",
            "id": "id",
            "method": "tools/call",
            "params": {
                "name": "knox_store_secret",
                "arguments": {"provider": "github", "secret": "abc"},
            },
        }
    )
    assert denied_store["error"]["code"] == -32001

    wrong_session = _tool_call(
        server,
        "knox_issue_session",
        ttl_minutes=15,
        request_label="wrong",
        scopes=["github:list_repos"],
    )
    denied_list = server.handle(
        {
            "jsonrpc": "2.0",
            "id": "id",
            "method": "tools/call",
            "params": {
                "name": "knox_list_secrets",
                "arguments": {"session_token": wrong_session["session_token"]},
            },
        }
    )
    assert denied_list["error"]["code"] == -32001
