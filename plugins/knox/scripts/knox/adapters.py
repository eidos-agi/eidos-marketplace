from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from .vault import VaultError, read_named_secret, read_provider_secret


class AdapterError(RuntimeError):
    """Raised when a provider adapter cannot complete a request."""


def _safe_request(
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    payload: str | None = None,
    timeout: int = 8,
) -> tuple[int, dict[str, Any] | list[Any]]:
    request = urllib.request.Request(url, data=payload.encode("utf-8") if payload else None, method=method)
    request.add_header("Accept", "application/json")
    request.add_header("User-Agent", "knox-mcp/0.1.0")
    if payload is not None:
        request.add_header("Content-Type", "application/json")
    if headers:
        for key, value in headers.items():
            request.add_header(key, value)

    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
        body = json.loads(raw) if raw else {}
        return int(response.status), body


def _redact_provider_result(data: dict[str, Any]) -> dict[str, Any]:
    redacted = dict(data)
    # ensure provider adapters do not leak provider credentials
    redacted.pop("authorization", None)
    redacted.pop("api_key", None)
    redacted.pop("token", None)
    redacted.pop("secret", None)
    return redacted


def _ensure_provider_secret(provider: str, secret_alias: str | None = None) -> str:
    try:
        if secret_alias:
            return read_named_secret(secret_alias)
        return read_provider_secret(provider)
    except VaultError as exc:
        raise AdapterError(str(exc)) from exc


def _github_request(method: str, endpoint: str, payload: str | None, token: str) -> tuple[bool, dict[str, Any]]:
    headers = {
        "Authorization": f"Bearer {token}",
    }
    try:
        status, body = _safe_request(method, f"https://api.github.com{endpoint}", headers, payload=payload)
    except urllib.error.HTTPError as exc:
        body = exc.reason if isinstance(exc.reason, str) else str(exc.reason)
        return False, {"provider": "github", "operation": endpoint, "error": str(body), "status_code": getattr(exc, "code", 500)}
    except Exception as exc:
        return False, {"provider": "github", "operation": endpoint, "error": str(exc)}
    return True, _redact_provider_result({"provider": "github", "operation": endpoint, "status_code": status, "payload": body})


def _openrouter_request(
    method: str,
    endpoint: str,
    payload: str | None,
    token: str,
) -> tuple[bool, dict[str, Any]]:
    headers = {
        "Authorization": f"Bearer {token}",
    }
    try:
        status, body = _safe_request(method, f"https://openrouter.ai{endpoint}", headers, payload=payload)
    except urllib.error.HTTPError as exc:
        body = exc.reason if isinstance(exc.reason, str) else str(exc.reason)
        return False, {"provider": "openrouter", "operation": endpoint, "error": str(body), "status_code": getattr(exc, "code", 500)}
    except Exception as exc:
        return False, {"provider": "openrouter", "operation": endpoint, "error": str(exc)}
    return True, _redact_provider_result({"provider": "openrouter", "operation": endpoint, "status_code": status, "payload": body})


def _result(summary: str, data: dict[str, Any], success: bool = True) -> dict[str, Any]:
    return {"success": success, "summary": summary, "result": data}


def _format_error(operation: str, message: str, details: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"operation": operation, "error": message}
    if details:
        payload["details"] = details
    return _result("operation failed", payload, success=False)


def _invoke_local(operation: str, payload: dict[str, Any]) -> dict[str, Any]:
    if operation == "time":
        return _result(
            "local time metadata",
            {"provider": "local", "operation": operation, "utc_timestamp": payload.get("timestamp", None) or __import__("datetime").datetime.utcnow().isoformat()},
        )
    if operation == "echo":
        payload_size = len(payload) if isinstance(payload, dict) else 0
        return _result(
            "local echo",
            {
                "provider": "local",
                "operation": operation,
                "payload_size": payload_size,
                "echo_accepted": True,
            },
        )
    return _format_error(operation, "unknown local operation")


