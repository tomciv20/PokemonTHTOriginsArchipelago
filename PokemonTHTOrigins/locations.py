from typing import TYPE_CHECKING, Callable

from BaseClasses import Location, Region, CollectionState

if TYPE_CHECKING:
    from . import PokemonTHTOriginsWorld
    from .data import ExtendedRule


class PokemonTHTOriginsLocation(Location):
    game = "Pokemon THT Origins"


def get_location_lookup_table() -> dict[str, int]:
    from .data.locations.ingame_items.overworld_items import table, abyssal_ruins
    from .data.locations.ingame_items.hidden_items import table as hidden_table
    from .data.locations.ingame_items.other import table as other_table
    from .data.locations.ingame_items.special import gym_badges, gym_tms, tm_hm_ncps
    from .data.locations import is_checkable_unpatched

    result: dict[str, int] = {}

    for name, data in {**table, **abyssal_ruins}.items():
        result[name] = data.flag_id + 100000

    for name, data in hidden_table.items():
        result[name] = data.flag_id + 200000

    for name, data in other_table.items():
        result[name] = data.flag_id * 100 + 300000 + (
            int(name[-2:].split("#")[-1]) if "#" in name[-3:] else 0
        )

    for name, data in gym_badges.items():
        result[name] = data.flag_id + 400000

    for name, data in {**gym_tms, **tm_hm_ncps}.items():
        result[name] = data.flag_id + 500000

    every = {**table, **abyssal_ruins, **hidden_table, **other_table, **gym_badges, **gym_tms, **tm_hm_ncps}
    return {name: loc_id for name, loc_id in result.items() if is_checkable_unpatched(every[name])}


def get_regions(world: "PokemonTHTOriginsWorld") -> dict[str, Region]:
    from .data.locations.regions import region_list

    return {
        name: Region(name, world.player, world.multiworld)
        for name in region_list
    }


def create_rule_dict(world: "PokemonTHTOriginsWorld") -> dict:
    from .data.locations.rules import extended_rules_list

    def f(r: "ExtendedRule"):
        return lambda state: r(state, world)

    return {rule: f(rule) for rule in extended_rules_list} | {None: None}


def connect_regions(world: "PokemonTHTOriginsWorld") -> None:
    from .data.locations import region_connections as gameplay_connections

    for name, data in gameplay_connections.connections.items():
        if data.exiting_region in world.regions and data.entering_region in world.regions:
            world.regions[data.exiting_region].connect(
                world.regions[data.entering_region], name, world.rules_dict[data.rule]
            )



def create_and_place_locations(world: "PokemonTHTOriginsWorld") -> None:
    from .data.locations.ingame_items.overworld_items import table, abyssal_ruins
    from .data.locations.ingame_items.hidden_items import table as hidden_table
    from .data.locations.ingame_items.other import table as other_table
    from .data.locations.ingame_items.special import gym_badges, gym_tms, tm_hm_ncps
    from .data.locations import is_checkable_unpatched

    options = world.options
    all_tables = [
        (table, options.include_overworld_items),
        (abyssal_ruins, options.include_overworld_items),
        (hidden_table, options.include_hidden_items),
        (other_table, options.include_npc_gifts),
        (gym_badges, options.include_npc_gifts),
        (gym_tms, options.include_npc_gifts),
        (tm_hm_ncps, options.include_npc_gifts),
    ]

    for tab, included in all_tables:
        if not included:
            continue
        for name, data in tab.items():
            if data.inclusion_rule is not None and not data.inclusion_rule(world):
                continue
            if not is_checkable_unpatched(data):
                continue
            if data.region not in world.regions:
                continue
            r: Region = world.regions[data.region]
            loc_id = world.location_name_to_id.get(name)
            if loc_id is None:
                continue
            loc = PokemonTHTOriginsLocation(world.player, name, loc_id, r)
            loc.progress_type = data.progress_type(world)
            if data.rule is not None:
                loc.access_rule = world.rules_dict.get(data.rule)
            r.locations.append(loc)


def create_goal_location(world: "PokemonTHTOriginsWorld") -> None:
    from BaseClasses import LocationProgressType

    menu = world.regions["Menu"]
    goal = PokemonTHTOriginsLocation(world.player, "Defeat Ghetsis", None, menu)
    goal.progress_type = LocationProgressType.DEFAULT
    goal.place_locked_item(world.create_item("Victory"))
    menu.locations.append(goal)


def count_to_be_filled_locations(regions: dict[str, Region]) -> int:
    return sum(
        1 for region in regions.values()
        for loc in region.locations
        if loc.item is None
    )
