
from typing import TYPE_CHECKING
import worlds._bizhawk as bizhawk
from ..data.items import all_main_items, all_key_items, all_berries, badges, seasons, all_items_dict_view, all_medicine, all_tm_hm, medicine
from ..data.items.key_items import progression as key_progression, vanilla as key_vanilla, special as key_special

if TYPE_CHECKING:
    from ..bizhawk_client import PokemonTHTOriginsClient
    from worlds._bizhawk.context import BizHawkClientContext

# Items that are part of the AP item pool (see items.py:get_main_item_pool) and therefore must not
# be usable until the player has actually received them from the multiworld. Since THT Origins isn't
# ROM-patched, the vanilla game still hands these out itself at their original story beats, so the
# client has to strip them back out of the relevant bag whenever the game grants one early.
_gated_key_item_ids: set[int] | None = None
_gated_tm_hm_ids: set[int] | None = None


def _get_gated_key_item_ids() -> set[int]:
    global _gated_key_item_ids
    if _gated_key_item_ids is None:
        ids = {data.item_id for data in key_progression.values()}
        ids |= {data.item_id for data in key_vanilla.values()}
        ids.add(key_special["Light Stone"].item_id)
        ids.add(key_special["Xtransceiver (Blue)"].item_id)
        # Dragon Skull is a forced vanilla grant-then-steal sequence (Pinwheel Forest: picked up,
        # then immediately taken by a Team Plasma grunt to open Skyarrow Bridge) - every player
        # triggers it regardless of AP state. Stripping it mid-sequence could interfere with the
        # vanilla script's own removal step and soft-lock the player, so it's exempt from gating.
        ids.discard(key_progression["Dragon Skull"].item_id)
        _gated_key_item_ids = ids
    return _gated_key_item_ids


def _get_gated_tm_hm_ids() -> set[int]:
    global _gated_tm_hm_ids
    if _gated_tm_hm_ids is None:
        _gated_tm_hm_ids = {data.item_id for data in all_tm_hm.values()}
    return _gated_tm_hm_ids


def _authorized_ids(ctx: "BizHawkClientContext", gated_ids: set[int]) -> set[int]:
    authorized: set[int] = set()
    for network_item in ctx.items_received:
        name = ctx.item_names.lookup_in_game(network_item.item)
        data = all_items_dict_view.get(name)
        if data is not None and data.item_id in gated_ids:
            authorized.add(data.item_id)
    return authorized


async def receive_items(client: "PokemonTHTOriginsClient", ctx: "BizHawkClientContext") -> None:

    received_items_count = await client.read_var(ctx, 0x126, 4)

    if received_items_count >= len(ctx.items_received):
        return

    main_items_bag_buffer: bytearray | None = None
    key_items_bag_buffer: bytearray | None = None
    medicine_bag_buffer: bytearray | None = None
    berry_bag_buffer: bytearray | None = None
    tm_hm_bag_buffer: bytearray | None = None

    new_received = received_items_count
    for index in range(received_items_count, len(ctx.items_received)):
        network_item = ctx.items_received[index]
        name = ctx.item_names.lookup_in_game(network_item.item)
        internal_id = all_items_dict_view[name].item_id
        match name:
            case x if x in all_main_items:
                if main_items_bag_buffer is None:
                    main_items_bag_buffer = await read_bag(client, ctx,
                                                           client.main_items_bag_offset, client.main_items_bag_size)
                if not await write_to_bag(client, ctx, main_items_bag_buffer, client.main_items_bag_offset,
                                          client.main_items_bag_size, internal_id, False):
                    client.logger.warning(f"Could not add {name} to main items bag, no space left. "
                                          f"Please report this to the developers.")
                    break
            case x if x in all_key_items:
                if key_items_bag_buffer is None:
                    key_items_bag_buffer = await read_bag(client, ctx,
                                                          client.key_items_bag_offset, client.key_items_bag_size)
                if not await write_to_bag(client, ctx, key_items_bag_buffer, client.key_items_bag_offset,
                                          client.key_items_bag_size, internal_id, False):
                    client.logger.warning(f"Could not add {name} to key items bag, no space left. "
                                          f"Please report this to the developers.")
                    break
            case x if x in all_berries:
                if berry_bag_buffer is None:
                    berry_bag_buffer = await read_bag(client, ctx, client.berry_bag_offset, client.berry_bag_size)
                if not await write_to_bag(client, ctx, berry_bag_buffer, client.berry_bag_offset,
                                          client.berry_bag_size, internal_id, False):
                    client.logger.warning(f"Could not add {name} to key items bag, no space left. "
                                          f"Please report this to the developers.")
                    break
            case x if x in badges.table:
                read = await bizhawk.read(
                    ctx.bizhawk_ctx, (
                        (client.save_data_address+client.badges_offset, 1, client.ram_read_write_domain),
                    )
                )
                new_state = read[0][0] | (1 << badges.table[name].bit)
                await bizhawk.write(
                    ctx.bizhawk_ctx, (
                        (client.save_data_address+client.badges_offset, [new_state], client.ram_read_write_domain),
                    )
                )
            case x if x in all_medicine:
                if medicine_bag_buffer is None:
                    medicine_bag_buffer = await read_bag(client, ctx,
                                                         client.medicine_bag_offset, client.medicine_bag_size)
                if not await write_to_bag(client, ctx, medicine_bag_buffer, client.medicine_bag_offset,
                                          client.medicine_bag_size, internal_id, False):
                    client.logger.warning(f"Could not add {name} to medicine bag, no space left. "
                                          f"Please report this to the developers.")
                    break
            case x if x in seasons.table:
                await client.write_set_flag(ctx, seasons.table[name].flag_id)
            case x if x in all_tm_hm:
                if tm_hm_bag_buffer is None:
                    tm_hm_bag_buffer = await read_bag(client, ctx, client.tm_hm_bag_offset, client.tm_hm_bag_size)
                if not await write_to_bag(client, ctx, tm_hm_bag_buffer, client.tm_hm_bag_offset,
                                          client.tm_hm_bag_size, internal_id, False):
                    client.logger.warning(f"Could not add {name} to TM/HM bag, no space left. "
                                          f"Please report this to the developers.")
                    break
            case _:
                client.logger.warning(f"Bad item name: {name}")
        new_received += 1

    if new_received > received_items_count:
        await client.write_var(ctx, 0x126, new_received, 4)


