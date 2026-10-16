# Ashen Veil

A dark-fantasy 2D Metroidvania action game built in **Godot 4.7+ (GDScript)**.

The game features fast, responsive side-scrolling combat, dodge rolls, multi-strike combos, heavy attacks, weapon skills, Soul Burst area damage, double-jumping, enemy AI with varying behaviors (patrolling, chasing, ranged archers, shielded defenders, armored knights), and an ornate dark-fantasy HUD with real-time fog-of-war minimap, floating damage numbers, and healing flasks.

## Controls

| Action | Primary Input | Secondary Input |
| :--- | :--- | :--- |
| **Move** | `A` / `D` | `Left` / `Right` Arrow keys |
| **Jump** | `Space` | `W` / `Up` (Double jump in air) |
| **Light Attack** | `J` | Left Mouse Button (press again for combo) |
| **Heavy Attack** | `K` | Right Mouse Button |
| **Dodge Roll** | `Shift` | Invulnerable roll |
| **Weapon Skill** | `E` | Costs 20 FP |
| **Soul Burst** | `Q` | Costs 40 FP (AoE explosion) |
| **Healing Flask** | `R` | Restores 110 HP (3 charges) |
| **Switch Weapon** | `1` / `2` / `3` | Rookfang / Gravetide / Oathbreaker (each changes damage, reach and slash FX) |
| **Switch Region** | `F1`–`F4` | Drowned March / Ashen Chapel / Cinder Bastion / Veiled Throne backdrops |
| **Switch Skin** | `F6` | Male (default) / Female / Ashen Knight |
| **Pause Menu** | `Esc` | Displays controls & resume/restart |

## Running the Project

Open the `godot/` folder in **Godot 4.7+** (standard version) and press **F5** (or run `main.tscn`).

To run headlessly or execute automated tests:
```bash
# Run player mechanics & state tests
godot --headless --path godot --script res://tests/test_player.gd

# Run combat & enemy AI tests
godot --headless --path godot --script res://tests/test_combat.gd
```

Each suite prints `FAILURES: 0` when everything passes. A ready-made GitHub Actions workflow is staged in `docs/ci/godot-tests.yml` (copy it to `.github/workflows/`).

## Architecture

- **`godot/player.gd`**: Player state machine (`NORMAL`, `DODGE`, `ATTACK`, `HURT`, `DEAD`), double-jump, combat combos, FP and cooldown management.
- **`godot/enemy.gd`**: Flexible enemy AI controller supporting melee, shielded blockers, leashed archers with projectiles, and armored brutes.
- **`godot/room.gd`**: Multi-layer parallax environment renderer, one-way collision platforms, dynamic PointLight2D torches, and prop placement.
- **`godot/hud.gd`**: Code-drawn gothic HUD in Cinzel typography, including dynamic HP/FP bars with damage trails, cooldown overlays, rolling souls counter, and fog-of-war minimap.
- **`godot/sheet_util.gd`**: Dynamic sprite sheet and FX animation loader supporting variable frame dimensions and hot-swappable art assets.