def _invoke_github(operation: str, payload: dict[str, Any], secret_alias: str | None = None) -> dict[str, Any]:
    token = _ensure_provider_secret("github", secret_alias=secret_alias)
    if operation == "list_repos":
        success, data = _github_request("GET", "/user/repos?per_page=100&sort=updated", None, token)
        if not success:
            return _format_error(operation, "github request failed", data.get("error"))
        repos = []
        if isinstance(data.get("payload"), list):
            for repo in data["payload"][:20]:
                if isinstance(repo, dict):
                    repos.append(
                        {
                            "full_name": repo.get("full_name"),
                            "private": bool(repo.get("private", False)),
                            "url": repo.get("html_url"),
                        }
                    )
        return _result("github repositories listed", {"provider": "github", "operation": operation, "repo_count": len(repos), "repos": repos})

    if operation == "get_user":
        success, data = _github_request("GET", "/user", None, token)
        if not success:
            return _format_error(operation, "github request failed", data.get("error"))
        user = data.get("payload", {}) if isinstance(data.get("payload"), dict) else {}
        return _result(
            "github user fetched",
            {
                "provider": "github",
                "operation": operation,
                "login": user.get("login"),
                "name": user.get("name"),
                "id": user.get("id"),
            },
        )

    if operation == "create_issue":
        repo = payload.get("repo")
        if not isinstance(repo, str) or "/" not in repo:
            return _format_error(operation, "repo must be owner/repo")
        title = payload.get("title")
        if not isinstance(title, str) or not title.strip():
            return _format_error(operation, "title is required")
        body = payload.get("body", "")
        body_payload = json.dumps({"title": title, "body": body or None})
        success, data = _github_request("POST", f"/repos/{repo}/issues", body_payload, token)
        if not success:
            return _format_error(operation, "github request failed", data.get("error"))
        issue = data.get("payload", {}) if isinstance(data.get("payload"), dict) else {}
        return _result(
            "github issue created",
            {
                "provider": "github",
                "operation": operation,
                "repo": repo,
                "issue_number": issue.get("number"),
                "issue_url": issue.get("html_url"),
            },
        )

    return _format_error(operation, "unknown github operation")


def _invoke_openrouter(operation: str, payload: dict[str, Any], secret_alias: str | None = None) -> dict[str, Any]:
    token = _ensure_provider_secret("openrouter", secret_alias=secret_alias)
    if operation == "list_models":
        success, data = _openrouter_request("GET", "/api/v1/models", None, token)
        if not success:
            return _format_error(operation, "openrouter request failed", data.get("error"))
        models = data.get("payload", [])
        count = len(models) if isinstance(models, list) else 0
        top = []
        if isinstance(models, list):
            for item in models[:10]:
                if isinstance(item, dict):
                    top.append(item.get("id"))
        return _result("openrouter models listed", {"provider": "openrouter", "operation": operation, "count": count, "sample_models": top})

    if operation == "list_credits":
        success, data = _openrouter_request("GET", "/api/v1/credits", None, token)
        if not success:
            return _format_error(operation, "openrouter request failed", data.get("error"))
        return _result(
            "openrouter credits read",
            {
                "provider": "openrouter",
                "operation": operation,
                "data": data.get("payload"),
            },
        )

    if operation == "run_query":
        prompt = payload.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            return _format_error(operation, "prompt required")
        body = json.dumps({"model": payload.get("model", "gpt-3.5-turbo"), "messages": [{"role": "user", "content": prompt}]})
        success, data = _openrouter_request("POST", "/api/v1/chat/completions", body, token)
        if not success:
            return _format_error(operation, "openrouter request failed", data.get("error"))
        response_body = data.get("payload", {})
        message = ""
        if isinstance(response_body, dict):
            choices = response_body.get("choices")
            if isinstance(choices, list) and choices:
                first = choices[0]
                if isinstance(first, dict):
                    message = str(first.get("message", {}).get("content", ""))
        return _result(
            "openrouter query executed",
            {"provider": "openrouter", "operation": operation, "message": message[:120], "credits_spent": response_body.get("usage", {}).get("total_tokens") if isinstance(response_body, dict) else None},
        )

    return _format_error(operation, "unknown openrouter operation")


@dataclass(frozen=True)
class Invocation:
    provider: str
    operation: str
    payload: dict[str, Any]


def invoke(provider: str, operation: str, payload: dict[str, Any], secret_alias: str | None = None) -> dict[str, Any]:
    payload = payload or {}
    if not isinstance(payload, dict):
        return _format_error(operation, "payload must be an object")

    if provider == "local":
        return _invoke_local(operation, payload)
    if provider == "github":
        return _invoke_github(operation, payload, secret_alias=secret_alias)
    if provider == "openrouter":
        return _invoke_openrouter(operation, payload, secret_alias=secret_alias)
    return _format_error(operation, f"unsupported provider: {provider}")


__all__ = ["AdapterError", "Invocation", "invoke"]
