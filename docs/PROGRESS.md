# Progress (read this first when resuming)

Priority: SAVE PROGRESS > MANY FEATURES. Commit and push after every small step.

## Done
- Python prototype in `AshenVeil_Python/` (playable, left untouched).
- Reference screenshots in `AshenVeil_Python/assets/reference_art/full/`.
- Generated placeholder art (96x96 frames, facing right, feet on row 88): `assets/characters/` (player + 4 enemies), `assets/fx/` (slashes, impact), `assets/tiles/`, `assets/props/`; generators in `tools/`.
- Cinzel font in `assets/fonts/`.
- Godot 4.7.2 (standard, not .NET) runs headless in the sandbox; project in `godot/` boots OK.
- Godot step 2 done: `godot/player.gd` (run, jump, dodge, light1->light2 combo, heavy, skill, hurt, death) builds animations from `player.png`/`player.json`; `main.tscn` has a test floor + camera. Headless test `godot/tests/test_player.gd` passes 13/13.
- Controls: A/D or arrows move, Space/W jump, Shift dodge, J or LMB light (press again for combo), K or RMB heavy, E skill.

## Decision
Port to Godot 4 (GDScript) for 2D lights, parallax, particles and shaders. Python version stays as a fallback.

## Next (in order)
1. (done) Player scene.
2. One room: TileMap/platforms, parallax layers, torch PointLight2D, moonlight.
3. Combat (light/heavy/skill, dodge), then enemies, then HUD with Cinzel.
4. Parallax background PNGs (sky/moon, castle, bridges, foreground arches).

## How to run headless test
Download Godot_v4.7.2-stable_linux.x86_64 from github.com/godotengine/godot-builds releases, then:
`./Godot_v4.7.2-stable_linux.x86_64 --headless --import --path godot` then
`./Godot_v4.7.2-stable_linux.x86_64 --headless --path godot --script res://tests/test_player.gd`
