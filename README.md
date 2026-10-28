# Ashen-Game — Unity Prototype

Unity editor: `6000.6.7f1`; template: Universal 3D (URP).

## Phase 1 — Camera and movement
1. Open `Assets/_Project/Scenes/Prototype_Scene.unity`.
2. Wait for scripts to compile and resolve red Console errors.
3. Select **Tools → Code Lyoko → Setup Phase 1 Prototype**.
4. Select **Tools → Code Lyoko → Validate Phase 1 Prototype**.
5. Press Play, click Game view, use WASD/arrows, Shift to run, and F1 for diagnostics.
6. Record results in `phase1_test_plan.md`.

## Phase 2 — Rigged character and animations
1. Open the prototype scene and wait for scripts to compile.
2. Select **Tools → Code Lyoko → Phase 2 → Build Rigged Character and Animations**.
3. Unity creates an original stylized skinned character, bone hierarchy, Generic Avatar, prefab, materials, meshes, Animator Controller and keyframed Idle/Walk/Run/Attack clips under `Assets/_Project/Characters/VeyrWanderer/`.
4. Select **Tools → Code Lyoko → Phase 2 → Validate Character Rig** and read the `[Phase 2 ...]` Console report.
5. Press Play. WASD/arrows walk, Shift runs, J/left click attacks if combat setup is present.
6. Record results in `phase2_test_plan.md`.

The generated model is an original stylized prototype, not a high-detail production hero. Its body/armor sections use SkinnedMeshRenderers weighted to a Generic bone hierarchy, with authored keyframed animation clips. It is not yet a Humanoid Avatar for broad retargeting. Replace or refine it later with a high-detail model and properly licensed animation assets if required.

## Combat prototype
Select **Tools → Code Lyoko → Setup Combat Prototype** to add the training enemy, health, melee, dodge and HUD. Controls: WASD/arrows move; Shift run; J/left click attack; Space dodge.

## Troubleshooting
- If materials appear magenta, stop Play mode and select **Tools → Code Lyoko → Repair Prototype Materials**.
- If scene-edit menus are disabled, stop Play mode and wait for script compilation.
- If validation finds missing scripts/assets, fix the Console report before retrying the builder.
- Do not disable SSL verification to work around Package Manager certificate issues.

## Repository hygiene
Commit `Assets/`, generated `.meta` files, `Packages/manifest.json`, `Packages/packages-lock.json`, and `ProjectSettings/`. Do not commit Unity's `Library/`, `Temp/`, `Logs/`, build outputs or local IDE files.

The project title is a working title matching an existing franchise. Choose an original title and keep the game world, characters, branding and assets original before public/commercial release.
