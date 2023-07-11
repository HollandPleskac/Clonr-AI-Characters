import calendar
from datetime import datetime
from zoneinfo import ZoneInfo

import dateutil

# NOTE: on datetime tokenizations
# isoformat with seconds is about 12 tokens on average (10 without seconds)
# the long human readable format is about 16 tokens on average (without seconds)
# for 100 messages, this can add up ☹️
ZERO_TIME_LABEL = "now"


def bytes_to_human_readable(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


class DateFormat:
    @staticmethod
    def isoformat(dt: datetime, include_seconds: bool = True) -> str:
        if include_seconds:
            pattern = "%Y-%m-%d %H:%M:%S"
        else:
            pattern = "%Y-%m-%d %H:%M"
        return dt.strftime(pattern)

    @staticmethod
    def _datediff_to_arr(*, start_date: datetime, end_date: datetime) -> list[str]:
        arr: list[str] = []
        delta = dateutil.relativedelta.relativedelta(end_date, start_date)
        if delta.years:
            arr.append(f"{delta.years} year")
        if delta.months:
            arr.append(f"{delta.months} month")
        if delta.days:
            arr.append(f"{delta.days} day")
        if delta.hours:
            arr.append(f"{delta.hours} hour")
        if delta.minutes:
            arr.append(f"{delta.minutes} minute")
        if delta.seconds:
            arr.append(f"{delta.seconds} second")
        arr = [x + ("s" if not x.startswith("1 ") else "") for x in arr]
        return arr

    @staticmethod
    def human_readable(
        dt: datetime, add_weekday: bool = True, use_today_and_yesterday: bool = True
    ):
        """Returns things like "yesterday at 4:05pm" or "Tuesday, June 5th, 2023 at 4:00pm"
        This might be too verbose and unnecessarily run up the token count. Test it out.
        Also, note that abbreviations don't reduce token count, since the month names are already
        tokens.
            Args:
                dt (datetime): datetime with timezone info.
        """
        arr: list[str] = []
        delta = datetime.now(tz=dt.tzinfo or ZoneInfo("utc")) - dt
        if use_today_and_yesterday and delta.days <= 0:
            arr.append("Today")
        elif use_today_and_yesterday and delta.days == 1:
            arr.append("Yesterday")
        else:
            if add_weekday:
                arr.append(calendar.day_name[dt.weekday()] + ",")
            month = calendar.month_name[dt.month]
            if dt.day in [1, 21, 31]:
                suffix = "st"
            elif dt.day in [2, 22]:
                suffix = "nd"
            elif dt.day in [3, 23]:
                suffix = "rd"
            else:
                suffix = "th"
            arr.append(f"{month} {dt.day}{suffix}, {dt.year}")
        arr.append("at")
        if dt.hour <= 12:
            suffix = "am"
        else:
            suffix = "pm"
        # this covers the 12am and 12pm case by converting 0 => 12
        hour = (dt.hour % 12) or 12
        arr.append(f"{hour}:{dt.second:02d}{suffix}")
        return " ".join(arr)

    @staticmethod
    def relative(
        start_date: datetime,
        end_date: datetime | None = None,
        n_largest_times: int = -1,
    ) -> str:
        """Converts a start and an end date pair into a relative time. Useful for
        giving a more realistic natural language description of retrieve memories.

        Example would be: "13 hours and 12 minutes" ago. as opposed to the raw datetime string.
        This does not parse today, yesterday.

        Args:
            start_date (datetime): start date.
            end_date (datetime, optional): end date or defaults to current date.
            n_largest_times (int, optional): how many denominations to keep, from largest to smallest
                a value of -1 means keep all denominations from years -> seconds. Defaults to -1.

        Returns:
            str: the natural language time difference string.
        """
        arr = DateFormat._datediff_to_arr(start_date=start_date, end_date=end_date)
        if not arr:
            return ZERO_TIME_LABEL
        if n_largest_times > 0:
            arr = arr[:n_largest_times]
        if len(arr) > 1:
            arr = arr[:-1] + ["and"] + arr[-1:]
        return " ".join(arr)
