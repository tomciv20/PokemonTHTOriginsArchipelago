import logging
import math
from typing import TYPE_CHECKING, Any, Coroutine, Callable

from NetUtils import ClientStatus

import worlds._bizhawk as bizhawk
from worlds._bizhawk.client import BizHawkClient
from .client.locations import check_flag_locations
from .client.items import receive_items, enforce_key_item_gating, enforce_tm_hm_gating, items_synced
from .client.setup import early_setup, late_setup

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext


def register_client():
    """Make this client the first one BizHawk tries for NDS ROMs.

    Handlers are tried in registration order, and the official Pokemon Black and White world (if installed)
    would otherwise claim an unpatched Pokemon Black based ROM before this client gets a look. This client
    hands patched vanilla BW ROMs back to it (see validate_rom), so both worlds keep working side by side.
    """
    from worlds._bizhawk.client import AutoBizHawkClientRegister

    for handlers in AutoBizHawkClientRegister.game_handlers.values():
        if PokemonTHTOriginsClient.game in handlers:
            ours = handlers.pop(PokemonTHTOriginsClient.game)
            others = dict(handlers)
            handlers.clear()
            handlers[PokemonTHTOriginsClient.game] = ours
            handlers.update(others)


class PokemonTHTOriginsClient(BizHawkClient):
    game = "Pokemon THT Origins"
    system = "NDS"
    # No patch_suffix — accepts the raw .nds ROM directly

    ram_read_write_domain = "Main RAM"
    rom_read_only_domain = "ROM"
    flags_amount = 2912
    flag_bytes_amount = math.ceil(flags_amount / 8)
    main_items_bag_size = 1240 // 4   # 310
    key_items_bag_size = 332 // 4     # 83
    tm_hm_bag_size = 436 // 4         # 109
    medicine_bag_size = 192 // 4      # 48
    berry_bag_size = 256 // 4         # 64

    data_address_address = 0x000024
    ingame_state_address = 0x000034
    header_address = 0x3ffa80
    var_offset = 0x209BC
    flags_offset = 0x20C38
    main_items_bag_offset = 0x18cbc
    key_items_bag_offset = 0x19194
    tm_hm_bag_offset = 0x192e0
    medicine_bag_offset = 0x19494
    berry_bag_offset = 0x19554
    badges_offset = 0x21ac0

    def __init__(self):
        super().__init__()
        self.flags_cache: bytearray = bytearray(self.flag_bytes_amount)
        self.dexsanity_included: bool = False
        self.player_name: str | None = None
        self.missing_flag_loc_ids: list[list[int]] = [[] for _ in range(self.flags_amount)]
        self.save_data_address = 0
        self.late_setup_done: bool = False
        self.goal_checking_method: Callable[["PokemonTHTOriginsClient", "BizHawkClientContext"],
                                            Coroutine[Any, Any, bool]] | None = None
        self.logger = logging.getLogger("Client")

    async def validate_rom(self, ctx: "BizHawkClientContext") -> bool:
        try:
            header = await bizhawk.read(
                ctx.bizhawk_ctx, (
                    (self.header_address, 0xc0, self.ram_read_write_domain),
                )
            )
        except Exception:
            return False

        # Must be Pokemon Black base ROM (IRBO01)
        if not header[0][:18].startswith(b'POKEMON B\0\0\0IRBO01'):
            return False

        # A ROM patched by the official Pokemon Black and White world stores its player name (UTF-8) at
        # offset 0xa0. THT Origins is unpatched, so that area is empty - leave anything with a name to the
        # official client.
        name_area = header[0][0xa0:].strip(b'\0')
        if name_area:
            try:
                name_area.decode()
                return False
            except UnicodeDecodeError:
                pass

        ctx.game = self.game
        ctx.items_handling = 0b111
        ctx.want_slot_data = True
        ctx.watcher_timeout = 1
        return True

    def on_package(self, ctx: "BizHawkClientContext", cmd: str, args: dict) -> None:
        if cmd == "Connected":
            from .data.locations import all_item_locations
            self.missing_flag_loc_ids = [[] for _ in range(self.flags_amount)]
            self.late_setup_done = False
            for loc_id in ctx.missing_locations:
                loc_name = ctx.location_names.lookup_in_game(loc_id)
                if loc_name in all_item_locations:
                    self.missing_flag_loc_ids[all_item_locations[loc_name].flag_id].append(loc_id)
                else:
                    self.logger.warning(f"Unknown location: {loc_name!r}")
        elif cmd == "RoomInfo":
            ctx.seed_name = args["seed_name"]

    async def game_watcher(self, ctx: "BizHawkClientContext") -> None:
        try:
            if (
                not ctx.server or
                not ctx.server.socket.open or
                ctx.server.socket.closed or
                ctx.slot_data is None
            ):
                return

            read = await bizhawk.read(
                ctx.bizhawk_ctx, (
                    (self.ingame_state_address, 1, self.ram_read_write_domain),
                )
            )
            if read[0][0] == 0:
                return

            if self.save_data_address == 0:
                await early_setup(self, ctx)

            locations_to_check = await check_flag_locations(self, ctx)
            if locations_to_check:
                await ctx.send_msgs([{"cmd": "LocationChecks", "locations": list(locations_to_check)}])

            await receive_items(self, ctx)

            # Right after connecting, ctx.items_received can still be empty (or partial) while the save already
            # remembers how many items it was given. Acting on that would treat legitimately received items as
            # unauthorized, so wait until the server's item list has caught up with the save.
            if await items_synced(self, ctx):
                if not self.late_setup_done:
                    await late_setup(self, ctx)
                    self.late_setup_done = True
                await enforce_key_item_gating(self, ctx)
                await enforce_tm_hm_gating(self, ctx)

            if await self.goal_checking_method(self, ctx):
                await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])

        except bizhawk.RequestFailedError:
            pass
        except bizhawk.ConnectorError:
            pass

    def get_flag(self, flag: int) -> bool:
        return (self.flags_cache[flag // 8] & (2 ** (flag % 8))) != 0

    async def write_set_flag(self, ctx: "BizHawkClientContext", flag: int) -> None:
        while not await bizhawk.guarded_write(
            ctx.bizhawk_ctx, ((
                self.save_data_address + self.flags_offset + (flag // 8),
                [self.flags_cache[flag // 8] | (2 ** (flag % 8))],
                self.ram_read_write_domain
            ),), ((
                self.save_data_address + self.flags_offset + (flag // 8),
                [self.flags_cache[flag // 8]],
                self.ram_read_write_domain
            ),)
        ):
            self.flags_cache[flag // 8] = (await bizhawk.read(
                ctx.bizhawk_ctx, (
                    (self.save_data_address + self.flags_offset + (flag // 8), 1, self.ram_read_write_domain),
                )
            ))[0][0]
        self.flags_cache[flag // 8] |= (2 ** (flag % 8))

    async def write_unset_flag(self, ctx: "BizHawkClientContext", flag: int) -> None:
        while not await bizhawk.guarded_write(
            ctx.bizhawk_ctx, ((
                self.save_data_address + self.flags_offset + (flag // 8),
                [self.flags_cache[flag // 8] & (255 - (2 ** (flag % 8)))],
                self.ram_read_write_domain
            ),), ((
                self.save_data_address + self.flags_offset + (flag // 8),
                [self.flags_cache[flag // 8]],
                self.ram_read_write_domain
            ),)
        ):
            self.flags_cache[flag // 8] = (await bizhawk.read(
                ctx.bizhawk_ctx, (
                    (self.save_data_address + self.flags_offset + (flag // 8), 1, self.ram_read_write_domain),
                )
            ))[0][0]
        self.flags_cache[flag // 8] &= (255 - (2 ** (flag % 8)))

    async def write_var(self, ctx: "BizHawkClientContext", var: int, value: int, length: int = 2) -> None:
        await bizhawk.write(
            ctx.bizhawk_ctx, ((
                self.save_data_address + self.var_offset + (2 * var),
                value.to_bytes(length, "little"),
                self.ram_read_write_domain
            ),)
        )

    async def read_var(self, ctx: "BizHawkClientContext", var: int, length: int = 2) -> int:
        return int.from_bytes((await bizhawk.read(
            ctx.bizhawk_ctx, (
                (self.save_data_address + self.var_offset + (2 * var), length, self.ram_read_write_domain),
            )
        ))[0], "little")
