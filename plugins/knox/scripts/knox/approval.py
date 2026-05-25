from __future__ import annotations

import hashlib
import json
import secrets
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

from . import config
from .keychain import challenge_code


_APPROVAL_MODES = {"code", "tray", "hybrid", "biometric", "mobile"}


@dataclass
class ApprovalRequest:
    request_id: str
    request_type: str
    request_label: str
    ttl_minutes: int
    scopes: list[str]
    client_hint: str | None
    code_hash: str
    challenge_code: str | None
    state: str
    required_approvals: int
    approvals: list[str]
    created_at: int
    expires_at: int
    decision: str | None = None


@dataclass
class ApprovalDecision:
    request_id: str
    state: str
    approved: bool


class ApprovalController:
    mode: str
    timeout_seconds: int

    def __init__(
        self,
        mode: str,
        timeout_seconds: int = 90,
        host: str = "127.0.0.1",
    ) -> None:
        normalized = (mode or "").strip().lower()
        if normalized not in _APPROVAL_MODES:
            raise ValueError(f"unsupported approval mode: {mode}")
        self.mode = normalized
        self.timeout_seconds = max(15, int(timeout_seconds))
        self.host = host
        self.requests: dict[str, ApprovalRequest] = {}
        self._condition = threading.Condition()
        self._server: ThreadingHTTPServer | None = None
        self._server_thread: threading.Thread | None = None
        self._server_token: str | None = None
        self._server_port: int | None = None
        self._paired: bool = False
        self._pairing_required: bool = False

    @property
    def control(self) -> tuple[int, str] | None:
        if self._server is None or self._server_token is None or self._server_port is None:
            return None
        return self._server_port, self._server_token

    @classmethod
    def normalize_mode(cls, value: str | None, *, fallback_code: bool = False) -> str:
        normalized = (value or "").strip().lower()
        if normalized in _APPROVAL_MODES:
            return normalized
        return "code" if fallback_code else "biometric"

    def set_pairing_state(self, paired: bool, pairing_required: bool) -> None:
        self._paired = paired
        self._pairing_required = pairing_required
        self._write_control_file()

    def start(self) -> bool:
        if self.mode not in {"tray", "hybrid", "mobile"}:
            return False
        if self._server is not None:
            return True

        self._server_token = secrets.token_urlsafe(20)
        token = self._server_token
        self._server = ThreadingHTTPServer((self.host, 0), self._build_handler(token))
        self._server_port = self._server.server_address[1]
        self._write_control_file()

        self._server_thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._server_thread.start()
        return True

    def stop(self) -> None:
        if self._server is None:
            return
        self._server.shutdown()
        self._server.server_close()
        if self._server_thread is not None:
            self._server_thread.join(timeout=0.2)
        self._server = None
        self._server_thread = None
        self._server_token = None
        self._server_port = None
        self._clear_control_file()

    def create_request(
        self,
        request_type: str,
        request_label: str,
        ttl_minutes: int,
        scopes: list[str],
        client_hint: str | None = None,
        required_approvals: int = 1,
    ) -> tuple[ApprovalRequest, str]:
        code = challenge_code()
        request_id = secrets.token_urlsafe(18)
        now = int(time.time())
        request = ApprovalRequest(
            request_id=request_id,
            request_type=request_type,
            request_label=request_label,
            ttl_minutes=ttl_minutes,
            scopes=list(scopes),
            client_hint=client_hint,
            code_hash=_hash_code(code),
            challenge_code=code,
            state="pending",
            required_approvals=max(1, int(required_approvals)),
            approvals=[],
            created_at=now,
            expires_at=now + self.timeout_seconds,
        )
        with self._condition:
            self.requests[request_id] = request
            self._condition.notify_all()
        return request, code

    def wait_for_decision(self, request: ApprovalRequest) -> ApprovalDecision:
        self._cleanup_request(request.request_id)
        with self._condition:
            remaining = request.expires_at - time.time()
            while request.state == "pending" and remaining > 0:
                self._condition.wait(remaining)
                remaining = request.expires_at - time.time()

            if request.state == "approved":
                self.requests.pop(request.request_id, None)
                return ApprovalDecision(request.request_id, request.state, True)
            if request.state == "denied":
                self.requests.pop(request.request_id, None)
                return ApprovalDecision(request.request_id, request.state, False)
            if request.state == "expired":
                self.requests.pop(request.request_id, None)
                return ApprovalDecision(request.request_id, request.state, False)

            request.state = "expired"
            self._cleanup_request(request.request_id)
            self.requests.pop(request.request_id, None)
            return ApprovalDecision(request.request_id, request.state, False)

    def submit_decision(
        self,
        request_id: str,
        code: str,
        action: str,
        approver_id: str | None = None,
    ) -> str:
        if action not in {"approve", "deny"}:
            return "invalid_decision"
        if not _is_six_digit(code):
            return "invalid_code"

        with self._condition:
            request = self.requests.get(request_id)
            if request is None:
                return "missing"
            self._cleanup_request(request_id)
            if request.state != "pending":
                return request.state
            if request.code_hash != _hash_code(code):
                return "invalid_code"

            if action == "approve":
                actor = approver_id.strip() if isinstance(approver_id, str) and approver_id.strip() else "local"
                if actor not in request.approvals:
                    request.approvals.append(actor)

                if len(request.approvals) >= request.required_approvals:
                    request.state = "approved"
                    request.decision = action
                    self.requests.pop(request_id, None)
                    self._condition.notify_all()
                    return request.state

                # Partial approvals are intentionally retained and wait for quorum.
                return "pending"

            request.state = "denied"
            request.decision = action
            self.requests.pop(request_id, None)
            self._condition.notify_all()
            return request.state

    def pending_requests(self, include_code: bool = False) -> list[dict[str, Any]]:
        now = int(time.time())
        with self._condition:
            self._cleanup()
            return [
                {
                    "request_id": request.request_id,
                    "request_type": request.request_type,
                    "request_label": request.request_label,
                    "ttl_minutes": request.ttl_minutes,
                    "scopes": request.scopes,
                    "client_hint": request.client_hint,
                    "required_approvals": request.required_approvals,
                    "approvals": request.approvals,
                    "state": request.state,
                    "created_at": request.created_at,
                    "expires_at": request.expires_at,
                    "seconds_left": max(0, request.expires_at - now),
                    "challenge_code": request.challenge_code if include_code and request.challenge_code else None,
                }
                for request in self.requests.values()
                if request.state == "pending"
            ]

    def _cleanup(self) -> None:
        now = int(time.time())
        for request in self.requests.values():
            if request.state == "pending" and request.expires_at <= now:
                request.state = "expired"

    def _cleanup_request(self, request_id: str) -> None:
        request = self.requests.get(request_id)
        if request is None:
            return
        if request.state == "pending" and request.expires_at <= int(time.time()):
            request.state = "expired"

    def _write_control_file(self) -> None:
        control = self.control
        if control is None:
            return
        payload = {
            "host": self.host,
            "port": control[0],
            "token": control[1],
            "mode": self.mode,
            "timeout_seconds": self.timeout_seconds,
            "request_at": int(time.time()),
            "paired": self._paired,
            "pairing_required": self._pairing_required,
        }
        path = config.KNOX_APPROVAL_CONTROL_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
        path.chmod(0o600)

    def _clear_control_file(self) -> None:
        path = config.KNOX_APPROVAL_CONTROL_PATH
        if not path.exists():
            return
        try:
            path.unlink()
        except OSError:
            return

    def _build_handler(self, token: str):
        controller = self

        class _RequestHandler(BaseHTTPRequestHandler):
            server_version = "KnoxApproval/1.0"

            def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
                body = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def _authorized(self) -> bool:
                value = self.headers.get("authorization", "")
                return value == f"Bearer {token}"

            def _bad_request(self, message: str) -> None:
                self._send_json({"error": message}, 400)

            def _read_json(self) -> dict[str, Any] | None:
                length = self.headers.get("Content-Length")
                if not length:
                    return {}
                try:
                    raw = self.rfile.read(int(length))
                    return json.loads(raw.decode("utf-8"))
                except (json.JSONDecodeError, OSError, UnicodeDecodeError, ValueError):
                    return None

            def do_GET(self) -> None:  # type: ignore[override]
                if not self._authorized():
                    return self._send_json({"error": "unauthorized"}, 401)

                parsed = urlparse(self.path)
                if parsed.path == "/approval/pending":
                    params = parse_qs(parsed.query)
                    include_code = params.get("include_code", [""])[0].lower() in {"1", "true", "yes", "on"}
                    return self._send_json({"requests": controller.pending_requests(include_code)})
                if parsed.path == "/approval/control":
                    return self._send_json(
                        {
                            "running": True,
                            "mode": controller.mode,
                            "host": controller.host,
                            "port": controller.control[0] if controller.control else None,
                            "paired": controller._paired,
                            "pairing_required": controller._pairing_required,
                        }
                    )
                self._send_json({"error": "not_found"}, 404)

            def do_POST(self) -> None:  # type: ignore[override]
                if not self._authorized():
                    return self._send_json({"error": "unauthorized"}, 401)

                parsed = urlparse(self.path)
                if parsed.path != "/approval/decision":
                    return self._send_json({"error": "not_found"}, 404)
                payload = self._read_json()
                if payload is None:
                    return self._bad_request("invalid_json")

                request_id = payload.get("request_id")
                code = payload.get("code")
                action = payload.get("action")
                if not isinstance(request_id, str) or not isinstance(code, str) or not isinstance(action, str):
                    return self._bad_request("invalid_payload")

                approver_id = payload.get("approver_id")
                if approver_id is not None and not isinstance(approver_id, str):
                    return self._bad_request("invalid_payload")

                result = controller.submit_decision(request_id, code, action, approver_id)
                return self._send_json({"result": result})

            def log_message(self, format: str, *args: object) -> None:
                return None

        return _RequestHandler


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def _is_six_digit(code: str) -> bool:
    return code.isdigit() and len(code) == 6
