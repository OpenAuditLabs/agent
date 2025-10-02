"""Security policies."""


class SecurityPolicy:
    """Defines security policies."""

    def __init__(self):
        """Initialize security policy."""
        pass

    def check_permission(self, action: str, resource: str) -> bool:
        """Check if action is permitted on resource."""
        # TODO: Implement permission checks
        return True
