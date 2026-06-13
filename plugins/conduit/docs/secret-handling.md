# Conduit Secret-Handling Policy

Conduit is a private repo, but it still must not store raw secrets.

## Allowed

- Machine ids.
- SSH aliases and hostnames.
- Usernames needed to form SSH specs.
- Vault or Keychain metadata paths.
- Public key ids.
- Token fingerprints or short fingerprints.
- Proof stderr/stdout that does not reveal secret values.

## Not Allowed

- Passwords.
- Private keys.
- API tokens.
- TOTP seeds.
- Recovery codes.
- Cookies or session tokens.
- Raw credential payloads.

## Agent Rules

- If a credential is needed, ask Knox or the appropriate credential agent to
  handle it. Do not put the value in Conduit docs, registry, proof rows, or
  Linear comments.
- If a proof command prints a secret, stop and redact before committing.
- Store references like `password_path`, `keychain_label`, or
  `vault_secret_id`, never the secret value.

## Proof Review

Before committing proof rows:

```bash
rg -n "password|api[_-]?token|totp|private[_-]?key|secret|cookie|session" registry/conduit-proofs
```

Matches are not automatically leaks, but they require review. Words in command
names or failure labels are acceptable only when no secret value is present.
