# Ashen Veil — Python Metroidvania Combat Sandbox

A dark-fantasy side-scrolling action platformer prototype built with Python and Pygame CE. The game uses procedural artwork; there are no external image assets to install.

## Features

- Side-scrolling camera and connected ruined-castle route with platforming, gaps and checkpoints.
- Three weapon types: Rookfang Longsword, Gravetide Twinblades and Oathbreaker Greatblade.
- Buffered light attacks and charged heavy attacks; attack timing is independent of movement.
- Dodge with temporary invulnerability, stamina, weapon skills and Soul Burst.
- Hollow enemies, ranged Ash Archers and a Grave Warden boss.
- Layered parallax castles and mountains, a cratered moon, detailed masonry, moss, torchlight, fog and curved attack trails.
- Health, stamina, Soul Burst meter, weapon cards, route progress, enemy telegraphs and a boss health bar.

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

This is an early playable prototype, not a finished commercial game. The graphics are procedurally drawn and have been enhanced with layered parallax scenery and more detailed silhouettes. Please test on Windows hardware; additional hand-authored sprite animations, boss movesets, hidden paths and progression systems remain future work.

No open-source license has been assigned yet.
