# Code Lyoko — Unity Prototype

Unity editor: `6000.6.7f1`; template: Universal 3D (URP).

## Start the prototype
1. Open `Assets/_Project/Scenes/Prototype_Scene.unity`.
2. Wait for scripts to compile.
3. If any materials appear bright magenta, select **Tools → Code Lyoko → Repair Prototype Materials**.
4. To make the placeholder movement animation more visible, select **Tools → Code Lyoko → Upgrade Player Locomotion Placeholder**.
5. To tighten the camera framing and improve contrast, select **Tools → Code Lyoko → Improve Prototype Arena Visibility**.

## Combat test
1. Select **Tools → Code Lyoko → Setup Combat Prototype** to add the training enemy, health, melee, dodge and HUD.
2. Press Play and click the Game view.

Controls:
- WASD / arrows: move
- Shift: run
- J or left mouse: melee attack
- Space: dodge (brief invulnerability)

The training enemy approaches, telegraphs attacks by flashing orange, strikes, and recovers. The temporary HUD displays player/enemy health. Hit reactions squash and shake the visual model briefly; player attacks animate the right arm; dodges leave a short cyan afterimage trail.

## Current animation stage
The temporary mannequin consists of primitive meshes. Procedural animation swings arms and legs with different walk/run stride and cadence, plus body bounce and torso lean. This validates the animation system but is not a finished character. Replace the primitives with an original, properly rigged model and licensed authored animation clips later.

## Common materials issue
If the floor, player or grid appears magenta, use **Tools → Code Lyoko → Repair Prototype Materials**. The tool reassigns supported URP shaders/material colors to existing scene objects. If it remains magenta, verify that URP packages imported correctly and check the Console for shader compilation errors.

## Repository hygiene
Commit `Assets/`, generated `.meta` files, `Packages/manifest.json`, `Packages/packages-lock.json`, and `ProjectSettings/`. Do not commit Unity's `Library/`, `Temp/`, `Logs/`, build outputs or local IDE files.

The project title is a working title that matches an existing franchise. Choose a distinct title and keep all characters, world elements, branding and assets original before any public/commercial release.
