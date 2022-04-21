import re
from types import NoneType


def _add_commas(num: int) -> str:
    return "{:,}".format(num)


def _regex_it(text: str | None) -> str | None:
    REGEX = r"(?i)(?<!\$)((?P<d>\$+)(?P=d))?((?<=\$)(?!\$)|(\$([a-f\d]{1,3}|[ionmwsztg<>]|[lhp](\[[^\]]+\])?)))"
    SUBST = ""

    if isinstance(text, NoneType):
        return None

    return re.sub(REGEX, SUBST, text)
