import unittest

from apps.api.medidas import format_measure, parse_measure


class MeasureTests(unittest.TestCase):
    def test_examples_round_trip_as_simplified_fractions(self):
        self.assertEqual(parse_measure("24"), 384)
        self.assertEqual(parse_measure("26 1/2"), 424)
        self.assertEqual(parse_measure("24 1/4 1/16"), 389)
        self.assertEqual(format_measure(389), "24 5/16")
        self.assertEqual(format_measure(424), "26 1/2")

    def test_rejects_incomplete_or_finer_than_sixteenth(self):
        for value in ("", " ", "0", "24 1/32", "24 1/", "24 1/2 1", "24.25", "-2"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_measure(value)


if __name__ == "__main__":
    unittest.main()
