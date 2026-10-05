from types import SimpleNamespace
from dataclasses import dataclass
from Options import PerGameCommonOptions, Choice, DefaultOnToggle, Toggle


class Goal(Choice):
    """Determines what your goal is to consider the game beaten."""
    display_name = "Goal"
    option_ghetsis = 0
    default = 0


class IncludeOverworldItems(DefaultOnToggle):
    """Whether items lying on the ground (277 locations) are checks. Turn off to have far fewer checks."""
    display_name = "Include Overworld Items"


class IncludeHiddenItems(DefaultOnToggle):
    """Whether items found with the Dowsing Machine (131 locations) are checks. Turn off to have far fewer checks."""
    display_name = "Include Hidden Items"


class IncludeNpcGifts(DefaultOnToggle):
    """Whether items and TMs/HMs given by NPCs and events (103 locations) are checks."""
    display_name = "Include NPC Gifts"


class IncludePostgameChecks(Toggle):
    """
    Whether locations that are only reachable after finishing the story (Routes 11 to 15, Undella Town, Giant Chasm,
    the Abyssal Ruins, Abundant Shrine, Challenger's Cave, Battle Company, ...) are checks. Off by default. If you turn it on they can only hold filler items, because
    anything useful placed there would leave other players waiting until you have finished your game.
    """
    display_name = "Include Postgame Checks"


@dataclass
class PokemonTHTOriginsOptions(PerGameCommonOptions):
    goal: Goal
    include_overworld_items: IncludeOverworldItems
    include_hidden_items: IncludeHiddenItems
    include_npc_gifts: IncludeNpcGifts
    include_postgame_checks: IncludePostgameChecks


# Class-level stubs so vanilla BW rules.py can access these without error
_stub_off = SimpleNamespace(
    is_randomize=False,
    is_require_flash=False,
    is_require_dowsing=False,
    is_useless_key_items=False,
    is_useful_filler=False,
    is_ban_bad_filler=False,
    is_consider_static=False,
    is_consider_trades=False,
    is_consider_evos=False,
)
PokemonTHTOriginsOptions.all_pokemon_seen = True          # type: ignore[attr-defined]
PokemonTHTOriginsOptions.season_control = "vanilla"       # type: ignore[attr-defined]
PokemonTHTOriginsOptions.modify_logic = _stub_off         # type: ignore[attr-defined]
PokemonTHTOriginsOptions.randomize_wild_pokemon = _stub_off  # type: ignore[attr-defined]
PokemonTHTOriginsOptions.modify_item_pool = _stub_off     # type: ignore[attr-defined]
PokemonTHTOriginsOptions.dexsanity = 0                    # type: ignore[attr-defined]
PokemonTHTOriginsOptions.version = SimpleNamespace(current_key="black")  # type: ignore[attr-defined]