async def reload_key_items(client: "PokemonTHTOriginsClient", ctx: "BizHawkClientContext") -> None:

    read = await bizhawk.read(
        ctx.bizhawk_ctx, (
            (client.save_data_address + client.var_offset + (2*0x126), 4, client.ram_read_write_domain),
        )
    )
    received_items_count = int.from_bytes(read[0], "little")

    key_items_bag_buffer: bytearray | None = None
    medicine_bag_buffer: bytearray | None = None
    tm_hm_bag_buffer: bytearray | None = None

    for index in range(received_items_count):
        network_item = ctx.items_received[index]
        name = ctx.item_names.lookup_in_game(network_item.item)
        internal_id = all_items_dict_view[name].item_id
        match name:
            case x if x in all_key_items:
                if key_items_bag_buffer is None:
                    key_items_bag_buffer = await read_bag(client, ctx,
                                                          client.key_items_bag_offset, client.key_items_bag_size)
                if not await write_to_bag(client, ctx, key_items_bag_buffer, client.key_items_bag_offset,
                                          client.key_items_bag_size, internal_id, True):
                    client.logger.warning(f"Could not add {name} to key items bag, no space left. "
                                          f"Please report this to the developers.")
                    break
            case x if x in badges.table:
                read = await bizhawk.read(
                    ctx.bizhawk_ctx, (
                        (client.save_data_address+client.badges_offset, 1, client.ram_read_write_domain),
                    )
                )
                new_state = read[0][0] | (1 << badges.table[name].bit)
                await bizhawk.write(
                    ctx.bizhawk_ctx, (
                        (client.save_data_address+client.badges_offset, [new_state], client.ram_read_write_domain),
                    )
                )
            case x if x in medicine.important:
                if medicine_bag_buffer is None:
                    medicine_bag_buffer = await read_bag(client, ctx,
                                                         client.medicine_bag_offset, client.medicine_bag_size)
                if not await write_to_bag(client, ctx, medicine_bag_buffer, client.medicine_bag_offset,
                                          client.medicine_bag_size, internal_id, True):
                    client.logger.warning(f"Could not add {name} to medicine bag, no space left. "
                                          f"Please report this to the developers.")
                    break
            case x if x in seasons.table:
                await client.write_set_flag(ctx, seasons.table[name].flag_id)
            case x if x in all_tm_hm:
                if tm_hm_bag_buffer is None:
                    tm_hm_bag_buffer = await read_bag(client, ctx, client.tm_hm_bag_offset, client.tm_hm_bag_size)
                if not await write_to_bag(client, ctx, tm_hm_bag_buffer, client.tm_hm_bag_offset,
                                          client.tm_hm_bag_size, internal_id, True):
                    client.logger.warning(f"Could not add {name} to TM/HM bag, no space left. "
                                          f"Please report this to the developers.")
                    break
            case _:
                # Other bags are irrelevant for this part
                pass


