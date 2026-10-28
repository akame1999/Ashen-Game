# Code Lyoko — Unity Prototype

This repository contains the game design documents and the first Unity movement prototype. The title is a working title; it refers to an existing franchise name, so select an original title before public/commercial release.

## Unity editor
- Editor version: `6000.6.7f1`
- Template: Universal 3D (URP)
- First milestone: isometric camera + player movement in a collision-bounded greybox arena.

## Play and upgrade the prototype
1. Open the project and wait for scripts to compile.
2. Open `Assets/_Project/Scenes/Prototype_Scene.unity`.
3. Select **Tools → Code Lyoko → Upgrade Player Locomotion Placeholder** to replace the old single capsule with a stylized primitive mannequin. Or select **Tools → Code Lyoko → Create Prototype Scene** to rebuild the greybox from scratch.
4. Press Play and click the Game view. Use WASD or arrow keys to walk; hold Shift to run.
5. Check that the camera follows the player and the perimeter walls block movement.

## Current animation stage
The temporary mannequin consists of simple primitive meshes. The movement script animates arm and leg pivots in opposite phases, changes the stride and cadence for running, and adds visible torso lean and body bounce. This is a prototype to verify movement/animation state wiring, not a finished character asset or authored humanoid animation clip.

When a licensed rigged character is imported, replace the primitive mannequin and use a real Animator Controller with suitable idle, walk, run, turn, dodge and combat clips. Keep root motion disabled while the CharacterController remains responsible for player movement.

## Source layout
- `Assets/_Project/Scripts/Player/IsometricPlayerController.cs`: camera-relative movement, facing direction, walk/run speed, gravity and collision.
- `Assets/_Project/Scripts/Player/PlayerLocomotionAnimator.cs`: visible procedural mannequin gait.
- `Assets/_Project/Scripts/Camera/IsometricCameraFollow.cs`: orthographic isometric follow camera.
- `Assets/_Project/Editor/PrototypeSceneSetup.cs`: generates the greybox scene and upgrades the placeholder mannequin.
- `Assets/_Project/Materials/`: placeholder URP materials.

Commit `Assets/`, generated `.meta` files, `Packages/manifest.json`, `Packages/packages-lock.json`, and `ProjectSettings/`. Do not commit Unity's `Library/`, `Temp/`, `Logs/`, build outputs or local IDE files.
