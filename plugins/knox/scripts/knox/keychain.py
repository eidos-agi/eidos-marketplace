from __future__ import annotations

import platform
import secrets
import subprocess
import tempfile
from pathlib import Path


SERVICE_NAME = "com.knox.secrets"


class KnoxKeychainError(RuntimeError):
    """Raised when keychain interactions fail."""


class KnoxKeychainUnavailable(RuntimeError):
    """Raised when macOS keychain access is unavailable."""


SWIFT_AUTH_SOURCE = r'''
import Foundation
import LocalAuthentication
import Security

let reason = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "Authorize Knox action"

func statusMessage(_ status: OSStatus) -> String {
    if let message = SecCopyErrorMessageString(status, nil) {
        return message as String
    }
    return "OSStatus \(status)"
}

let context = LAContext()
var error: NSError?
if !context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) {
    print("KNOX_AUTH_ERROR:" + (error?.localizedDescription ?? "biometric unavailable"))
    exit(2)
}

let sem = DispatchSemaphore(value: 0)
context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, localizedReason: reason) { success, authError in
    if !success {
        print("KNOX_AUTH_ERROR:" + (authError?.localizedDescription ?? "authentication failed"))
        exit(1)
    }
    sem.signal()
}
sem.wait()
'''


SWIFT_STORE_SOURCE = r'''
import Foundation
import Security

let service = "com.knox.secrets"
let alias = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : ""

func statusMessage(_ status: OSStatus) -> String {
    if let message = SecCopyErrorMessageString(status, nil) {
        return message as String
    }
    return "OSStatus \(status)"
}

if alias.isEmpty {
    print("KNOX_STORE_ERROR:missing alias")
    exit(2)
}

let secretData = FileHandle.standardInput.readDataToEndOfFile()
if secretData.isEmpty {
    print("KNOX_STORE_ERROR:empty secret")
    exit(2)
}

let query: [String: Any] = [
    kSecClass as String: kSecClassGenericPassword,
    kSecAttrService as String: service,
    kSecAttrAccount as String: alias
]

let updateAttrs: [String: Any] = [
    kSecValueData as String: secretData
]

let updateStatus = SecItemUpdate(query as CFDictionary, updateAttrs as CFDictionary)
if updateStatus == errSecSuccess {
    exit(0)
}
if updateStatus != errSecItemNotFound {
    print("KNOX_STORE_ERROR:\(statusMessage(updateStatus))")
    exit(1)
}

var addQuery = query
addQuery[kSecValueData as String] = secretData
addQuery[kSecAttrAccessible as String] = kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly

let addStatus = SecItemAdd(addQuery as CFDictionary, nil)
if addStatus != errSecSuccess {
    print("KNOX_STORE_ERROR:\(statusMessage(addStatus))")
    exit(1)
}
'''


def ensure_macos() -> None:
    if platform.system() != "Darwin":
        raise KnoxKeychainUnavailable("Knox macOS security policy requires macOS in v1.")


def run_command(args: list[str], input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def is_available() -> bool:
    """Return True when the macOS security toolchain can run."""
    if platform.system() != "Darwin":
        return False
    security = Path("/usr/bin/security")
    return security.exists()


def store_secret(alias: str, secret: str) -> None:
    ensure_macos()
    if not is_available():
        raise KnoxKeychainUnavailable("macOS security tool unavailable.")

    with tempfile.NamedTemporaryFile("w", suffix=".swift", delete=False) as tmp:
        tmp.write(SWIFT_STORE_SOURCE)
        swift_path = Path(tmp.name)

    try:
        proc = run_command(["/usr/bin/swift", str(swift_path), alias], input_text=secret)
    finally:
        swift_path.unlink(missing_ok=True)

    if proc.returncode != 0:
        message = proc.stdout.strip() or proc.stderr.strip() or "failed to store secret"
        if message.startswith("KNOX_STORE_ERROR:"):
            message = message.replace("KNOX_STORE_ERROR:", "").strip()
        raise KnoxKeychainError(message)


def read_secret(alias: str) -> str:
    ensure_macos()
    if not is_available():
        raise KnoxKeychainUnavailable("macOS security tool unavailable.")

    proc = run_command(
        [
            "/usr/bin/security",
            "find-generic-password",
            "-a",
            alias,
            "-s",
            SERVICE_NAME,
            "-w",
        ]
    )
    if proc.returncode != 0:
        raise KnoxKeychainError(proc.stderr.strip() or proc.stdout.strip() or "secret not found")

    token = proc.stdout.strip()
    if not token:
        raise KnoxKeychainError("empty token from keychain")
    return token


def delete_secret(alias: str) -> None:
    if not is_available():
        return
    run_command(["/usr/bin/security", "delete-generic-password", "-a", alias, "-s", SERVICE_NAME])


def has_secret(alias: str) -> bool:
    if not is_available():
        return False
    proc = run_command(["/usr/bin/security", "find-generic-password", "-a", alias, "-s", SERVICE_NAME])
    return proc.returncode == 0


def authorize_human(reason: str) -> None:
    """
    Require a local biometric approval from the signed-in user.

    Knox uses LocalAuthentication so the approval is tied to the actual operator and local
    OS credential.
    """
    ensure_macos()
    if not is_available():
        raise KnoxKeychainUnavailable("macOS security tool unavailable.")

    with tempfile.NamedTemporaryFile("w", suffix=".swift", delete=False) as tmp:
        tmp.write(SWIFT_AUTH_SOURCE)
        swift_path = Path(tmp.name)

    try:
        proc = run_command(["/usr/bin/swift", str(swift_path), reason])
    finally:
        swift_path.unlink(missing_ok=True)

    if proc.returncode != 0:
        message = proc.stdout.strip() or proc.stderr.strip() or "biometric approval failed"
        if message.startswith("KNOX_AUTH_ERROR:"):
            message = message.replace("KNOX_AUTH_ERROR:", "").strip()
        raise KnoxKeychainError(message)


def challenge_code(length: int = 6) -> str:
    return "".join([str(secrets.randbelow(10)) for _ in range(length)])
