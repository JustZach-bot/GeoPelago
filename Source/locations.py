"""Location definitions for GeoPelago. Names must match the website exactly."""

BRACKETS = ("0-1999", "2000-2999", "3000-3999", "4000-5000")
MAX_CHECKS = 999          # most checks allowed in any one bracket (and for Correct Country)
MIN_TOTAL_CHECKS = 250    # fewest checks allowed across everything
DEFAULT_CHECKS = 50       # 5 groups x 50 = 250


def points_name(bracket: str, n: int) -> str:
    return f"Points {bracket} #{n}"


def country_name(n: int) -> str:
    return f"Correct Country #{n}"


# Every possible location is registered; the options decide how many of each are active.
LOCATION_NAME_TO_ID = {}
for _b, _bracket in enumerate(BRACKETS):
    for _n in range(1, MAX_CHECKS + 1):
        LOCATION_NAME_TO_ID[points_name(_bracket, _n)] = _b * MAX_CHECKS + _n
for _n in range(1, MAX_CHECKS + 1):
    LOCATION_NAME_TO_ID[country_name(_n)] = len(BRACKETS) * MAX_CHECKS + _n
