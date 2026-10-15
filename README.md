# Ashen Veil — Python Combat Sandbox

A self-contained 2D dark-fantasy action-combat prototype built with Python and Pygame CE. The project focuses on responsive movement-plus-attacking, weapon-specific combat timing, readable enemy telegraphs, and a gothic ruined-arena atmosphere.

## Features

- Three weapons: Rookfang Longsword, Gravetide Twinblades, and Oathbreaker Greatblade.
- Buffered light attacks and charged heavy attacks, with attacks processed independently of movement.
- Dodge with temporary invulnerability, stamina, weapon skills, and Soul Burst.
- Enemy waves, ranged enemies, and a Grave Warden boss encounter.
- Dark-fantasy arena visuals, torch glow, attack arcs, impact particles, screen shake, minimap, and combat HUD.
- Windows launcher and optional PyInstaller build script.

## Run on Windows

1. Install Python 3.10 or later.
2. Open `AshenVeil_Python` and run `launch_windows.bat`.
3. Or run these commands from that folder:

```powershell
py -3 -m pip install -r requirements.txt
py -3 main.py
```

## Controls

| Input | Action |
|---|---|
| WASD | Move |
| Mouse | Aim |
| Hold left-click | Repeat light combo attacks |
| Hold and release right-click | Charged heavy attack |
| Space / Shift | Dodge |
| 1 / 2 / 3 | Switch weapon |
| E | Weapon skill |
| Q | Soul Burst |
| Esc | Pause / resume |

## Project status

This is an early playable combat sandbox, not a finished commercial game. The enhanced input and visuals should be tested on Windows hardware. Additional animation, levels, bosses, accessibility options, and progression systems remain future work.

## Requirements and license

See `AshenVeil_Python/requirements.txt` for the Python dependency. No third-party art assets are bundled; arena visuals are rendered procedurally.

No license has been assigned yet. Do not assume the project is open-source licensed until a LICENSE file is added.
