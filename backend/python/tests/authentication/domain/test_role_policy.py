import unittest

from authentication.domain.policies.role_policy import has_any_role


class RolePolicyTestCase(unittest.TestCase):
    def test_matching_role_is_allowed(self) -> None:
        self.assertTrue(has_any_role([" authenticated "], ["authenticated"]))

    def test_missing_role_is_denied(self) -> None:
        self.assertFalse(has_any_role(["authenticated"], ["admin"]))
