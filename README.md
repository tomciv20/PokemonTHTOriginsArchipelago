# Pokemon THT Origins — Archipelago World

An [Archipelago](https://archipelago.gg) multiworld integration for **Pokemon THT Origins**, a custom Pokemon Black romhack.

---

## What Is This?

Pokemon THT Origins is a Pokemon Black romhack with a new story featuring original characters. This apworld lets you play it as part of an Archipelago multiworld — items from the game get shuffled across all players' worlds, and you collect items sent to you from other players.

**Win condition:** Defeat Jonah (Ghetsis in vanilla) to complete your game.

---

## Installation

### Requirements
- [Archipelago 0.6.0+](https://github.com/ArchipelagoMW/Archipelago/releases)
- [BizHawk 2.10+](https://tasvideos.org/BizHawk/ReleaseHistory)
- Pokemon THT Origins `.nds` ROM file

### Steps

1. Copy `PokemonTHTOrigins.apworld` to your Archipelago `custom_worlds` folder:
   - Windows: `C:\ProgramData\Archipelago\custom_worlds\`
2. Copy `PokemonTHTOrigins.yaml` to your Archipelago `Players` folder and edit with your name
3. Generate a multiworld using the Archipelago Launcher as normal

---

## Playing

1. Open **BizHawk** and load your `Pokemon THT Origins.nds` ROM — **do not patch it**
2. In the Archipelago Launcher, open **BizHawk Client**
3. Connect to your Archipelago server (e.g. `archipelago.gg:12345`)
4. Enter your slot name when prompted
5. Play the game normally — items you pick up in the world are sent as checks; items from other players appear in your bag automatically

### Important Notes

- Play the game **without applying any Archipelago patch** — the ROM is used as-is
- The BizHawk client communicates with the game via memory rather than ROM patching
- Items are delivered directly to your in-game bag
- Defeating Jonah (the final boss, renamed from Ghetsis) completes your game
- Since the ROM isn't patched, the vanilla game still hands you key items and TMs/HMs at their normal story beats. The client detects this and removes them from your bag again until Archipelago has actually sent you that item, so progression stays gated by the multiworld rather than by vanilla pickups

---

## What Gets Shuffled

All item pickup locations from Pokemon Black are included:
- **Overworld items** — items on the ground across the region
- **Hidden items** — items found with the Dowsing Machine
- **NPC gifts** — items given by characters in the story
- **Gym Badges** — all 8 badges from gym leaders
- **TMs and HMs** — all technical and hidden machines
- **Key items** — story-critical items (Dragon Skull, Liberty Pass, etc.)

**609 items** shuffled across **633 locations** (the difference is filled with vanilla-style filler items).

---

## Differences from Vanilla Pokemon Black AP

- No ROM patching required — plays on the original `.nds` file
- No wild Pokemon, starter, or trainer randomization, and none planned — the vanilla world implements these by rewriting ROM data tables at patch time, which isn't possible without introducing real ROM patching here
- A handful of vanilla BW key items that only functioned as progression gates because of the vanilla world's ROM patch (Explorer Kit, Loot Sack, Red Chain, Oak's Letter, Parcel, Blue Card, Basement Key, Machine Part, Tidal Bell, Lock Capsule) have been removed entirely, since they never gated anything here
- Only goal: Defeat Jonah (Ghetsis) — no alternate win conditions

---

## Building from Source

```powershell
.\Build-APWorld.ps1
```

This builds `PokemonTHTOrigins.apworld` and copies it to `custom_worlds` automatically.

The apworld zip must contain files under a `PokemonTHTOrigins/` subdirectory.
