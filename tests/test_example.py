import unittest

import r2_ert
import r2_ert.helper_functions
import r2_ert.Structured_Foward_Survey


class TestPackaging(unittest.TestCase):
    def test_package_imports(self) -> None:
        self.assertIsNotNone(r2_ert)
        self.assertIsNotNone(r2_ert.helper_functions)
        self.assertIsNotNone(r2_ert.Structured_Foward_Survey)


if __name__ == "__main__":
    unittest.main()
