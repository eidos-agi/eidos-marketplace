from __future__ import annotations

import json
import os
import platform
import secrets
import subprocess
import sys
import inspect
import re
import tempfile
import time
from dataclasses import dataclass
from typing import Any

from .adapters import AdapterError, invoke as invoke_provider
from .audit import log_event
from . import config
from .keychain import KnoxKeychainError, authorize_human, challenge_code
from .approval import ApprovalController
from .policy import OperationPolicy, is_operation_allowed, load_policy, operation_policy
from .session import ALLOWED_TTLS, ProxyToken, Session, SessionStore
from .vault import VaultError
from .vault import list_secret_records, register_provider_secret, suggest_key_name
from .vault import ensure_no_plaintext_fallback


DEFAULT_SERVER_NAME = "knox"
DEFAULT_SERVER_VERSION = "0.2.0"


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    inputSchema: dict[str, Any]


def _build_tools() -> list[Tool]:
    return [
        Tool(
            name="knox_issue_session",
            description=(
                "Create a short-lived action session (15/60/180 minutes) for gated provider operations."
                " Uses local approval by default; use challenge_compat_mode for code fallback."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "ttl_minutes": {"type": "integer", "enum": sorted(ALLOWED_TTLS)},
                    "scopes": {"type": "array", "items": {"type": "string"}},
                    "request_label": {"type": "string"},
                    "client_hint": {"type": "string"},
                    "approval_required_approvals": {"type": "integer", "minimum": 1},
                    "secret_bindings": {"type": "object"},
                    "challenge_token": {"type": "string"},
                    "challenge_code": {"type": "string"},
                    "challenge_code_setup": {"type": "string", "pattern": "^\\d{6}$"},
                    "challenge_compat_mode": {"type": "boolean"},
                },
                "required": ["ttl_minutes", "scopes", "request_label"],
            },
        ),
        Tool(
            name="knox_issue_proxy_token",
            description=(
                "Create a proxy token (pxr-style) bound to per-tool scopes and optional key aliases."
                " Use for agent-first workflows where tools receive only a short-lived proxy token."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string"},
                    "ttl_minutes": {"type": "integer", "enum": sorted(ALLOWED_TTLS)},
                    "scopes": {"type": "array", "items": {"type": "string"}},
                    "request_label": {"type": "string"},
                    "client_hint": {"type": "string"},
                    "approval_required_approvals": {"type": "integer", "minimum": 1},
                    "secret_bindings": {"type": "object"},
                    "challenge_token": {"type": "string"},
                    "challenge_code": {"type": "string"},
                    "challenge_code_setup": {"type": "string", "pattern": "^\\d{6}$"},
                    "challenge_compat_mode": {"type": "boolean"},
                },
                "required": ["agent_id", "ttl_minutes", "scopes", "request_label"],
            },
        ),
        Tool(
            name="knox_revoke_proxy_token",
            description="Revoke a proxy token immediately.",
            inputSchema={
                "type": "object",
                "properties": {"proxy_token": {"type": "string"}},
                "required": ["proxy_token"],
            },
        ),
        Tool(
            name="knox_proxy_token_status",
            description="Check the state of one proxy token.",
            inputSchema={
                "type": "object",
                "properties": {"proxy_token": {"type": "string"}},
            },
        ),
        Tool(
            name="knox_pairing_status",
            description="Check setup state and what to do next.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="knox_pair_device",
            description=(
                "Start pairing by calling without challenge fields to get a local 6-digit code."
                " Then call again with challenge_token + challenge_code to complete setup."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "challenge_token": {"type": "string"},
                    "challenge_code": {"type": "string"},
                    "challenge_code_setup": {"type": "string", "pattern": "^\\d{6}$"},
                    "force_reset": {"type": "boolean"},
                },
            },
        ),
        Tool(
            name="knox_revoke_session",
            description="Revoke a session token immediately.",
            inputSchema={
                "type": "object",
                "properties": {"session_token": {"type": "string"}},
                "required": ["session_token"],
            },
        ),
        Tool(
            name="knox_session_status",
            description="Check the state of one session token.",
            inputSchema={
                "type": "object",
                "properties": {"session_token": {"type": "string"}},
            },
        ),
        Tool(
            name="knox_invoke",
            description="Execute an allowed provider operation using an active session token.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_token": {"type": "string"},
                    "proxy_token": {"type": "string"},
                    "provider": {"type": "string"},
                    "operation": {"type": "string"},
                    "payload": {"type": "object"},
                    "idempotency_key": {"type": "string"},
                },
                "required": ["provider", "operation", "payload"],
            },
        ),
        Tool(
            name="knox_store_secret",
            description="Store a new secret in Keychain with metadata about where it came from.",
            inputSchema={
                "type": "object",
                "properties": {
                    "provider": {"type": "string"},
                    "secret": {"type": "string"},
                    "session_token": {"type": "string"},
                    "source": {"type": "string"},
                    "project": {"type": "string"},
                    "environment": {"type": "string"},
                    "notes": {"type": "string"},
                    "key_name": {"type": "string"},
                    "overwrite": {"type": "boolean"},
                    "dry_run": {"type": "boolean"},
                },
                "required": ["provider"],
            },
        ),
        Tool(
            name="knox_list_secrets",
            description="List secret metadata records without returning secret values.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_token": {"type": "string"},
                    "provider": {"type": "string"},
                },
                "required": ["session_token"],
            },
        ),
    ]


KNOWN_TOOLS: list[dict[str, Any]] = [tool.__dict__ for tool in _build_tools()]


class KnoxError(RuntimeError):
    pass


class KnoxBadRequest(KnoxError):
    pass


class KnoxUnauthorized(KnoxError):
    pass


