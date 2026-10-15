# Ashen Veil

A dark-fantasy 2D action game prototype. The current Python build is a **side-scrolling Metroidvania-style combat sandbox**, with interconnected ruins, platforming, weapon-specific attacks, enemy encounters, checkpoints and a boss. Recent updates also improve the procedural artwork and fix a Soul Burst charge crash after defeating enemies.

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

Early playable prototype. The aim is deliberate Soulslike combat and dark atmosphere in a side-view Metroidvania format. Combat feel, platform collisions and visuals should be tested on Windows hardware; further animation, exploration, ability-gate and level-polish work remains.

The game uses original procedural drawings and currently includes no third-party art assets. No open-source license has been assigned yet.
