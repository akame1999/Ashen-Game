# Art spec: replacing the placeholder art with real painted art

The game loads art from fixed file names. Replace a PNG with your own and it is used as-is, no code change.
Put files in `godot/assets/...` (keep the Python copies in `AshenVeil_Python/assets/...` in sync only if you still use that version).
Only use art you own or are licensed to use (check your image tool's terms).

## 1. Parallax layers  (`godot/assets/parallax/`)
Files, back to front: `0_sky.png`, `1_castle.png`, `2_aqueduct.png`, `3_ruins.png`, `4_foreground.png`.
- Any width, any height: each file is scaled to 540 px tall and repeated sideways, so the LEFT and RIGHT edges must tile seamlessly.
- Layers 1 to 4 need a transparent background (PNG alpha). `0_sky` is opaque.
- Keep the walkable ground line about 80% of the way down (art row 430 of 540): that is where the player's feet go.
- Keep detail low-contrast in the middle layers so the player and enemies stay readable. `4_foreground` should be sparse (vines, plants, dark silhouettes).
- Scroll speeds are set in `room.gd` (`PARALLAX`), so the layers are built to move slower the further back they are.

## 2. Character sheets  (`godot/assets/characters/`)
Files: `player`, `skeleton`, `shield_skeleton`, `archer`, `armored_knight`; each is `<name>.png` plus `<name>.json`.
- Square frames of any size (96 now; 128 is fine), facing RIGHT, one animation per ROW, frames left to right, transparent background.
- The JSON says how to cut the sheet:
  `{"frame": 96, "feet_row": 88, "center_x": 44, "rows": [{"name": "idle", "row": 0, "frames": 4}, ...]}`
  `feet_row` = pixel row of the ground line inside a frame; `center_x` = pixel column of the character's centre.
- Rows and frame counts (player): idle 4, run 6, jump 2, fall 2, dodge 4, light1 5, light2 5, heavy 6, skill 6, hurt 2, death 6.
- Rows for each enemy: idle 4, walk 6, attack 6, hurt 2, death 6. Hit lands on attack frame 3 (skeleton), 4 (shield skeleton, archer, knight).
- Keep the character about 36 px tall inside a 96 px frame (scale up proportionally for bigger frames, but then tell me so I can scale the collision and reach).

## 3. Effects  (`godot/assets/fx/`)
Horizontal strips, square frames (96 px), pivot = where the swing starts:
`slash_light.png` (6 frames), `slash_heavy.png` (7), `slash_skill.png` (7), `impact_spark.png` (6), `soul_burst.png` (8, centred ring).
Slashes face right with the pivot at about (29, 50) of the frame.

## 4. Tiles and props  (`godot/assets/tiles/`, `godot/assets/props/`)
`tileset.png`: 32x32 tiles in one row: stone, stone_dark, stone_moss_top, stone_big, plank, pillar.
`torch.png` 4 frames of 32x48, `banner.png` 4 frames of 48x96, `chain.png` 16x32, `ladder.png` 24x32 (the last two tile vertically), `statue_hooded.png` 64x112.

## 5. Prompts for an image generator (adapt to your tool)
Use the same style words every time so everything matches. Style line:
"dark fantasy 2D pixel art, painterly, moonlit gothic ruined cathedral, deep blue shadows, warm orange torchlight, moss and red leaves, side view"
- Backgrounds: "<style line>, wide seamless horizontal panorama, distant gothic castle with lit windows and giant aqueduct bridge, waterfall, fog, no characters, no UI" then split into depth layers (sky/moon, castle, bridge, ruins, foreground) in an image editor (Krita, Photoshop) and make each side-tile.
- Character: "<style line>, side view, facing right, white-haired swordsman in red cloak, full body, transparent background, plain flat lighting" then build animation frames in Aseprite (trace or redraw each pose). Image generators rarely keep a character consistent across frames, so plan on hand cleanup, or an AI tool made for sprite animation.
- Enemies: same, one at a time: skeleton with spear, skeleton with round shield and short sword, hooded skeleton archer with bow, armored knight with red plume and greatsword.
- Tileset and props: ask for "seamless 32x32 stone brick tile, dark blue-gray, moss on top" and so on, then cut to size.

## 6. HUD
The HUD is drawn in code (`hud.gd`). If you want painted frames and icons, send PNGs for: portrait ring, bar frames, 5 hotbar icons (38x38), souls icon, minimap frame, and I will switch the HUD to use them.
