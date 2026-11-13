from dataclasses import dataclass

from Options import OptionDict, OptionSet, PerGameCommonOptions, Range

from .items import COUNTRY_NAMES
from .locations import BRACKETS, CHECKS_PER_BRACKET, MAX_COUNTRY_CHECKS


class StartingCountries(Range):
    """How many random countries are unlocked from the start.
    Ignored if you list your own starting countries."""
    display_name = "Starting Countries"
    range_start = 1
    range_end = 10
    default = 3


class StartingCountryList(OptionSet):
    """Choose exactly which countries you start with instead of random ones."""
    display_name = "Starting Country List"
    valid_keys = frozenset(COUNTRY_NAMES)


class ExcludedCountries(OptionSet):
    """Countries that never appear in the item pool. They are also not needed for your goal."""
    display_name = "Excluded Countries"
    valid_keys = frozenset(COUNTRY_NAMES)


class ScoreChecks(OptionDict):
    """How many score checks are active in each bracket (0-25 each).
    Brackets: 0-1999, 2000-2999, 3000-3999, 4000-5000."""
    display_name = "Score Checks"
    valid_keys = frozenset(BRACKETS)
    default = {bracket: CHECKS_PER_BRACKET for bracket in BRACKETS}


class CountryChecks(Range):
    """How many 'Correct Country' checks are active (0-50)."""
    display_name = "Country Checks"
    range_start = 0
    range_end = MAX_COUNTRY_CHECKS
    default = MAX_COUNTRY_CHECKS


@dataclass
class GeoPelagoOptions(PerGameCommonOptions):
    starting_countries: StartingCountries
    starting_country_list: StartingCountryList
    excluded_countries: ExcludedCountries
    score_checks: ScoreChecks
    country_checks: CountryChecks
