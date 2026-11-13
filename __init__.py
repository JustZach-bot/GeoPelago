from typing import Any, Dict, List

from BaseClasses import Item, ItemClassification, Location, Region, Tutorial
from Options import OptionError
from worlds.AutoWorld import WebWorld, World

from .items import COUNTRY_NAMES, FILLER_ITEM, ITEM_NAME_TO_ID
from .locations import (BRACKETS, CHECKS_PER_BRACKET, LOCATION_NAME_TO_ID,
                        MAX_COUNTRY_CHECKS, country_name, points_name)
from .options import GeoPelagoOptions

GAME = "GeoPelago"


class GeoPelagoItem(Item):
    game = GAME


class GeoPelagoLocation(Location):
    game = GAME


class GeoPelagoWeb(WebWorld):
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "How to play GeoPelago with the GeoPelago website.",
        "English",
        "setup_en.md",
        "setup/en",
        ["GeoPelago"],
    )]


class GeoPelagoWorld(World):
    """
    GeoPelago is a geography guessing game. Guess where you are in the world to
    send checks. Each country must be unlocked by finding its item before you can
    guess in it. Unlock every country to win.
    """
    game = GAME
    web = GeoPelagoWeb()
    options_dataclass = GeoPelagoOptions
    options: GeoPelagoOptions
    topology_present = False

    item_name_to_id = ITEM_NAME_TO_ID
    location_name_to_id = LOCATION_NAME_TO_ID
    item_name_groups = {"Countries": set(COUNTRY_NAMES)}

    pool: List[str]
    starting: List[str]
    active_locations: List[str]

    def _fail(self, msg: str) -> None:
        raise OptionError(f"GeoPelago ({self.player_name}): {msg}")

    def generate_early(self) -> None:
        opts = self.options

        excluded = set(opts.excluded_countries.value)
        self.pool = [c for c in COUNTRY_NAMES if c not in excluded]
        if not self.pool:
            self._fail("excluded_countries removes every country.")

        chosen = sorted(opts.starting_country_list.value)
        if chosen:
            bad = [c for c in chosen if c in excluded]
            if bad:
                self._fail(f"starting countries are also excluded: {', '.join(bad)}")
            self.starting = chosen
        else:
            count = min(opts.starting_countries.value, len(self.pool))
            self.starting = self.random.sample(self.pool, count)

        names: List[str] = []
        for bracket in BRACKETS:
            amount = int(opts.score_checks.value.get(bracket, CHECKS_PER_BRACKET))
            if not 0 <= amount <= CHECKS_PER_BRACKET:
                self._fail(f"score_checks for {bracket} must be between 0 and {CHECKS_PER_BRACKET}.")
            names += [points_name(bracket, i) for i in range(1, amount + 1)]
        names += [country_name(i) for i in range(1, opts.country_checks.value + 1)]
        self.active_locations = names

        to_place = len(self.pool) - len(self.starting)
        if len(self.active_locations) < to_place:
            self._fail(f"{to_place} country items need homes but only "
                       f"{len(self.active_locations)} checks are active. "
                       "Raise your check counts, start with more countries, or exclude some.")

    def create_item(self, name: str) -> Item:
        cls = ItemClassification.progression if name in COUNTRY_NAMES else ItemClassification.filler
        return GeoPelagoItem(name, cls, self.item_name_to_id[name], self.player)

    def get_filler_item_name(self) -> str:
        return FILLER_ITEM

    def create_regions(self) -> None:
        menu = Region("Menu", self.player, self.multiworld)
        for name in self.active_locations:
            menu.locations.append(
                GeoPelagoLocation(self.player, name, self.location_name_to_id[name], menu))
        self.multiworld.regions.append(menu)

    def create_items(self) -> None:
        for name in self.starting:
            self.multiworld.push_precollected(self.create_item(name))
        pool = [self.create_item(n) for n in self.pool if n not in self.starting]
        filler = len(self.active_locations) - len(pool)
        pool += [self.create_item(FILLER_ITEM) for _ in range(filler)]
        self.multiworld.itempool += pool

    def set_rules(self) -> None:
        needed = list(self.pool)
        self.multiworld.completion_condition[self.player] = \
            lambda state: state.has_all(needed, self.player)

    def fill_slot_data(self) -> Dict[str, Any]:
        # The website reads "countries" to know which countries count toward the goal.
        return {"countries": list(self.pool), "starting_countries": list(self.starting)}
