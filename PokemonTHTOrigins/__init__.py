from typing import ClassVar, Mapping, Any

from BaseClasses import MultiWorld, Item, ItemClassification, LocationProgressType
from Options import OptionError

from worlds.AutoWorld import World, WebWorld
from . import options, locations, items, bizhawk_client as _bizhawk_client

_bizhawk_client.register_client()


class PokemonTHTOriginsWebWorld(WebWorld):
    theme = "ocean"


class PokemonTHTOriginsWorld(World):
    """
    Pokemon THT Origins is a custom Pokemon Black romhack. Travel through Unova,
    collect items shuffled across the multiworld, and defeat Jonah (Ghetsis) to win.
    """
    game = "Pokemon THT Origins"
    options_dataclass = options.PokemonTHTOriginsOptions
    options: options.PokemonTHTOriginsOptions
    topology_present = True
    web = PokemonTHTOriginsWebWorld()
    item_name_to_id: ClassVar[dict[str, int]] = items.get_item_lookup_table()
    location_name_to_id: ClassVar[dict[str, int]] = locations.get_location_lookup_table()

    def __init__(self, multiworld: MultiWorld, player: int):
        super().__init__(multiworld, player)
        self.regions: dict | None = None
        self.rules_dict: dict | None = None
        self.to_be_filled_locations: int = 0
        # Stub sets for HM-access rules; using HM name means "can use if you have the HM"
        self.surf_species: set = {"HM03 Surf"}
        self.strength_species: set = {"HM04 Strength"}
        self.cut_species: set = {"HM01 Cut"}
        self.waterfall_species: set = {"HM05 Waterfall"}
        self.dive_species: set = {"HM06 Dive"}
        self.flash_species: set = {"TM70 Flash"}
        # Fighting type species: use Trio Badge as a proxy (obtained before Pinwheel Forest)
        self.fighting_type_species: set = {"Trio Badge"}

    def generate_early(self) -> None:
        if not (self.options.include_overworld_items or self.options.include_hidden_items
                or self.options.include_npc_gifts):
            raise OptionError(f"{self.player_name}: at least one of Include Overworld Items, Include Hidden Items "
                              f"and Include NPC Gifts must be on")
        self.regions = locations.get_regions(self)
        self.rules_dict = locations.create_rule_dict(self)
        locations.connect_regions(self)

        # Remove unreachable regions
        to_remove = [name for name, region in self.regions.items()
                     if len(region.entrances) == 0 and name != "Menu"]
        for name in to_remove:
            self.regions.pop(name)

    def create_regions(self) -> None:
        locations.create_and_place_locations(self)
        locations.create_goal_location(self)
        self.to_be_filled_locations = locations.count_to_be_filled_locations(self.regions)
        self.multiworld.regions.extend(self.regions.values())

        # Register indirect conditions after regions are in the multiworld
        try:
            entrance = self.multiworld.get_entrance("Relic Castle B5F castleside", self.player)
            if entrance is not None and "N's Castle" in self.regions:
                self.multiworld.register_indirect_condition(self.regions["N's Castle"], entrance)
        except Exception:
            pass

    def create_item(self, name: str) -> Item:
        return items.generate_item(name, self)

    def get_filler_item_name(self) -> str:
        return items.generate_filler(self)

    def create_items(self) -> None:
        item_pool = items.get_main_item_pool(self)

        # Deduplicate by name (some data tables may have overlaps)
        seen_names: set[str] = set()
        deduped: list[Item] = []
        for item in item_pool:
            if item.name not in seen_names:
                seen_names.add(item.name)
                deduped.append(item)
        item_pool = deduped

        if len(item_pool) > self.to_be_filled_locations:
            # Fewer locations than curated items (some location groups turned off): drop the least important
            # ones first, so everything the logic needs is always kept. Excluded locations can only hold filler,
            # so leave room for that as well.
            excluded = sum(1 for location in self.multiworld.get_unfilled_locations(self.player)
                           if location.progress_type == LocationProgressType.EXCLUDED)
            item_pool.sort(key=lambda item: 0 if item.advancement else (1 if item.useful else 2))
            item_pool = item_pool[:max(0, self.to_be_filled_locations - excluded)]
        while len(item_pool) < self.to_be_filled_locations:
            item_pool.append(self.create_item(self.get_filler_item_name()))

        self.multiworld.itempool.extend(item_pool)

    def set_rules(self) -> None:
        from BaseClasses import CollectionState

        def goal_rule(state: CollectionState) -> bool:
            return state.can_reach_region("N's Castle", self.player)

        self.multiworld.completion_condition[self.player] = goal_rule

    def generate_output(self, output_directory: str) -> None:
        pass  # No ROM patching needed

    def fill_slot_data(self) -> Mapping[str, Any]:
        return {
            "options": {
                "goal": "ghetsis",
                "dexsanity": 0,
            }
        }
