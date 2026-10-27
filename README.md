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
- `Assets/Scripts/Core` camera follow, placeholder sprites
- `Assets/Scripts/UI` temporary HUD
- `Assets/Scripts/Editor` one-click starter scene builder

Art is placeholder squares until real sprites are imported.

## Roadmap
Boss fight, skill tree/items, interconnected rooms with ability gates, checkpoints and save/load, parallax + 2D lighting, animation and audio.
