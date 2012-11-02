"""
Calendar related utility functions
"""

DT_FORMAT = '%Y-%m-%dT%H:%M:%S'
"""Date/time format string"""

from datetime import datetime
from datetime import timedelta


def str_to_datetime(dt_str):
    """
    Convert a "Google String" (RFC3339) to a datetime object.
    @note: does not support the timezone (ignores it)!

    @param str: dt_str, datetime as string
    @return: datetime
    """
    return datetime.strptime(dt_str[:-6], DT_FORMAT)


def num_working_days(start, end):
    """
    Calculate the number of working days in a given date range.

    TODO: does not take holidays into account

    @param start: datetime, start of range
    @param end: datetime, end of range
    @return: int, number of working days
    """
    # add one day to the end, since that's easier to calculate that way
    end = end + timedelta(days=1)

    # count whole weeks
    total = end - start
    weeks = (total.days) / 7
    wdays = weeks * 5

    # handle the rest
    start_num = start.weekday()
    end_num = end.weekday()
    if end_num < start_num:
        end_num += 7
    # count number of non-weekend days in the range from start to end
    rest = len([d for d in range(start_num, end_num) if d % 7 < 5])
    wdays += rest

    return wdays
