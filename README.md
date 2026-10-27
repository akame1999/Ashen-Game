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

## Layout
- `Assets/Scripts/Player` player controller (coyote time, jump buffer, dash, attack, stamina)
- `Assets/Scripts/Combat` Health + shared melee hit check
- `Assets/Scripts/Enemies` state-machine enemy (patrol, chase, wind-up, strike, recover)
- `Assets/Scripts/Core` camera follow, parallax, sprite animator, checkpoints, placeholder sprites
- `Assets/Scripts/UI` temporary HUD
- `Assets/Scripts/Editor` one-click starter scene builder

Art is generated pixel art in a dark-fantasy style (`Tools/generate_sprites.py` (128px characters, 72 px/unit), `Tools/generate_backgrounds.py`, `Tools/generate_environment.py` (mossy stone ground/platform tiles + checkpoint pillar, 32 px/unit, 9-sliced), shared grading in `Tools/stylize.py`: rim light, glowing eyes, dithered fog, atmospheric perspective); replace the PNGs under `Assets/Resources/` with real art any time.

## Roadmap
Boss fight, skill tree/items, interconnected rooms with ability gates, save/load (checkpoints done: touch a pillar to set respawn), parallax + 2D lighting, animation and audio.
