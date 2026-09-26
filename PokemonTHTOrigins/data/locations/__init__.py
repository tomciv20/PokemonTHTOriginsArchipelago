from .ingame_items import overworld_items, hidden_items, other, special
from typing import TYPE_CHECKING
from collections import ChainMap

if TYPE_CHECKING:
    from .. import AnyLocationData, TMLocationData

# Flags 0x172-0x1DF are custom flags that vanilla Pokemon BW's Archipelago ROM patch adds to the game's
# scripts (gym badge rewards, most NPC gifts, the goal flags, ...). An unpatched ROM never sets them, so a
# location tied to one could never be checked. Verified by scanning the script archive (a/0/5/7): the
# set-flag command references none of them in vanilla Black or in THT Origins, only in the AP-patched ROM.
PATCH_ONLY_FLAGS = range(0x172, 0x1E0)

# Flags in that range that the THT Origins ROM sets itself (i.e. the hack's scripts contain a set-flag for
# them). Add a flag here once the hack sets it, and the locations that use it come back into the world.
HACK_SET_FLAGS: frozenset[int] = frozenset()


def is_checkable_unpatched(data: "AnyLocationData") -> bool:
    return data.flag_id not in PATCH_ONLY_FLAGS or data.flag_id in HACK_SET_FLAGS


all_tm_locations: ChainMap[str, "TMLocationData"] = ChainMap[str, "TMLocationData"](
    special.gym_tms,
    special.tm_hm_ncps,
)

all_item_locations: ChainMap[str, "AnyLocationData"] = ChainMap[str, "AnyLocationData"](
    overworld_items.table,
    overworld_items.abyssal_ruins,
    hidden_items.table,
    other.table,
    special.gym_badges,
    special.gym_tms,
    special.tm_hm_ncps,
)
