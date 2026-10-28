# Ashen-Game — Unity Prototype

Unity editor: `6000.6.7f1`; template: Universal 3D (URP).

## Phase 1: prepare and validate
1. Open `Assets/_Project/Scenes/Prototype_Scene.unity`.
2. Wait for scripts to compile. Fix all red Console errors before testing.
3. Select **Tools → Code Lyoko → Setup Phase 1 Prototype**.
4. Select **Tools → Code Lyoko → Validate Phase 1 Prototype**. Read the full `[Phase 1 ...]` report in the Console; fix any errors.
5. Press Play and click the Game view. Press F1 to show the debug overlay.

## Phase 1 controls and acceptance
- WASD / arrows: camera-relative move
- Shift: run
- F1: toggle diagnostics
- Movement should accelerate and decelerate, turn toward the direction of travel, and collide with boundary walls.
- Camera should remain orthographic and follow the Player.
- The debug overlay reports input, speed, grounded state, player position and camera assignment.

Use `phase1_test_plan.md` to run and record the manual checks. Do not mark Phase 1 complete until those checks pass on the target machine.

## Combat test (later milestone)
1. Select **Tools → Code Lyoko → Setup Combat Prototype**.
2. Press Play and click the Game view.
3. J or left click: attack; Space: dodge; WASD/arrows: move; Shift: run.

The combat scene is still a prototype using simple range checks and placeholder visuals. It is separate from Phase 1's movement acceptance criteria.

## Troubleshooting
- If any material appears magenta, stop Play mode and select **Tools → Code Lyoko → Repair Prototype Materials**.
- If Unity reports Missing (Mono Script), stop Play mode, wait for compilation, then inspect the Player hierarchy and Console before running the setup tool again.
- If Package Manager reports a certificate error, do not disable SSL verification; investigate the approved proxy/CA configuration separately.

## Repository hygiene
Commit `Assets/`, generated `.meta` files, `Packages/manifest.json`, `Packages/packages-lock.json`, and `ProjectSettings/`. Do not commit Unity's `Library/`, `Temp/`, `Logs/`, build outputs or local IDE files.

The title is a working title matching an existing franchise. Choose an original title and keep game world, characters, branding and assets original before public/commercial release.
