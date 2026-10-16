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

- Godot step 3 done: `godot/room.gd` builds the first room in code (5 parallax layers from `assets/parallax/`, tiled stone floor, 5 one-way platforms, 7 torches with flickering PointLight2D, banners, statue, ladder, chains, CanvasModulate dusk tint). Camera zoom 1.25. Headless test 14/14. Rendered screenshot: `docs/room_preview.png` (made with `xvfb-run -a godot --rendering-driver opengl3 --resolution 1280x720 --path godot --script res://tests/screenshot.gd -- out.png`).
- Godot step 4 done: `godot/hud.gd` (code-drawn HUD in Cinzel: portrait + level, HP/FP bars, 5-slot hotbar LMB/RMB/Shift/E/Q, souls counter, minimap with area name). Player stats in `player.gd` (hp 320, fp 120, skill costs 20 FP, FP regen, `hurt(amount)`). Chains no longer poke into the floor. Tests 15/15.

## Decision
Port to Godot 4 (GDScript) for 2D lights, parallax, particles and shaders. Python version stays as a fallback.

## Next (in order)
1. (done) Player scene.
2. (done, needs visual review) One room.
3. Combat (light/heavy/skill, dodge), then enemies, then HUD with Cinzel.
4. (done) Parallax background PNGs.
5. Next: enemies with AI, slash FX attached to attacks, HP/damage, minimap, SFX.

## How to run headless test
Download Godot_v4.7.2-stable_linux.x86_64 from github.com/godotengine/godot-builds releases, then:
`./Godot_v4.7.2-stable_linux.x86_64 --headless --import --path godot` then
`./Godot_v4.7.2-stable_linux.x86_64 --headless --path godot --script res://tests/test_player.gd`
