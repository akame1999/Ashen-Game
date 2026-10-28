# Code Lyoko — Unity Prototype

This repository contains the game design documents and the first Unity prototype scripts. The title is a working title; it refers to an existing franchise name, so select an original title before public/commercial release.

## Unity editor
- Editor version: `6000.6.7f1`
- Template: Universal 3D (URP)
- First milestone: isometric camera + player movement in a collision-bounded greybox arena.

## Create the prototype scene
1. Open this repository as a Unity project using the Unity version above.
2. Wait for scripts to compile. The package manager may report a Visual Studio integration certificate error on networks with TLS inspection; this is separate from the prototype scripts.
3. In Unity, select **Tools → Code Lyoko → Create Prototype Scene**.
4. Open `Assets/_Project/Scenes/Prototype_Scene.unity`.
5. Press Play and use WASD or arrow keys. Focus the Game view to send keyboard input.

The scene-creation command generates a floor, four boundary walls, a capsule player, a CharacterController, an isometric follow camera, placeholder materials and a directional light.

## Source layout
- `Assets/_Project/Scripts/Player/IsometricPlayerController.cs`: camera-relative movement and rotation.
- `Assets/_Project/Scripts/Camera/IsometricCameraFollow.cs`: orthographic isometric follow camera.
- `Assets/_Project/Editor/PrototypeSceneSetup.cs`: Unity menu action that builds the greybox scene.

The scene is generated locally by the Unity Editor and then should be committed along with generated `.meta` files once verified.
