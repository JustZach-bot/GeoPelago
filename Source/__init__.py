from typing import Any, Dict, List

from BaseClasses import Item, ItemClassification, Location, Region, Tutorial
from Options import OptionError
from worlds.AutoWorld import WebWorld, World

from .items import COUNTRY_NAMES, FILLER_ITEM, GATE_ITEMS, ITEM_NAME_TO_ID
from .locations import (BRACKETS, DEFAULT_CHECKS, LOCATION_NAME_TO_ID, MAX_CHECKS,
                        MIN_STARTER_CHECKS, MIN_TOTAL_CHECKS, country_name, points_name)
from .options import GeoPelagoOptions

GAME = "GeoPelago"
VERSION = "GeoPelago 0.6.0"


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
    GeoPelago 0.6.0 is a geography guessing game. Guess where you are in the world to
    send checks. Each country must be unlocked by finding its item before you can
    guess in it, and the higher score brackets and the Correct Country checks have
    their own unlock items. Unlock enough countries to win.
    """
    game = GAME
    web = GeoPelagoWeb()
    options_dataclass = GeoPelagoOptions
    options: GeoPelagoOptions
    topology_present = False

    item_name_to_id = ITEM_NAME_TO_ID
    location_name_to_id = LOCATION_NAME_TO_ID
    item_name_groups = {"Countries": set(COUNTRY_NAMES), "Unlocks": set(GATE_ITEMS.values())}

    pool: List[str]
    starting: List[str]
    counts: Dict[str, int]   # active checks per group: each bracket, plus "country"
    gates: List[str]         # unlock items that are in this game (empty when lock_checks is off)
    lock: bool               # False = solo mode: every check is open from the start
    required: int

    def _fail(self, msg: str) -> None:
        raise OptionError(f"GeoPelago ({self.player_name}): {msg}")

    @staticmethod
    def _names(key: str, amount: int) -> List[str]:
        if key == "country":
            return [country_name(i) for i in range(1, amount + 1)]
        return [points_name(key, i) for i in range(1, amount + 1)]

    def generate_early(self) -> None:
        opts = self.options

        self.pool = list(COUNTRY_NAMES)   # every country is in the pool

        chosen = sorted(opts.starting_country_list.value)
        if chosen:
            self.starting = chosen
        else:
            count = min(opts.starting_countries.value, len(self.pool))
            self.starting = self.random.sample(self.pool, count)

        self.required = opts.countries_required.value
        if self.required > len(self.pool):
            self._fail(f"countries_required is {self.required} but only {len(self.pool)} countries are in the pool.")
        if self.required <= len(self.starting):
            self._fail(f"countries_required ({self.required}) must be higher than your "
                       f"{len(self.starting)} starting countries.")

        self.counts = {}
        for bracket in BRACKETS:
            amount = int(opts.score_checks.value.get(bracket, DEFAULT_CHECKS))
            if not 0 <= amount <= MAX_CHECKS:
                self._fail(f"score_checks for {bracket} must be between 0 and {MAX_CHECKS}.")
            self.counts[bracket] = amount
        self.counts["country"] = opts.country_checks.value

        total = sum(self.counts.values())
        if total < MIN_TOTAL_CHECKS:
            self._fail(f"you have {total} checks in total but at least {MIN_TOTAL_CHECKS} are required.")
        self.lock = bool(opts.lock_checks.value)
        if self.lock and self.counts["0-999"] < MIN_STARTER_CHECKS:
            self._fail(f"the 0-999 bracket is the only one open at the start, so it needs at least "
                       f"{MIN_STARTER_CHECKS} checks.")

        # Only groups that actually have checks get an unlock item.
        self.gates = [item for key, item in GATE_ITEMS.items() if self.lock and self.counts[key] > 0]

        to_place = len(self.pool) - len(self.starting) + len(self.gates)
        if total < to_place:
            self._fail(f"{to_place} items need homes but only {total} checks are active. "
                       "Raise your check counts or start with more countries.")

    def create_item(self, name: str) -> Item:
        if name in COUNTRY_NAMES or name in GATE_ITEMS.values():
            cls = ItemClassification.progression
        else:
            cls = ItemClassification.filler
        return GeoPelagoItem(name, cls, self.item_name_to_id[name], self.player)

    def get_filler_item_name(self) -> str:
        return FILLER_ITEM

    def create_regions(self) -> None:
        # Logic for the checks:
        #   - 0-999 checks are in the Menu region, open from the start.
        #   - Each other group (1000-1999, 2000-2999, 3000-3999, 4000-5000, Correct Country) is its own region that can only be
        #     entered once its unlock item has been found.
        menu = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(menu)
        for key in (*BRACKETS, "country"):
            amount = self.counts[key]
            if amount <= 0:
                continue
            gate = GATE_ITEMS.get(key) if self.lock else None   # lock_checks off: everything is open
            if gate is None:
                region = menu
            else:
                region = Region(f"{key} checks", self.player, self.multiworld)
                self.multiworld.regions.append(region)
                menu.connect(region, f"Unlock {key}",
                             lambda state, item=gate: state.has(item, self.player))
            for name in self._names(key, amount):
                region.locations.append(
                    GeoPelagoLocation(self.player, name, self.location_name_to_id[name], region))

    def create_items(self) -> None:
        for name in self.starting:
            self.multiworld.push_precollected(self.create_item(name))
        pool = [self.create_item(n) for n in self.pool if n not in self.starting]
        pool += [self.create_item(n) for n in self.gates]
        filler = sum(self.counts.values()) - len(pool)
        pool += [self.create_item(FILLER_ITEM) for _ in range(filler)]
        self.multiworld.itempool += pool

    def set_rules(self) -> None:
        names = list(self.pool)
        required = self.required
        player = self.player
        self.multiworld.completion_condition[player] = \
            lambda state: sum(1 for n in names if state.has(n, player)) >= required

    def fill_slot_data(self) -> Dict[str, Any]:
        # The website reads these: the country pool, how many countries finish the game, and which check groups
        # need an unlock item (so it knows to hold back those checks until the item arrives).
        return {"countries": list(self.pool),
                "countries_required": self.required,
                "starting_countries": list(self.starting),
                "gated_categories": [key for key in GATE_ITEMS if self.lock and self.counts[key] > 0],
                "version": VERSION}