async def _enforce_bag_gating(client: "PokemonTHTOriginsClient", ctx: "BizHawkClientContext",
                              bag_offset: int, bag_size: int, gated_ids: set[int], bag_label: str) -> None:
    """Strip any gated item the vanilla game handed out directly, before AP has actually sent it.

    THT Origins isn't ROM-patched, so its own scripts still place these items in their bag at their
    original story beats regardless of the multiworld state. This runs every watcher tick and removes
    any such item that isn't yet in ctx.items_received, so the player can't use it (e.g. to teach an
    HM, or satisfy an in-game "do you have X" check) before AP has actually granted it. Legitimately
    received copies (written by receive_items/reload_key_items) are left alone.
    """
    authorized_ids = _authorized_ids(ctx, gated_ids)

    buffer = await read_bag(client, ctx, bag_offset, bag_size)
    for slot in range(bag_size):
        old_slot_bytes = buffer[slot*4:(slot*4)+4]
        id_in_slot = int.from_bytes(old_slot_bytes[:2], "little")
        if id_in_slot == 0 or id_in_slot not in gated_ids or id_in_slot in authorized_ids:
            continue

        if await bizhawk.guarded_write(
            ctx.bizhawk_ctx, ((
                client.save_data_address + bag_offset + (slot*4),
                bytes(4),
                client.ram_read_write_domain
            ),), ((
                client.save_data_address + bag_offset + (slot*4),
                bytes(old_slot_bytes),
                client.ram_read_write_domain
            ),)
        ):
            buffer[slot*4:(slot*4)+4] = bytes(4)
            client.logger.info(
                f"Removed {bag_label} (id {id_in_slot:#06x}) the game granted before it was received from Archipelago."
            )


async def enforce_key_item_gating(client: "PokemonTHTOriginsClient", ctx: "BizHawkClientContext") -> None:
    await _enforce_bag_gating(client, ctx, client.key_items_bag_offset, client.key_items_bag_size,
                              _get_gated_key_item_ids(), "key item")


async def enforce_tm_hm_gating(client: "PokemonTHTOriginsClient", ctx: "BizHawkClientContext") -> None:
    await _enforce_bag_gating(client, ctx, client.tm_hm_bag_offset, client.tm_hm_bag_size,
                              _get_gated_tm_hm_ids(), "TM/HM")


async def read_bag(client: "PokemonTHTOriginsClient", ctx: "BizHawkClientContext", bag_offset: int, bag_size: int) -> bytearray:
    return bytearray((await bizhawk.read(
        ctx.bizhawk_ctx, (
            (client.save_data_address + bag_offset, bag_size * 4, client.ram_read_write_domain),
        )
    ))[0])


async def write_to_bag(client: "PokemonTHTOriginsClient", ctx: "BizHawkClientContext",
                       buffer: bytearray, bag_offset: int, bag_size: int, internal_id: int, only_once: bool) -> bool:

    # go through all slots in bag
    for slot in range(bag_size):
        id_bytes_in_slot = buffer[slot*4:(slot*4)+2]
        id_in_slot = int.from_bytes(id_bytes_in_slot, "little")

        # slot which already has that item or first empty slot found
        if id_in_slot == internal_id or id_in_slot == 0:
            old_amount_bytes = buffer[(slot*4)+2:(slot*4)+4]
            old_amount = int.from_bytes(old_amount_bytes, "little")
            if only_once and old_amount > 0:
                return True  # Only when key items get reloaded

            internal_id_bytes = internal_id.to_bytes(2, "little")
            new_amount_bytes = min(old_amount + 1, 995).to_bytes(2, "little")
            # write item id and new amount to slot
            if await bizhawk.guarded_write(
                ctx.bizhawk_ctx, ((
                    client.save_data_address+bag_offset+(slot*4),
                    internal_id_bytes + new_amount_bytes,
                    client.ram_read_write_domain
                ),), ((
                    client.save_data_address+bag_offset+(slot*4),
                    id_bytes_in_slot + old_amount_bytes,
                    client.ram_read_write_domain
                ),)
            ):
                buffer[slot*4:(slot*4)+4] = internal_id_bytes + new_amount_bytes
                return True
            else:
                return await write_to_bag(client, ctx, buffer, bag_offset, bag_size, internal_id, only_once)

    else:
        # went through all slots and none can be written to
        return False