class KnoxSetupRequired(KnoxUnauthorized):
    def __init__(self, message: str, tool: str):
        super().__init__(message)
        self.tool = tool


def _jsonrpc_error(id_value: object | None, code: int, message: str, data: str | dict[str, Any] | None = None) -> dict[str, Any]:
    response: dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": id_value,
        "error": {"code": code, "message": message},
    }
    if data is not None:
        response["error"]["data"] = data
    return response


def _jsonrpc_success(id_value: object | None, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": id_value, "result": result}


def _tool_result(content: dict[str, Any], is_error: bool = False) -> dict[str, Any]:
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(content, sort_keys=True, default=str),
            }
        ],
        "isError": is_error,
    }


def _scope_authorized(scope_tokens: list[str], provider: str, operation: str) -> bool:
    requested = f"{provider}:{operation}"
    return (
        requested in scope_tokens
        or f"{provider}:*" in scope_tokens
        or f"*:{operation}" in scope_tokens
        or "*" in scope_tokens
    )


def _deliver_challenge_code(code: str, request_label: str) -> None:
    if platform.system() == "Darwin":
        script = (
            'display dialog "Knox approval code request\n\nRequest: '
            + request_label
            + '\\n\\nCode: '
            + code
            + '\\n\\nUse this code in the matching knox_pair_device / knox_issue_* command." with title "Knox" buttons {"Copy in MCP"} default button "Copy in MCP"'
        )
        proc = subprocess.run(["/usr/bin/osascript"], input=script, capture_output=True, text=True, check=False)
        if proc.returncode == 0:
            return
    raise KnoxUnauthorized("challenge code could not be delivered through a local approval channel")


def _escape_applescript_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _approval_prompt_lines(request_label: str, ttl_minutes: int, scopes: list[str], request_type: str) -> list[str]:
    return [
        f"Knox {request_type} request",
        f"Request: {request_label}",
        f"TTL: {ttl_minutes} minutes",
        "Scopes: " + (", ".join(scopes) if scopes else "none"),
    ]


