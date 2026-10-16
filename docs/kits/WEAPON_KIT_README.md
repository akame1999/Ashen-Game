# Ashen Veil — Godot 4 Weapon Assets

A self-contained dark-fantasy weapon art kit for a 2D side-scrolling action / Metroidvania game.

## Included

- 12 separate high-resolution weapon/accessory PNGs with transparent alpha backgrounds.
- A transparent 4×3 utility atlas at `assets/weapon_sprite_atlas.png` (512×256 cells).
- Matching scalable SVG originals under `assets/weapons/` (also copied to `assets/source_svg/`).
- 12 128×128 inventory icons under `assets/icons/`.
- 6 transparent combat/VFX sprites under `assets/effects/`.
- `weapon_manifest.json` listing file paths and grip-anchor coordinates.
- A Godot 4 weapon gallery scene and an example pivot/equip script.

## Weapon list

1. Rookfang Longsword — balanced straight sword, gold guard and crimson rune accents.
2. Oathbreaker Greatsword — heavy jagged blade with ember-red fissures.
3. Ashen Katana — curved blade with red edge runes.
4. Gravetide Twinblades — twin steel blades with violet and frost-blue details.
5. Void Dagger Pair — fast paired daggers.
6. Veilpiercer Spear — long thrusting weapon.
7. Cinder Greataxe — heavy executioner axe.
8. Frost Halberd — polearm with a broad icy head.
9. Ghostwood Bow — tall curved bow with a luminous string.
10. Soulfire Rune Staff — arcane staff with a blue crystal.
11. Blackthorn Shield — defensive off-hand accessory.
12. Nightfall Scythe — long-handled crescent scythe.

## Use in your own Godot project

1. Copy `assets/` into your Godot project's `res://` folder.
2. Add a `Node2D` child named `WeaponPivot` at the player's weapon-hand location.
3. Add a `Sprite2D` child named `WeaponSprite` beneath it.
4. Attach `scripts/equip_weapon_example.gd` to `WeaponPivot` or copy the helper functions to your player script.
5. Use the manifest grip anchor so the weapon rotates around the handle instead of its image center.
6. Flip the weapon horizontally when your character faces left; tune scale and attack rotation to match your player sprite.

All weapon PNGs have transparent backgrounds. Most melee weapons face right with the handle at the left; the bow, staff and shield are vertically oriented. The anchor coordinates are source-image pixels for the 1024×512 weapon canvases.

## Run the sample gallery

Open this folder in Godot 4 and press F6/F5 to run `scenes/weapon_gallery.tscn`. Use Left/Right to select a weapon, F to flip it, and Q/E to rotate the selected preview.

## Notes

These are original vector-designed starter assets with a dark-steel / aged-gold / crimson-rune palette, intended to be easy to recolor and modify. They are standalone weapon sprites, not a full set of hand-animated character attack sprites; animation timing, collision hitboxes, and character-specific grip placement still need to be integrated into your combat controller.
