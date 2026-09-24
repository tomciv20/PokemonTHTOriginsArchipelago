from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

if TYPE_CHECKING:
    from . import PokemonTHTOriginsWorld

_all_items_view = None


class PokemonTHTOriginsItem(Item):
    game = "Pokemon THT Origins"


def _get_all_items():
    global _all_items_view
    if _all_items_view is None:
        from .data.items import all_items_dict_view
        _all_items_view = all_items_dict_view
    return _all_items_view


def get_item_lookup_table() -> dict[str, int]:
    return {name: data.item_id for name, data in _get_all_items().items()}


def generate_item(name: str, world: "PokemonTHTOriginsWorld") -> PokemonTHTOriginsItem:
    if name == "Victory":
        return PokemonTHTOriginsItem(name, ItemClassification.progression, None, world.player)
    data = _get_all_items()[name]
    return PokemonTHTOriginsItem(name, data.classification(world), world.item_name_to_id[name], world.player)


def get_main_item_pool(world: "PokemonTHTOriginsWorld") -> list[PokemonTHTOriginsItem]:
    from .data.items.badges import table as badge_table
    from .data.items.key_items import progression, vanilla, special as key_special
    from .data.items.medicine import important as med_important
    from .data.items.tm_hm import tm, hm
    from .data.items.main_items import min_once, fossils

    pool: list[PokemonTHTOriginsItem] = []

    for name, data in badge_table.items():
        pool.append(PokemonTHTOriginsItem(name, data.classification(world), data.item_id, world.player))

    for name, data in {**progression, **vanilla, **med_important}.items():
        pool.append(PokemonTHTOriginsItem(name, data.classification(world), data.item_id, world.player))

    pool.append(generate_item("Xtransceiver (Blue)", world))
    pool.append(generate_item("Light Stone", world))

    for name, data in {**tm, **hm}.items():
        pool.append(PokemonTHTOriginsItem(name, data.classification(world), data.item_id, world.player))

    for name, data in {**min_once, **fossils}.items():
        pool.append(PokemonTHTOriginsItem(name, data.classification(world), data.item_id, world.player))

    return pool


def generate_filler(world: "PokemonTHTOriginsWorld") -> str:
    from .data.items.main_items import filler
    return world.random.choice(list(filler.keys()))
