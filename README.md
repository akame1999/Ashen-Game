# Ashen Game (Unity)

2D dark-fantasy action platformer in the spirit of Mandragora: Whispers of the Witch Tree.
Souls-like combat (stamina, dodge i-frames, telegraphed enemy attacks) with metroidvania structure planned.

## Open it
1. Install Unity Hub and Unity 6 (6000.0.x LTS). Newer 6000.x editors will offer to upgrade the project.
2. Unity Hub > Add > select this folder.
3. Menu **Ashen > Build Starter Scene**, then press Play.

## Controls (legacy Input Manager)
| Action | Keys |
|---|---|
| Move | A / D or arrows |
| Jump | Space (hold for higher) |
| Attack | J or left mouse |
| Dash (i-frames) | Left Shift or K |
| Respawn | R |
| Wipe save (checkpoint + boss) | F9 |

## Layout
- `Assets/Scripts/Player` player controller (coyote time, jump buffer, dash, attack, stamina)
- `Assets/Scripts/Combat` Health + shared melee hit check
- `Assets/Scripts/Enemies` state-machine enemy (patrol, chase, wind-up, strike, recover) + `BossEncounter` (boss health bar, enrage phase at 50% HP)
- `Assets/Scripts/Core` camera follow, parallax, sprite animator, checkpoints, save/load (PlayerPrefs), torch flicker, placeholder sprites
- `Assets/Scripts/UI` temporary HUD
- `Assets/Scripts/Editor` one-click starter scene builder

Art is generated pixel art in a dark-fantasy style (`Tools/import_character_art.py` aligns externally made character frames onto 192x128 canvases, 72 px/unit; the old procedural `Tools/generate_sprites.py` is kept), `Tools/generate_backgrounds_painted.py` (painterly moonlit sky + hazy keep/ridges, ruins + dead trees, foreground grass and mist, 64 px/unit; the old pixel-art `generate_backgrounds.py` is kept), `Tools/generate_props_painted.py` (painted wrought-iron torches with flame frames + glow, seamless hanging chains, broken pillars, rubble, gravestones; 128 px/unit; the old pixel-art `generate_props.py` is kept), `Tools/generate_environment_painted.py` (painterly lit stone ground/platform tiles, 256px at 128 px/unit, 9-sliced; needs numpy) and `Tools/generate_environment.py` (checkpoint pillar, pixel art), shared grading in `Tools/stylize.py`: rim light, glowing eyes, dithered fog, atmospheric perspective); replace the PNGs under `Assets/Resources/` with real art any time.

## Roadmap
Boss fight (first boss, the Hollow Warden, done: enrage phase + health bar; more bosses/arena gates planned), skill tree/items, interconnected rooms with ability gates, full save/load (checkpoint + boss state persist via PlayerPrefs; touch a pillar to set respawn), parallax + 2D lighting, animation and audio.
