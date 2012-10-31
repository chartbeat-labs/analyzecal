from datetime import datetime
import unittest

from utils import num_working_days


class NumWorkingDaysTest(unittest.TestCase):
    def test_whole_weeks(self):
        start = datetime(2012, 10, 1)
        end = datetime(2012, 10, 7)
        # Mon-Sun, 1 week
        self.assertEqual(num_working_days(start, end), 5)

        start = datetime(2012, 10, 1)
        end = datetime(2012, 10, 14)
        # Mon-Sun, 2 weeks
        self.assertEqual(num_working_days(start, end), 10)

    def test_odd_days(self):
        start = datetime(2012, 10, 1)
        end = datetime(2012, 10, 3)
        # Mon-Wed
        self.assertEqual(num_working_days(start, end), 3)

        start = datetime(2012, 10, 1)
        end = datetime(2012, 10, 5)
        # Mon-Fri
        self.assertEqual(num_working_days(start, end), 5)

        start = datetime(2012, 10, 5)
        end = datetime(2012, 10, 8)
        # Fri-Mon
        self.assertEqual(num_working_days(start, end), 2)

        start = datetime(2012, 10, 7)
        end = datetime(2012, 10, 10)
        # Sun-Wed
        self.assertEqual(num_working_days(start, end), 3)

    def test_weeks_plus_odd_days(self):
        start = datetime(2012, 10, 1)
        end = datetime(2012, 10, 17)
        self.assertEqual(num_working_days(start, end), 13)
