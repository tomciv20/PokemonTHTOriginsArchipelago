from typing import TYPE_CHECKING
import worlds._bizhawk as bizhawk

if TYPE_CHECKING:
    from ..bizhawk_client import PokemonTHTOriginsClient
    from worlds._bizhawk.context import BizHawkClientContext


async def early_setup(client: "PokemonTHTOriginsClient", ctx: "BizHawkClientContext") -> None:
    from .goals import get_method

    client.goal_checking_method = get_method(client, ctx)

    read = await bizhawk.read(
        ctx.bizhawk_ctx, (
            (client.data_address_address, 3, client.ram_read_write_domain),
        )
    )
    client.save_data_address = int.from_bytes(read[0], "little")


async def late_setup(client: "PokemonTHTOriginsClient", ctx: "BizHawkClientContext") -> None:
    from .items import reload_key_items

    await reload_key_items(client, ctx)

    if not client.get_flag(0x1DE):
        await client.write_set_flag(ctx, 0x1DE)
