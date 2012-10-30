DT_FORMAT = '%Y-%m-%dT%H:%M:%S'
"""Date/time format string"""

from datetime import datetime


def str_to_datetime(str):
    """
    Convert a "Google String" (RFC3339) to a datetime object.
    @note: does not support the timezone (ignores it)!

    @param str: str, datetime as string
    @return: datetime
    """
    return datetime.strptime(str[:-6], DT_FORMAT)
