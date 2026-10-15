# Ashen Veil — Python Metroidvania Combat Sandbox

A dark-fantasy side-scrolling action-platformer prototype built with Python and Pygame CE.

## Visual target and reference art

The owner-provided screenshots that define the intended visual direction are stored in [`assets/reference_art/`](assets/reference_art/). They show the current prototype and target qualities: cinematic painterly gothic environments, moonlit castles and bridges, atmospheric fog and torchlight, readable combat silhouettes, dramatic weapon trails, layered platforms, exploration, and a richer action-game HUD.

The repository copies are lightweight 128×72 preview thumbnails to keep the source repository small; they are visual references, **not in-game textures**. The actual game backgrounds are the four scalable SVG environment scenes in `assets/backgrounds/`, rendered behind the playable geometry with parallax.

## Visuals and world

The game includes four original vector environment illustrations:
- **The Drowned March** — moonlit blue-grey ruins.
- **The Ashen Chapel** — ember-lit, blood-red ruins.
- **The Cinder Bastion** — volcanic fortress and molten falls.
- **The Veiled Throne** — violet eclipse and shadowed citadel.

## Gameplay

- Connected side-scrolling route with platforms, gaps, shrines/checkpoints and a Grave Warden boss.
- Three weapon types: Rookfang Longsword, Gravetide Twinblades and Oathbreaker Greatblade.
- Buffered light attacks and charged heavy attacks, dodge invulnerability, stamina, weapon skills and Soul Burst.
- Hollow enemies, ranged Ash Archers, boss telegraphs, health bars, and a route-progress HUD.

## Run on Windows

1. Install Python 3.10 or later.
2. Double-click `launch_windows.bat`.
3. Or run from this folder:

```powershell
py -3 -m pip install -r requirements.txt
py -3 main.py
```

## Controls

| Input | Action |
|---|---|
| A / D or arrow keys | Move |
| Space / W / Up | Jump; jump again for double jump |
| Left-click | Light combo attacks |
| Right-click | Heavy attack |
| Shift | Dodge |
| 1 / 2 / 3 | Switch weapon |
| E | Weapon skill |
| Q | Soul Burst |
| Esc | Pause / resume |

## Status

This is an early playable prototype, not a finished commercial game. CI smoke tests verify source compilation, headless rendering, SVG background loading, and the Soul Burst reward path. The intended art target requires future hand-authored animated sprites, richer foreground architecture, and more detailed exploration systems.

No open-source license has been assigned yet.
