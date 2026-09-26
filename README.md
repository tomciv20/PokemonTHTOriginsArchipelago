# Pokemon THT Origins — Archipelago World

An [Archipelago](https://archipelago.gg) multiworld integration for **Pokemon THT Origins**, a custom Pokemon Black romhack.

---

## What Is This?

Pokemon THT Origins is a Pokemon Black romhack with a new story featuring original characters. This apworld lets you play it as part of an Archipelago multiworld — items from the game get shuffled across all players' worlds, and you collect items sent to you from other players.

**Win condition:** Defeat Jonah (Ghetsis in vanilla) to complete your game. *(See [Known limitations](#known-limitations) — this needs a small change in the ROM's scripts before it can trigger.)*

---

## Installation

### Requirements
- [Archipelago 0.6.0+](https://github.com/ArchipelagoMW/Archipelago/releases)
- [BizHawk 2.10+](https://tasvideos.org/BizHawk/ReleaseHistory)
- Pokemon THT Origins `.nds` ROM file

### Steps

1. Copy `PokemonTHTOrigins.apworld` to your Archipelago `custom_worlds` folder:
   - Windows: `C:\ProgramData\Archipelago\custom_worlds\`
2. Copy `PokemonTHTOrigins.yaml` to your Archipelago `Players` folder, and change `name:` at the top to your own player name
3. Generate a multiworld using the Archipelago Launcher as normal

---

## Playing

1. Open **BizHawk** and load your `Pokemon THT Origins.nds` ROM — **do not patch it**
2. In BizHawk, open **Tools → Lua Console** and run the connector script from your Archipelago install: `C:\ProgramData\Archipelago\data\lua\connector_bizhawk_generic.lua`
3. In the Archipelago Launcher, open **BizHawk Client**. It should say it is running the handler for **Pokemon THT Origins**
4. Connect to your Archipelago server (e.g. `/connect archipelago.gg:12345`) and enter your slot name when prompted
5. Play the game normally — items you pick up in the world are sent as checks; items from other players appear in your bag automatically

### Important Notes

- Play the game **without applying any Archipelago patch** — the ROM is used as-is
- The BizHawk client communicates with the game via memory rather than ROM patching
- Items are delivered directly to your in-game bag
- Since the ROM isn't patched, the vanilla game still hands you key items and TMs/HMs at their normal story beats. The client detects this and removes them from your bag again until Archipelago has actually sent you that item, so progression stays gated by the multiworld rather than by vanilla pickups
- Having the official **Pokemon Black and White** apworld installed as well is fine: this client takes ROMs that were not patched by that world, and leaves ROMs patched by it alone

---

## What Gets Shuffled

**511 locations**, all of which the unpatched game can actually report:

| Locations | Count |
|---|---|
| Overworld items (incl. Abyssal Ruins) | 277 |
| Hidden items (Dowsing Machine) | 131 |
| NPC gifts and events | 88 |
| TMs/HMs given by NPCs | 15 |

The item pool is the 8 gym badges, HMs and TMs, evolution stones and other held items, fossils, and the key items **Dragon Skull, Liberty Pass, Super Rod and the three Wingull Grams**, plus the vanilla Bicycle, Pal Pad, Vs. Recorder, Gracidea, Dowsing Machine and Prop Case. The remaining slots are filled with random filler items.

---

## Known limitations

The official Pokemon Black and White world works by patching the ROM. Among other things, that patch adds its own flags (numbered `0x172`–`0x1DF`) to the game's scripts so the client can tell when certain events happen. **THT Origins is not patched, and its scripts never set those flags** (checked by scanning the ROM's script archive: vanilla Black and THT Origins contain no set-flag command for any of them, the AP-patched ROM contains 67). That has two consequences:

- **94 locations from the official world are not included here** because they can never be checked: all 8 gym badge rewards, the gym TM rewards, most NPC gifts and NPC TMs, and 14 hidden items whose flags come from the patch.
- **The win condition cannot trigger yet.** The client watches flag `0x1D3` (defeating Ghetsis/Jonah), which the ROM never sets.

Both go away if the ROM sets those flags itself, see below.

Other differences from the official world:

- No wild Pokemon, starter, or trainer randomization, and none planned — the official world implements these by rewriting ROM data tables at patch time, which isn't possible without introducing real ROM patching here
- A handful of vanilla BW key items that only functioned as progression gates because of the official world's ROM patch (Explorer Kit, Loot Sack, Red Chain, Oak's Letter, Parcel, Blue Card, Basement Key, Machine Part, Tidal Bell, Lock Capsule) have been removed entirely, since they never gated anything here
- Region logic still assumes the vanilla gates (badges, HMs) apply, but nothing stops a player from walking through areas the multiworld logic considers locked; only the checks and items are enforced
- The gating of key items and TMs/HMs works by removing them from the bag a moment after the game hands them out, so it's best-effort: a player who is fast enough can use an item in that window

### For the ROM's author

To make the win condition work, add a set-flag for `0x1D3` to the script that runs after the final fight against Jonah. To bring other locations back, set their flag in the matching script (badge rewards use `0x172`–`0x179`, in the order Striaton to Opelucid), then add the flag to `HACK_SET_FLAGS` in `PokemonTHTOrigins/data/locations/__init__.py` and rebuild.

---

## Building from Source

```powershell
.\Build-APWorld.ps1
```

This builds `PokemonTHTOrigins.apworld` and copies it to `custom_worlds` automatically.

The apworld zip must contain files under a `PokemonTHTOrigins/` subdirectory.
