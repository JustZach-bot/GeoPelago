"""Location definitions for GeoPelago. Names must match the website exactly."""
from .items import BASE_ID

BRACKETS = ("0-1999", "2000-2999", "3000-3999", "4000-5000")
CHECKS_PER_BRACKET = 25
MAX_COUNTRY_CHECKS = 50


def points_name(bracket: str, n: int) -> str:
    return f"Points {bracket} #{n}"


def country_name(n: int) -> str:
    return f"Correct Country #{n}"


LOCATION_NAME_TO_ID = {}
for _b, _bracket in enumerate(BRACKETS):
    for _n in range(1, CHECKS_PER_BRACKET + 1):
        LOCATION_NAME_TO_ID[points_name(_bracket, _n)] = BASE_ID + 1000 + _b * 100 + _n
for _n in range(1, MAX_COUNTRY_CHECKS + 1):
    LOCATION_NAME_TO_ID[country_name(_n)] = BASE_ID + 2000 + _n
