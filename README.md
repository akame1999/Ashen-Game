# Code Lyoko — Unity Prototype

Unity editor: `6000.6.7f1`; template: Universal 3D (URP).

## Start the prototype
1. Open `Assets/_Project/Scenes/Prototype_Scene.unity`.
2. Wait for scripts to compile.
3. Run **Tools → Code Lyoko → Setup Combat Prototype**.
4. Press Play and click the Game view.

## Controls
- WASD / arrows: move
- Shift: run
- J or left mouse button: melee attack
- Space: dodge (brief invulnerability)

## Combat prototype
- Player health and dodge invulnerability
- Short-range directional melee attack and temporary slash arc
- Training enemy that approaches, visibly telegraphs its attack by flashing orange, hits, and recovers
- Temporary on-screen health HUD

This is a gameplay greybox, not production combat. It uses primitive visuals, simple range checks, and a temporary OnGUI HUD. Attack timings, damage and enemy behavior must be playtested and tuned. The movement/animation remains procedural until a rigged character and licensed animation clips are imported.

The title is a working title; it refers to an existing franchise name. Use an original title and original IP before public/commercial release.
