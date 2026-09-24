from types import SimpleNamespace
from dataclasses import dataclass
from Options import PerGameCommonOptions, Choice


class Goal(Choice):
    """Determines what your goal is to consider the game beaten."""
    display_name = "Goal"
    option_ghetsis = 0
    default = 0


@dataclass
class PokemonTHTOriginsOptions(PerGameCommonOptions):
    goal: Goal


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