def _approve_on_macos(request_label: str, ttl_minutes: int, scopes: list[str], request_type: str) -> bool:
    if platform.system() != "Darwin":
        return True

    prompt = "\\n".join(_approval_prompt_lines(request_label, ttl_minutes, scopes, request_type))
    script = (
        'set user_choice to button returned of ('
        'display dialog "'
        + _escape_applescript_string(prompt)
        + '" with title "Knox Approval" buttons {"Deny", "Approve"} default button "Approve" cancel button "Deny")'
        '\n'
        'return user_choice'
    )
    proc = subprocess.run(["/usr/bin/osascript"], input=script, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise KnoxUnauthorized("approval cancelled or unavailable")
    return "button returned:Approve" in proc.stdout


def _normalize_challenge_code(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise KnoxBadRequest("challenge code must be a 6-digit string")
    if not re.fullmatch(r"^\d{6}$", value):
        raise KnoxBadRequest("challenge code must be exactly 6 digits")
    return value


def _pairing_status_payload(paired: bool, pairing_required: bool) -> dict[str, Any]:
    if paired:
        return {
            "paired": True,
            "pairing_required": pairing_required,
            "status": "paired",
            "next_step": "pairing complete",
        }
    return {
        "paired": False,
        "pairing_required": pairing_required,
        "status": "not_paired",
        "message": "run knox_pair_device to complete setup",
        "next_step": "call knox_pair_device to request a 6-digit setup code",
    }


def _pairing_setup_error_data(tool_name: str) -> dict[str, Any]:
    return {
        "reason": "setup_required",
        "tool": tool_name,
        "pairing_required": True,
        "next_step": "call knox_pairing_status, then knox_pair_device",
    }


class KnoxMCPServer:
    def __init__(
        self,
        strict_keychain: bool = True,
        store: SessionStore | None = None,
        policy: dict[str, Any] | None = None,
        *,
        code_only_approval: bool | None = None,
        require_pairing: bool | None = None,
        approval_mode: str | None = None,
    ):
        self.policy = policy or load_policy()
        if strict_keychain:
            ensure_no_plaintext_fallback()
        self.store = store or SessionStore()
        if code_only_approval is None:
            env_preference = os.getenv("KNOX_CODE_ONLY_APPROVAL", "").strip().lower()
            self.code_only_approval = env_preference in {"1", "true", "yes", "on"}
        else:
            self.code_only_approval = code_only_approval
        # Backward compatibility: explicit code-only mode always forces challenge mode.
        if self.code_only_approval:
            approval_mode = "code"
        if require_pairing is None:
            env_preference = os.getenv("KNOX_REQUIRE_PAIRING", "").strip().lower()
            self.require_pairing = env_preference in {"1", "true", "yes", "on"}
        else:
            self.require_pairing = require_pairing
        self.strict_keychain = strict_keychain
        timeout = int(os.getenv("KNOX_APPROVAL_TIMEOUT_SECONDS", "90") or 90)
        try:
            self.approval_required_approvals = max(1, int(os.getenv("KNOX_APPROVAL_REQUIRED_APPROVALS", "1") or 1))
        except ValueError:
            self.approval_required_approvals = 1
        if approval_mode is None:
            env_mode = os.getenv("KNOX_APPROVAL_MODE", "").strip().lower()
            self.approval_mode = ApprovalController.normalize_mode(env_mode, fallback_code=False)
        else:
            self.approval_mode = ApprovalController.normalize_mode(approval_mode, fallback_code=False)
        if self.approval_mode not in {"code", "tray", "hybrid", "biometric", "mobile"}:
            raise KnoxError(f"unsupported approval mode: {self.approval_mode}")
        self.approval = ApprovalController(self.approval_mode, timeout_seconds=timeout)
        self.approval.start()
        self.approval.set_pairing_state(self._is_paired(), self.require_pairing)

    def finalize(self) -> None:
        self.approval.stop()

    def _pairing_state_defaults(self) -> dict[str, Any]:
        return {
            "paired": False,
            "paired_at": None,
            "pairing_version": 1,
        }

    def _read_pairing_state(self) -> dict[str, Any]:
        state = config.load_json_file(config.KNOX_PAIRING_PATH, self._pairing_state_defaults())
        if not isinstance(state, dict):
            return self._pairing_state_defaults()
        paired = bool(state.get("paired", False))
        paired_at = state.get("paired_at")
        if paired_at is not None and not isinstance(paired_at, int):
            paired_at = None
        return {"paired": paired, "paired_at": paired_at, "pairing_version": int(state.get("pairing_version", 1))}

    def _write_pairing_state(self, state: dict[str, Any]) -> None:
        config.ensure_directory(config.KNOX_PAIRING_PATH.parent)
        normalized = {
            "paired": bool(state.get("paired", False)),
            "paired_at": state.get("paired_at"),
            "pairing_version": int(state.get("pairing_version", 1)),
        }
        payload = json.dumps(normalized, sort_keys=True).encode("utf-8")
        with tempfile.NamedTemporaryFile("wb", dir=config.KNOX_PAIRING_PATH.parent, delete=False) as handle:
            handle.write(payload)
            temp_path = handle.name
        os.replace(temp_path, config.KNOX_PAIRING_PATH)
        os.chmod(config.KNOX_PAIRING_PATH, 0o600)

    def _is_paired(self) -> bool:
        return bool(self._read_pairing_state().get("paired"))

    def _set_paired(self, paired: bool) -> None:
        state = self._pairing_state_defaults()
        if paired:
            state["paired"] = True
            state["paired_at"] = int(time.time())
        self._write_pairing_state(state)
        self.approval.set_pairing_state(paired, self.require_pairing)

    def _require_pairing(self, tool_name: str) -> None:
        if not self.require_pairing:
            return
        if self._is_paired():
            return
        if tool_name in {"knox_pairing_status", "knox_pair_device"}:
            return
        raise KnoxSetupRequired(
            "setup required. this Knox instance is not paired yet. run knox_pair_device with a 6-digit flow first.",
            tool_name,
        )

    def _issue_challenge(
        self,
        request_label: str,
        ttl_minutes: int,
        scopes: list[str],
        client_hint: str | None,
        challenge_code_setup: str | None,
    ) -> dict[str, Any]:
        code = challenge_code_setup or challenge_code()
        token = secrets.token_urlsafe(16)
        self.store.create_challenge(
            challenge_token=token,
            code=code,
            request_label=request_label,
            scopes=scopes,
            ttl_minutes=ttl_minutes,
            client_hint=client_hint,
            ttl_seconds=300,
        )
        if challenge_code_setup is None:
            _deliver_challenge_code(code, request_label)
        return {
            "status": "challenge_issued",
            "challenge_token": token,
            "challenge_ttl_seconds": 300,
            "message": "challenge issued; enter the 6-digit code in knox_issue_session or knox_issue_proxy_token",
            "next_step": "call same tool with challenge_token and challenge_code to complete",
        }

    def _issue_pairing_challenge(
        self,
        challenge_code_setup: str | None,
        force_reset: bool = False,
    ) -> dict[str, Any]:
        if force_reset:
            self._set_paired(False)
        return self._issue_challenge(
            request_label="Knox pairing setup",
            ttl_minutes=15,
            scopes=["knox:pair"],
            client_hint="setup-mode",
            challenge_code_setup=challenge_code_setup,
        )

    def _request_human_approval(
        self,
        request_type: str,
        request_label: str,
        ttl_minutes: int,
        scopes: list[str],
        client_hint: str | None,
        required_approvals: int,
    ) -> tuple[bool, dict[str, Any]]:
        if self.approval_mode == "code":
            return False, self._issue_challenge(request_label, ttl_minutes, scopes, client_hint, None)

        if self.approval_mode == "tray":
            request, code = self.approval.create_request(
                request_type,
                request_label,
                ttl_minutes,
                scopes,
                client_hint,
                required_approvals=required_approvals,
            )
            log_event(
                "approval_requested",
                {
                    "request_type": request_type,
                    "request_label": request_label,
                    "request_id": request.request_id,
                    "result_status": "pending",
                },
            )
            decision = self.approval.wait_for_decision(request)
            if decision.approved:
                return True, {
                    "status": "approved",
                    "request_id": request.request_id,
                    "request_type": request_type,
                    "state": "approved",
                    "approval_mode": "tray",
                    "code": code,
                }
            if decision.state == "denied":
                return False, {"status": "denied", "request_id": request.request_id, "reason": "user denied"}
            return False, {
                "status": "expired",
                "request_id": request.request_id,
                "approval_mode": "tray",
                "reason": "approval timeout",
            }

        if self.approval_mode == "hybrid":
            request, code = self.approval.create_request(
                request_type,
                request_label,
                ttl_minutes,
                scopes,
                client_hint,
                required_approvals=required_approvals,
            )
            log_event(
                "approval_requested",
                {
                    "request_type": request_type,
                    "request_label": request_label,
                    "request_id": request.request_id,
                    "result_status": "pending",
                },
            )
            decision = self.approval.wait_for_decision(request)
            if decision.approved:
                return True, {
                    "status": "approved",
                    "request_id": request.request_id,
                    "request_type": request_type,
                    "approval_mode": "hybrid",
                    "state": "approved",
                    "code": code,
                }
            if decision.state == "denied":
                return False, {"status": "denied", "request_id": request.request_id, "reason": "user denied"}
            fallback = self._issue_challenge(request_label, ttl_minutes, scopes, client_hint, None)
            fallback["approval_request_id"] = request.request_id
            fallback["approval_mode"] = "hybrid"
            return False, fallback

        if self.approval_mode == "mobile":
            request, code = self.approval.create_request(
                request_type,
                request_label,
                ttl_minutes,
                scopes,
                client_hint,
                required_approvals=required_approvals,
            )
            log_event(
                "approval_requested",
                {
                    "request_type": request_type,
                    "request_label": request_label,
                    "request_id": request.request_id,
                    "result_status": "pending",
                    "approval_mode": "mobile",
                    "required_approvals": request.required_approvals,
                },
            )
            decision = self.approval.wait_for_decision(request)
            if decision.approved:
                return True, {
                    "status": "approved",
                    "request_id": request.request_id,
                    "request_type": request_type,
                    "approval_mode": "mobile",
                    "state": "approved",
                    "code": code,
                }
            if decision.state == "denied":
                return False, {"status": "denied", "request_id": request.request_id, "reason": "user denied"}

            return False, {
                "status": "expired",
                "request_id": request.request_id,
                "approval_mode": "mobile",
                "reason": "approval timeout",
            }

        # Biometric path remains available for compatibility, not default.
        _approve_on_macos(request_label, ttl_minutes, scopes, request_type)
        try:
            authorize_human(f"Approve Knox {request_type} request: {request_label}")
        except KnoxKeychainError as exc:
            log_event(
                "approval_fallback_to_code",
                {
                    "request_type": request_type,
                    "request_label": request_label,
                    "result_status": "fallback-to-code",
                },
            )
            return False, self._issue_challenge(request_label, ttl_minutes, scopes, client_hint, None)
        except KnoxUnauthorized:
            raise
        return True, {
            "status": "approved",
            "request_type": request_type,
            "approval_mode": "biometric",
            "state": "approved",
        }

    def pairing_status(self, _arguments: dict[str, Any]) -> dict[str, Any]:
        state = self._read_pairing_state()
        status = _pairing_status_payload(bool(state.get("paired")), self.require_pairing)
        if state.get("paired"):
            status["paired_at"] = state.get("paired_at")
        return status

    def pair_device(self, arguments: dict[str, Any]) -> dict[str, Any]:
        challenge_token = arguments.get("challenge_token")
        challenge_code_value = arguments.get("challenge_code")
        force_reset = bool(arguments.get("force_reset", False))

        if challenge_token is None and challenge_code_value is None and self._is_paired() and not force_reset:
            return {
                "status": "already_paired",
                "paired": True,
                "paired_at": self._read_pairing_state().get("paired_at"),
                "message": "already paired; no action required",
                "next_step": "continue with session/proxy operations",
            }

        challenge_code_setup = _normalize_challenge_code(arguments.get("challenge_code_setup"))
        if challenge_token or challenge_code_value:
            if challenge_code_setup is not None:
                raise KnoxBadRequest("challenge_code_setup cannot be used with challenge_token/challenge_code")
            if not (challenge_token and challenge_code_value and isinstance(challenge_token, str) and isinstance(challenge_code_value, str)):
                raise KnoxBadRequest("challenge_token and challenge_code must be provided together")
            pending = self.store.verify_challenge(challenge_token, challenge_code_value)
            if pending is None or "knox:pair" not in pending.scopes:
                raise KnoxUnauthorized("pairing challenge invalid or expired")
            self._set_paired(True)
            log_event(
                "pairing_completed",
                {
                    "request_label": pending.request_label,
                    "client_hint": pending.client_hint,
                    "result_status": "paired",
                },
            )
            return {
                "status": "paired",
                "paired": True,
                "paired_at": self._read_pairing_state().get("paired_at"),
                "message": "pairing complete",
                "next_step": "retry your previous Knox request",
            }

        return self._issue_pairing_challenge(challenge_code_setup=challenge_code_setup, force_reset=force_reset)

    def handle(self, request: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(request, dict):
            return _jsonrpc_error(None, -32600, "Invalid JSON-RPC request")

        method = request.get("method")
        request_id = request.get("id")
        if not isinstance(method, str):
            return _jsonrpc_error(request_id, -32600, "Missing method")

        params = request.get("params")
        params = params if isinstance(params, dict) else {}

        if method == "initialize":
            return self._handle_initialize(request_id, params)
        if method == "tools/list":
            return self._handle_tools_list(request_id, params)
        if method == "tools/call":
            return self._handle_tool_call(request_id, params)

        return _jsonrpc_error(request_id, -32601, f"Method not found: {method}")

    def _handle_initialize(self, request_id: object | None, params: dict[str, Any]) -> dict[str, Any]:
        del params
        return _jsonrpc_success(
            request_id,
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {
                    "name": DEFAULT_SERVER_NAME,
                    "version": DEFAULT_SERVER_VERSION,
                    "description": "Knox local MCP secret broker with session-scoped capability grants.",
                },
            },
        )

    def _handle_tools_list(self, request_id: object | None, _params: dict[str, Any]) -> dict[str, Any]:
        return _jsonrpc_success(request_id, {"tools": KNOWN_TOOLS})

    def _handle_tool_call(self, request_id: object | None, params: dict[str, Any]) -> dict[str, Any]:
        name = params.get("name")
        arguments = params.get("arguments")
        if not isinstance(name, str):
            return _jsonrpc_error(request_id, -32602, "tool name required")
        if not isinstance(arguments, dict):
            return _jsonrpc_error(request_id, -32602, "tool arguments required")

        try:
            if name == "knox_pairing_status":
                result = self.pairing_status(arguments)
            elif name == "knox_pair_device":
                result = self.pair_device(arguments)
            else:
                self._require_pairing(name)
                if name == "knox_issue_session":
                    result = self.issue_session(arguments)
                elif name == "knox_issue_proxy_token":
                    result = self.issue_proxy_token(arguments)
                elif name == "knox_revoke_proxy_token":
                    result = self.revoke_proxy_token(arguments)
                elif name == "knox_proxy_token_status":
                    result = self.proxy_token_status(arguments)
                elif name == "knox_revoke_session":
                    result = self.revoke_session(arguments)
                elif name == "knox_session_status":
                    result = self.session_status(arguments)
                elif name == "knox_invoke":
                    result = self.invoke(arguments)
                elif name == "knox_store_secret":
                    result = self.store_secret(arguments)
                elif name == "knox_list_secrets":
                    result = self.list_secrets(arguments)
                else:
                    return _jsonrpc_error(request_id, -32602, f"unknown tool: {name}")
        except KnoxBadRequest as exc:
            return _jsonrpc_error(request_id, -32602, str(exc))
        except KnoxSetupRequired as exc:
            return _jsonrpc_error(request_id, -32001, str(exc), _pairing_setup_error_data(exc.tool))
        except KnoxUnauthorized as exc:
            return _jsonrpc_error(request_id, -32001, str(exc))
        except VaultError as exc:
            return _jsonrpc_error(request_id, -32000, str(exc))
        except KnoxError as exc:
            return _jsonrpc_error(request_id, -32000, str(exc))

        return _jsonrpc_success(request_id, _tool_result(result))

    def issue_session(self, arguments: dict[str, Any]) -> dict[str, Any]:
        ttl_minutes = arguments.get("ttl_minutes")
        scopes = arguments.get("scopes")
        request_label = arguments.get("request_label")
        client_hint = arguments.get("client_hint")
        secret_bindings = self._normalize_secret_bindings(arguments.get("secret_bindings"))
        approval_required_approvals = self._normalize_required_approvals(arguments.get("approval_required_approvals"))
        challenge_token = arguments.get("challenge_token")
        challenge_code_value = arguments.get("challenge_code")
        challenge_compat_mode = bool(arguments.get("challenge_compat_mode", False))

        if not isinstance(ttl_minutes, int):
            raise KnoxBadRequest("ttl_minutes is required and must be an integer")
        if ttl_minutes not in ALLOWED_TTLS:
            raise KnoxBadRequest("ttl_minutes must be one of 15, 60, 180")
        if not request_label or not isinstance(request_label, str):
            raise KnoxBadRequest("request_label is required")
        if not isinstance(scopes, list) or not scopes:
            raise KnoxBadRequest("scopes must be a non-empty list")
        if not all(isinstance(item, str) and item for item in scopes):
            raise KnoxBadRequest("each scope must be a non-empty string")

        scopes = self._normalize_scopes(scopes)
        challenge_code_setup = _normalize_challenge_code(arguments.get("challenge_code_setup"))
        if challenge_token or challenge_code_value:
            if challenge_code_setup is not None:
                raise KnoxBadRequest("challenge_code_setup cannot be used with challenge_token/challenge_code")
            if not (challenge_token and challenge_code_value and isinstance(challenge_token, str) and isinstance(challenge_code_value, str)):
                raise KnoxBadRequest("challenge_token and challenge_code must be provided together")
            pending = self.store.verify_challenge(challenge_token, challenge_code_value)
            if pending is None:
                raise KnoxUnauthorized("challenge invalid or expired")
            session = self.store.issue_session(
                scopes=pending.scopes or scopes,
                ttl_minutes=pending.ttl_minutes,
                request_label=f"{request_label} (challenge)",
                client_hint=client_hint or pending.client_hint,
                key_bindings=secret_bindings,
            )
            log_event(
                "session_issued",
                {
                    "request_label": request_label,
                    "client_hint": client_hint,
                    "provider": pending.scopes[0] if pending.scopes else "unknown",
                    "result_status": "issued",
                    "session": session.token[:6],
                },
            )
            return self._session_payload(session, issued_via="challenge")

        if challenge_compat_mode or self.code_only_approval:
            log_event("session_challenge_issued", {"request_label": request_label, "client_hint": client_hint, "result_status": "challenge-issued"})
            return self._issue_challenge(request_label, ttl_minutes, scopes, client_hint, challenge_code_setup)

        approved, approval_state = self._request_human_approval(
            "session",
            request_label,
            ttl_minutes,
            scopes,
            client_hint,
            approval_required_approvals,
        )
        if not approved:
            if approval_state.get("status") in {"denied", "expired"}:
                if approval_state.get("status") == "denied":
                    raise KnoxUnauthorized(f"session request denied: {approval_state.get('reason')}")
                if approval_state.get("status") == "expired":
                    return approval_state | {
                        "result_status": "challenge-required",
                    }
            return approval_state

        session = self.store.issue_session(
            scopes=scopes,
            ttl_minutes=ttl_minutes,
            request_label=request_label,
            client_hint=client_hint,
            key_bindings=secret_bindings,
        )
        log_event(
            "session_issued",
            {
                "request_label": request_label,
                "client_hint": client_hint,
                "result_status": "issued",
                "session": session.token[:6],
            },
        )
        issued_via = "challenge" if challenge_compat_mode else self.approval_mode
        return self._session_payload(session, issued_via=issued_via)

    def issue_proxy_token(self, arguments: dict[str, Any]) -> dict[str, Any]:
        agent_id = arguments.get("agent_id")
        ttl_minutes = arguments.get("ttl_minutes")
        scopes = arguments.get("scopes")
        request_label = arguments.get("request_label")
        client_hint = arguments.get("client_hint")
        secret_bindings = self._normalize_secret_bindings(arguments.get("secret_bindings"))
        approval_required_approvals = self._normalize_required_approvals(arguments.get("approval_required_approvals"))
        challenge_token = arguments.get("challenge_token")
        challenge_code_value = arguments.get("challenge_code")
        challenge_compat_mode = bool(arguments.get("challenge_compat_mode", False))

        if not agent_id or not isinstance(agent_id, str):
            raise KnoxBadRequest("agent_id is required")
        if not isinstance(ttl_minutes, int):
            raise KnoxBadRequest("ttl_minutes is required and must be an integer")
        if ttl_minutes not in ALLOWED_TTLS:
            raise KnoxBadRequest("ttl_minutes must be one of 15, 60, 180")
        if not request_label or not isinstance(request_label, str):
            raise KnoxBadRequest("request_label is required")
        if not isinstance(scopes, list) or not scopes:
            raise KnoxBadRequest("scopes must be a non-empty list")
        if not all(isinstance(item, str) and item for item in scopes):
            raise KnoxBadRequest("each scope must be a non-empty string")

        scopes = self._normalize_scopes(scopes)
        challenge_code_setup = _normalize_challenge_code(arguments.get("challenge_code_setup"))
        if challenge_token or challenge_code_value:
            if challenge_code_setup is not None:
                raise KnoxBadRequest("challenge_code_setup cannot be used with challenge_token/challenge_code")
            if not (challenge_token and challenge_code_value and isinstance(challenge_token, str) and isinstance(challenge_code_value, str)):
                raise KnoxBadRequest("challenge_token and challenge_code must be provided together")
            pending = self.store.verify_challenge(challenge_token, challenge_code_value)
            if pending is None:
                raise KnoxUnauthorized("challenge invalid or expired")
            proxy_token = self.store.issue_proxy_token(
                agent_id=agent_id,
                scopes=pending.scopes or scopes,
                ttl_minutes=pending.ttl_minutes,
                request_label=f"{request_label} (challenge)",
                client_hint=client_hint or pending.client_hint,
                key_bindings=secret_bindings,
            )
            log_event(
                "proxy_token_issued",
                {
                    "agent_id": agent_id,
                    "request_label": request_label,
                    "client_hint": client_hint,
                    "provider": pending.scopes[0] if pending.scopes else "unknown",
                    "result_status": "issued",
                    "proxy_token": proxy_token.token[:6],
                },
            )
            return self._proxy_token_payload(proxy_token, issued_via="challenge")

        if challenge_compat_mode or self.code_only_approval:
            log_event("proxy_token_challenge_issued", {"agent_id": agent_id, "request_label": request_label, "client_hint": client_hint, "result_status": "challenge-issued"})
            return self._issue_challenge(request_label, ttl_minutes, scopes, client_hint, challenge_code_setup)

        approved, approval_state = self._request_human_approval(
            "proxy",
            request_label,
            ttl_minutes,
            scopes,
            client_hint,
            approval_required_approvals,
        )
        if not approved:
            if approval_state.get("status") in {"denied", "expired"}:
                if approval_state.get("status") == "denied":
                    raise KnoxUnauthorized(f"proxy token request denied: {approval_state.get('reason')}")
                if approval_state.get("status") == "expired":
                    return approval_state
            return approval_state

        proxy_token = self.store.issue_proxy_token(
            agent_id=agent_id,
            scopes=scopes,
            ttl_minutes=ttl_minutes,
            request_label=request_label,
            client_hint=client_hint,
            key_bindings=secret_bindings,
        )
        log_event(
            "proxy_token_issued",
            {
                "agent_id": agent_id,
                "request_label": request_label,
                "client_hint": client_hint,
                "result_status": "issued",
                "proxy_token": proxy_token.token[:6],
            },
        )
        issued_via = "challenge" if challenge_compat_mode else self.approval_mode
        return self._proxy_token_payload(proxy_token, issued_via=issued_via)

    def revoke_proxy_token(self, arguments: dict[str, Any]) -> dict[str, Any]:
        token = arguments.get("proxy_token")
        if not token or not isinstance(token, str):
            raise KnoxBadRequest("proxy_token is required")
        revoked = self.store.revoke_proxy_token(token)
        if revoked:
            log_event("proxy_token_revoked", {"proxy_token": token[:6], "result_status": "revoked"})
        return {"proxy_token": token, "revoked": revoked}

    def proxy_token_status(self, arguments: dict[str, Any]) -> dict[str, Any]:
        token = arguments.get("proxy_token")
        if not token or not isinstance(token, str):
            raise KnoxBadRequest("proxy_token is required")
        status = self.store.proxy_token_status(token)
        if status is None:
            return {"active": False, "proxy_token": token}
        return status

    def store_secret(self, arguments: dict[str, Any]) -> dict[str, Any]:
        provider = arguments.get("provider")
        secret = arguments.get("secret")
        session_token = arguments.get("session_token")
        source = arguments.get("source")
        project = arguments.get("project")
        environment = arguments.get("environment")
        notes = arguments.get("notes")
        key_name = arguments.get("key_name")
        overwrite = bool(arguments.get("overwrite", False))
        dry_run = bool(arguments.get("dry_run", False))

        if not provider or not isinstance(provider, str):
            raise KnoxBadRequest("provider is required")
        if source is not None and not isinstance(source, str):
            raise KnoxBadRequest("source must be a string")
        if project is not None and not isinstance(project, str):
            raise KnoxBadRequest("project must be a string")
        if environment is not None and not isinstance(environment, str):
            raise KnoxBadRequest("environment must be a string")
        if notes is not None and not isinstance(notes, str):
            raise KnoxBadRequest("notes must be a string")
        if key_name is not None and not isinstance(key_name, str):
            raise KnoxBadRequest("key_name must be a string")

        if dry_run:
            return {
                "status": "name_suggested",
                "provider": provider,
                "suggested_key_name": key_name or suggest_key_name(provider=provider, source=source, project=project),
                "metadata": {
                    "source": source,
                    "project": project,
                    "environment": environment,
                    "notes": notes,
                },
            }

        if not secret or not isinstance(secret, str):
            raise KnoxBadRequest("secret is required")
        self._require_session_scope(session_token, "knox", "store_secret")

        record = register_provider_secret(
            provider=provider,
            secret=secret,
            key_name=key_name,
            source=source,
            project=project,
            environment=environment,
            notes=notes,
            overwrite=overwrite,
        )
        log_event(
            "secret_stored",
            {
                "provider": provider,
                "key_name": record.key_name,
                "result_status": "stored",
            },
        )
        return {
            "status": "stored",
            "provider": record.provider,
            "key_name": record.key_name,
            "is_default": record.is_default,
            "metadata": {
                "source": record.source,
                "project": record.project,
                "environment": record.environment,
                "notes": record.notes,
            },
        }

    def list_secrets(self, arguments: dict[str, Any]) -> dict[str, Any]:
        session_token = arguments.get("session_token")
        provider = arguments.get("provider")
        if provider is not None and not isinstance(provider, str):
            raise KnoxBadRequest("provider must be a string")

        self._require_session_scope(session_token, "knox", "list_secrets")
        records = list_secret_records(provider=provider)
        return {
            "count": len(records),
            "secrets": [
                {
                    "provider": item.provider,
                    "key_name": item.key_name,
                    "source": item.source,
                    "project": item.project,
                    "environment": item.environment,
                    "notes": item.notes,
                    "is_default": item.is_default,
                    "created_at": item.created_at,
                    "updated_at": item.updated_at,
                }
                for item in records
            ],
        }

    def _require_session_scope(self, token: Any, provider: str, operation: str) -> Session:
        if not token or not isinstance(token, str):
            raise KnoxUnauthorized("session_token is required")
        session = self.store.get_session(token)
        if session is None:
            raise KnoxUnauthorized("session_token is invalid, expired, or revoked")
        if not _scope_authorized(session.scopes, provider, operation):
            raise KnoxUnauthorized("session lacks scope for this operation")
        return session

    def _session_payload(self, session: Session, issued_via: str) -> dict[str, Any]:
        return {
            "status": "issued",
            "issued_via": issued_via,
            "session_token": session.token,
            "ttl_minutes": (session.expires_at - session.issued_at) // 60,
            "expires_at": session.expires_at,
            "request_label": session.request_label,
            "scopes": session.scopes,
            "key_bindings": session.key_bindings,
        }

    def _proxy_token_payload(self, proxy: ProxyToken, issued_via: str) -> dict[str, Any]:
        return {
            "status": "issued",
            "issued_via": issued_via,
            "proxy_token": proxy.token,
            "ttl_minutes": (proxy.expires_at - proxy.issued_at) // 60,
            "expires_at": proxy.expires_at,
            "request_label": proxy.request_label,
            "scopes": proxy.scopes,
            "key_bindings": proxy.key_bindings,
            "agent_id": proxy.agent_id,
        }

    def revoke_session(self, arguments: dict[str, Any]) -> dict[str, Any]:
        token = arguments.get("session_token")
        if not token or not isinstance(token, str):
            raise KnoxBadRequest("session_token is required")
        revoked = self.store.revoke_session(token)
        if revoked:
            log_event("session_revoked", {"session": token[:6], "result_status": "revoked"})
        return {"session_token": token, "revoked": revoked}

    def session_status(self, arguments: dict[str, Any]) -> dict[str, Any]:
        token = arguments.get("session_token")
        if not token:
            return {"active": False, "message": "session_token is required"}
        if not isinstance(token, str):
            raise KnoxBadRequest("session_token must be a string")
        status = self.store.session_status(token)
        if status is None:
            return {"active": False, "session_token": token}
        return status

    def invoke(self, arguments: dict[str, Any]) -> dict[str, Any]:
        token_type, token, token_model, key_bindings = self._extract_invocation_token(arguments)
        provider = arguments.get("provider")
        operation = arguments.get("operation")
        payload = arguments.get("payload")
        idempotency_key = arguments.get("idempotency_key")

        if not isinstance(token, str):
            raise KnoxBadRequest(f"{token_type}_token is required")
        if not provider or not isinstance(provider, str):
            raise KnoxBadRequest("provider is required")
        if not operation or not isinstance(operation, str):
            raise KnoxBadRequest("operation is required")
        payload = payload if isinstance(payload, dict) else {}

        if not is_operation_allowed(self.policy, provider, operation):
            raise KnoxBadRequest(f"Unknown operation: {provider}:{operation}")

        if not _scope_authorized(token_model.scopes, provider, operation):
            raise KnoxUnauthorized("session lacks scope for this operation")

        # allow policy metadata checks
        policy: OperationPolicy = operation_policy(self.policy, provider, operation)
        if idempotency_key is not None and not isinstance(idempotency_key, str):
            raise KnoxBadRequest("idempotency_key must be a string")

        if isinstance(idempotency_key, str) and idempotency_key:
            cached = self.store.read_idempotent(token, idempotency_key)
            if cached:
                return {"status": "replayed", "result": json.loads(cached)}

        secret_alias = key_bindings.get(provider)
        try:
            if "secret_alias" in inspect.signature(invoke_provider).parameters:
                adapter_result = invoke_provider(provider, operation, payload, secret_alias=secret_alias)
            else:
                adapter_result = invoke_provider(provider, operation, payload)
        except (AdapterError, VaultError) as exc:
            payload_out = {"success": False, "summary": "adapter failure", "result": {"error": str(exc)}}
        else:
            payload_out = adapter_result

        outcome = "ok" if payload_out.get("success") else "error"
        result_out = {
            "provider": provider,
            "operation": operation,
            "result_status": outcome,
            "risk": policy.risk,
            "result": payload_out.get("result", payload_out),
            "summary": payload_out.get("summary"),
        }

        # do not include payload/body in log and don't cache raw content
        log_event(
            "knox_invoke",
            {
                "provider": provider,
                "operation": operation,
                "request_label": token_model.request_label,
                "client_hint": token_model.client_hint,
                "result_status": outcome,
                f"{token_type}": token[:6],
            },
        )

        if isinstance(idempotency_key, str) and idempotency_key:
            if token_type != "session":
                raise KnoxBadRequest("idempotency_key is only supported for session tokens")
            self.store.mark_idempotent(
                token,
                idempotency_key,
                json.dumps(result_out, sort_keys=True),
            )

        if not payload_out.get("success"):
            return {"status": "error", "error": payload_out.get("result", {}).get("error", "operation failed"), "summary": payload_out.get("summary"), "risk": policy.risk}
        if token_type == "session":
            return {
                "status": "ok",
                "session_token": token,
                "payload": result_out["result"],
                "risk": policy.risk,
                "summary": payload_out.get("summary"),
            }
        return {
            "status": "ok",
            "proxy_token": token,
            "payload": result_out["result"],
            "risk": policy.risk,
            "summary": payload_out.get("summary"),
        }

    def _extract_invocation_token(self, arguments: dict[str, Any]) -> tuple[str, str, Session | ProxyToken, dict[str, str]]:
        session_token = arguments.get("session_token")
        proxy_token = arguments.get("proxy_token")

        if session_token is None and proxy_token is None:
            raise KnoxUnauthorized("session_token or proxy_token is required")
        if session_token is not None and proxy_token is not None:
            raise KnoxBadRequest("only one of session_token or proxy_token may be provided")
        if isinstance(session_token, str):
            session = self.store.get_session(session_token)
            if session is None:
                raise KnoxUnauthorized("session_token is invalid, expired, or revoked")
            return "session", session_token, session, session.key_bindings
        if isinstance(proxy_token, str):
            token = self.store.get_proxy_token(proxy_token)
            if token is None:
                raise KnoxUnauthorized("proxy_token is invalid, expired, or revoked")
            return "proxy", proxy_token, token, token.key_bindings
        raise KnoxBadRequest("session_token or proxy_token must be strings")

    def _normalize_secret_bindings(self, value: Any) -> dict[str, str]:
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise KnoxBadRequest("secret_bindings must be an object")
        normalized: dict[str, str] = {}
        for raw_key, raw_value in value.items():
            if not isinstance(raw_key, str) or not isinstance(raw_value, str):
                raise KnoxBadRequest("secret_bindings keys and values must be strings")
            key = raw_key.strip()
            alias = raw_value.strip()
            if not key or not alias:
                raise KnoxBadRequest("secret_bindings keys and values must be non-empty")
            normalized[key] = alias
        return normalized

    def _normalize_required_approvals(self, value: Any) -> int:
        if value is None:
            return self.approval_required_approvals
        if not isinstance(value, int):
            raise KnoxBadRequest("approval_required_approvals must be an integer")
        if value < 1:
            raise KnoxBadRequest("approval_required_approvals must be at least 1")
        return value

    def _normalize_scopes(self, scopes: list[str]) -> list[str]:
        allowed = set()
        for scope in scopes:
            if not isinstance(scope, str) or ":" not in scope:
                raise KnoxBadRequest(f"invalid scope format: {scope}")
            provider, operation = scope.split(":", 1)
            if not provider:
                raise KnoxBadRequest(f"invalid scope provider: {scope}")
            if operation == "*":
                if provider not in self.policy.get("providers", {}):
                    raise KnoxBadRequest(f"unsupported provider in scope: {provider}")
                allowed.add(f"{provider}:*")
                continue
            if operation in (self.policy.get("providers", {}).get(provider, {}).get("operations", {})):
                allowed.add(f"{provider}:{operation}")
            else:
                raise KnoxBadRequest(f"scope not permitted: {scope}")
        return sorted(allowed)


def _read_stdin_request() -> tuple[dict[str, Any] | None, bool]:
    """Read a JSON-RPC message from stdio.

    Returns:
        (request, used_header_framing)
    """
    header: dict[str, str] = {}
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None, bool(header)
        if not line.strip():
            break
        decoded = line.decode("utf-8", errors="replace").strip()
        if decoded.lower().startswith("content-length:"):
            header["content-length"] = decoded.split(":", 1)[1].strip()
        if decoded.lower().startswith("{") and "content-length" not in header:
            # JSON framed message with one-line fallback
            try:
                return json.loads(decoded), False
            except json.JSONDecodeError:
                return None, False

    length_raw = header.get("content-length")
    if not length_raw:
        return None, bool(header)
    try:
        length = int(length_raw)
    except ValueError:
        return None, bool(header)
    body = sys.stdin.buffer.read(length)
    if not body:
        return None, bool(header)
    try:
        return json.loads(body.decode("utf-8")), True
    except json.JSONDecodeError:
        return None, True


def _write_response(response: dict[str, Any], use_header_framing: bool) -> None:
    raw = json.dumps(response)
    if use_header_framing:
        sys.stdout.write(f"Content-Length: {len(raw)}\r\n\r\n{raw}")
    else:
        sys.stdout.write(raw + "\n")
    sys.stdout.flush()


def main() -> int:
    try:
        server = KnoxMCPServer()
    except Exception as exc:
        # Fail-closed if Keychain is unavailable.
        sys.stderr.write(f"Knox failed to start: {exc}\n")
        return 1

    use_header_framing = False
    try:
        while True:
            req, header_mode = _read_stdin_request()
            if req is None:
                break
            if header_mode:
                use_header_framing = True
            response = server.handle(req)
            _write_response(response, use_header_framing)
    finally:
        server.finalize()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
