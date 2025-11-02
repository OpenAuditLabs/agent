import pytest
from unittest.mock import AsyncMock, patch
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


@pytest.mark.asyncio
async def test_check_static_analysis_misconfigurations():
    with patch("os.path.exists", return_value=True):
        with patch("os.path.isfile", return_value=True):
            policy = SecurityPolicy()
            policy.slither_tool.analyze = AsyncMock(side_effect=[["finding1"], []])

            # Test case where misconfigurations are found
            result_found = await policy.check_static_analysis_misconfigurations(
                "path/to/contract.sol"
            )
            assert result_found is True
            policy.slither_tool.analyze.assert_called_with("path/to/contract.sol")

            # Test case where no misconfigurations are found
            result_not_found = await policy.check_static_analysis_misconfigurations(
                "path/to/another_contract.sol"
            )
            assert result_not_found is False
            policy.slither_tool.analyze.assert_called_with("path/to/another_contract.sol")
