# Ashen Veil

A dark-fantasy 2D action game prototype. The current Python build is a **side-scrolling Metroidvania-style combat sandbox** with platforming, weapon-specific attacks, enemy encounters, checkpoints, and a boss.

The world now uses four original SVG environment illustrations (Drowned March, Ashen Chapel, Cinder Bastion, and Veiled Throne), rendered with slow parallax, color grading, drifting fog, and ember effects. The game also retains a procedural drawing fallback if SVG loading isn't supported by a particular Pygame build.

## Run the game

Open [`AshenVeil_Python`](AshenVeil_Python/) and follow its [README](AshenVeil_Python/README.md).

On Windows, install Python 3.10+ and double-click `launch_windows.bat`, or run:

```powershell
py -3 -m pip install -r requirements.txt
py -3 main.py
```

## Controls

- **A / D** or arrow keys: move
- **Space / W / Up:** jump (double jump available)
- **Left mouse button:** light attacks / combos
- **Right mouse button:** heavy attack
- **Shift:** dodge
- **1 / 2 / 3:** change weapon
- **E:** weapon skill
- **Q:** Soul Burst
- **Esc:** pause

## Project status

Early playable prototype. Automated smoke tests cover source compilation, headless rendering, background-asset loading, and enemy-death soul rewards. Visual gameplay and collision feel should still be tested on Windows hardware.

No third-party art assets are bundled. No open-source license has been assigned yet.
