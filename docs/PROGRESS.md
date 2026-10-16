# Progress (read this first when resuming)

Priority: SAVE PROGRESS > MANY FEATURES. Commit and push after every small step.

## Done
- Python prototype decommissioned and removed; project is now exclusively focused on Godot 4 (GDScript).
- Generated placeholder art (96x96 frames, facing right, feet on row 88): `assets/characters/` (player + 4 enemies), `assets/fx/` (slashes, impact), `assets/tiles/`, `assets/props/`; generators in `tools/`.
- Cinzel font in `assets/fonts/`.
- Godot 4.7.2 (standard, not .NET) runs headless in the sandbox; project in `godot/` boots OK.
- Godot step 2 done: `godot/player.gd` (run, jump, dodge, light1->light2 combo, heavy, skill, hurt, death) builds animations from `player.png`/`player.json`; `main.tscn` has a test floor + camera. Headless test `godot/tests/test_player.gd` passes 13/13.
- Controls: A/D or arrows move, Space/W jump, Shift dodge, J or LMB light (press again for combo), K or RMB heavy, E skill.

- Godot step 3 done: `godot/room.gd` builds the first room in code (5 parallax layers from `assets/parallax/`, tiled stone floor, 5 one-way platforms, 7 torches with flickering PointLight2D, banners, statue, ladder, chains, CanvasModulate dusk tint). Camera zoom 1.25. Headless test 14/14. Rendered screenshot: `docs/room_preview.png` (made with `xvfb-run -a godot --rendering-driver opengl3 --resolution 1280x720 --path godot --script res://tests/screenshot.gd -- out.png`).
- Godot step 4 done: `godot/hud.gd` (code-drawn HUD in Cinzel: portrait + level, HP/FP bars, 5-slot hotbar LMB/RMB/Shift/E/Q, souls counter, minimap with area name). Player stats in `player.gd` (hp 320, fp 120, skill costs 20 FP, FP regen, `hurt(amount)`). Chains no longer poke into the floor. Tests 15/15.
- Godot step 5 done: enemies (`enemy.gd`, configs for skeleton / shield_skeleton / archer / armored_knight; patrol -> chase -> attack, hurt, death, souls), `arrow.gd`, `sheet_util.gd`; player melee hit detection with slash FX + impact sparks + damage numbers; i-frames after being hit; death reloads the scene after 2.5 s. Room spawns 5 enemies. Tests: `tests/test_player.gd` 14/14, `tests/test_combat.gd` 9/9. Combat screenshot: `xvfb-run -a godot --rendering-driver opengl3 --resolution 1280x720 --path godot --script res://tests/screenshot.gd -- out.png combat`.
- Godot step 6 done: Q Soul Burst (40 FP, 70 damage in a 110px radius, 0.5 s invulnerable while charging, burst FX `soul_burst.png`), cooldowns (dodge 0.8 s, heavy 1.2 s, skill 2 s, burst 4 s) with dark overlays and a blue 'not enough FP' tint on the hotbar. Tests 14/14 + 10/10. Screenshot tool gained `burst` mode (use physics-synced input; wait 2 rendered frames before capture).
- Art pipeline: owner wants painted art like the reference (cannot be generated in code). Game now accepts replacement art: parallax PNGs of any size (scaled to 540 tall, tiled sideways), character sheets with any frame size via `<name>.json` (`frame`, `feet_row`, `center_x`, `rows`). Full spec + image-generator prompts in `docs/ART_SPEC.md`. Waiting on owner to supply art; HUD art optional.
- HUD layout aligned to visual target (Image 2): ability diamond sockets (Q Soul Burst, E Skill, Focus) placed directly under HP/FP bars with active cooldown overlays; bottom-left hotbar restructured to 4 inventory slots (Flask R with count, Weapon 1 Rookfang, Weapon 2 Gravetide, Weapon 3 Oathbreaker) with gold active-weapon indicator; weapon switching implemented (keys 1/2/3); top-right minimap plate labeled Gravework Keep. Test suite expanded with weapon selection tests (22/22 player tests pass, 10/10 combat tests pass).
- Region 1 High-Resolution Environment Art integrated (`drowned_march_bg.jpg`): added painterly gothic moonlit citadel & viaduct backdrop into `godot/room.gd` with multi-plane parallax scrolling, improved torch lighting, and ambient night color grading. Both test suites (test_player 18/18, test_combat 10/10) pass.
- Double jump implemented in Godot player (matching Python prototype mechanic; allows mid-air jump with spark effect, resets upon landing on floor). Controls updated in pause menu and on-screen hint. Test suite updated with double-jump assertions (18/18 pass, combat tests 10/10 pass).
- UI pass done: ornate pointed HP/FP bars with trailing damage bar, segmented HP, low-HP pulse; ornate portrait + level badge; 6-slot hotbar with key badges, numeric cooldowns, ready flash, FP-lack tint; healing flask (R, 3 charges, +110 HP); souls counter that rolls up with +N popups; fog-of-war minimap with real exploration %; red hit/low-HP screen edges; YOU DIED screen (scene reloads after 3.5 s); pause menu (Esc, Enter restarts) with controls list; fading intro hint. Preview: `docs/ui_preview.png`. Screenshot modes: ui, pause, death, burst, combat. Tests 15/15 + 10/10.
- Art direction: owner wants Bloodstained / Mandragora quality. Cannot be generated in code and cannot be copied. Plan: use licensed hand-made packs (Gothicvania by ansimuz, CC0, see `docs/ASSET_LICENSES.md`); owner downloads the zips and uploads them to the chat; then integrate hero, enemies, tiles and backgrounds into `godot/` (sheet loader already reads per-sheet json, so frame sizes can differ). Style note: Gothicvania is small-scale Castlevania-style pixel art, not painterly like the reference screenshots.
- CI: replaced stale Python smoke workflow with `.github/workflows/godot-tests.yml` (headless import + player/combat tests, fails unless `FAILURES: 0`).

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
