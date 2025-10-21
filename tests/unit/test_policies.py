from src.oal_agent.security.policies import SecurityPolicy

def test_unknown_policy_action():
    policy = SecurityPolicy()
    assert not policy.check_permission("unknown_action", "some_resource")

def test_allowed_policy_action():
    policy = SecurityPolicy()
    assert policy.check_permission("read", "some_resource")
    assert policy.check_permission("write", "another_resource")
    assert policy.check_permission("execute", "yet_another_resource")
    assert policy.check_permission("analyze", "some_code")
