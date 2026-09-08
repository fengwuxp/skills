import unittest

from labels import normalize_label


class NormalizeLabelTests(unittest.TestCase):
    def test_none(self):
        self.assertEqual(normalize_label(None), "")

    def test_trimmed_string(self):
        self.assertEqual(normalize_label("  sample  "), "sample")

    def test_empty_string(self):
        self.assertEqual(normalize_label(""), "")


if __name__ == "__main__":
    unittest.main()
