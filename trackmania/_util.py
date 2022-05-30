import logging
import re
from datetime import datetime
from types import NoneType

_log = logging.getLogger(__name__)


def _add_commas(num: int) -> str:
    return "{:,}".format(num)


def _regex_it(text: str | None) -> str | None:
    REGEX = r"(?i)(?<!\$)((?P<d>\$+)(?P=d))?((?<=\$)(?!\$)|(\$([a-f\d]{1,3}|[ionmwsztg<>]|[lhp](\[[^\]]+\])?)))"
    SUBST = ""

    if isinstance(text, NoneType):
        return None

    return re.sub(REGEX, SUBST, text)


def _frmt_str_to_datetime(date_string: str | None) -> datetime | None:
    if date_string is None:
        return None

    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S+00:00",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d_%H_%M",
    ]

    for fmt in formats:
        _log.debug("Trying %s with format %s", date_string, fmt)
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue

    return None
