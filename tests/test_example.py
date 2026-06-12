import unittest

from example_package_roryyeung import greet


class TestExample(unittest.TestCase):
    def test_greet(self) -> None:
        self.assertEqual(greet("World"), "Hello, World!")


if __name__ == "__main__":
    unittest.main()
