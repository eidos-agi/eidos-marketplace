from scripts.knox import policy


def test_default_policy_has_expected_providers():
    payload = policy.load_policy()
    providers = payload.get("providers", {})
    assert "github" in providers
    assert "openrouter" in providers
    assert "local" in providers


def test_is_operation_allowed():
    payload = policy.load_policy()
    assert policy.is_operation_allowed(payload, "github", "list_repos")
    assert policy.is_operation_allowed(payload, "local", "time")
    assert not policy.is_operation_allowed(payload, "github", "delete_org")
    assert not policy.is_operation_allowed(payload, "missing", "anything")
