# Progress (read this first when resuming)

Priority: SAVE PROGRESS > MANY FEATURES. Commit and push after every small step.

## Done
- Python prototype in `AshenVeil_Python/` (playable, left untouched).
- Reference screenshots in `AshenVeil_Python/assets/reference_art/full/`.
- Generated placeholder art (96x96 frames, facing right, feet on row 88): `assets/characters/` (player + 4 enemies), `assets/fx/` (slashes, impact), `assets/tiles/`, `assets/props/`; generators in `tools/`.
- Cinzel font in `assets/fonts/`.
- Godot 4.7.2 (standard, not .NET) runs headless in the sandbox; minimal project in `godot/` boots OK.

## Decision
Port to Godot 4 (GDScript) for 2D lights, parallax, particles and shaders. Python version stays as a fallback.

## Next (in order)
1. Copy art into `godot/assets/`, player scene moving with `player.png` animations (rows in `player.json`).
2. One room: TileMap/platforms, parallax layers, torch PointLight2D, moonlight.
3. Combat (light/heavy/skill, dodge), then enemies, then HUD with Cinzel.
4. Parallax background PNGs (sky/moon, castle, bridges, foreground arches).

## How to run headless test
Download Godot_v4.7.2-stable_linux.x86_64 from github.com/godotengine/godot-builds releases, then:
`./Godot_v4.7.2-stable_linux.x86_64 --headless --path godot --quit-after 60`
