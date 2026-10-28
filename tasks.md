# TASKS AND MILESTONES

Use [ ] for not started, [~] for implemented/in progress, [x] only after the acceptance criteria have been tested. Code being on GitHub does not mean Unity runtime behavior is verified.

## M0 — Repository baseline
- [~] Unity URP project opened locally (editor: `6000.6.7f1`).
- [~] Documentation, scripts and core Unity folders present in GitHub.
- [ ] Fresh clone opens without missing files/packages or compile errors.
**Acceptance:** clean clone opens in Unity with no missing script references.

## M1 — Camera and movement (Phase 1 implementation delivered; manual tests pending)
- [~] Greybox scene with floor, walls and player.
- [~] Orthographic isometric follow camera.
- [~] Camera-relative WASD/arrow movement and turning.
- [~] Acceleration and deceleration tuning added.
- [~] CharacterController collision and boundary wall colliders.
- [~] F1 movement diagnostics overlay.
- [~] Editor setup and validation commands added.
- [ ] Verify cardinal and diagonal movement, walk/run transition, release/deceleration.
- [ ] Test all four walls and corners for collision/leak-through.
- [ ] Verify camera follow, framing and no unexpected wall clipping.
- [ ] Run `Tools → Code Lyoko → Validate Phase 1 Prototype` and fix every failure.
**Acceptance:** predictable movement, useful camera framing, no escape through blockers; all manual tests pass. Do not mark complete before local Unity verification.

## M2 — Rigged character and animation
- [~] Add Phase 2 editor generator for an original articulated character, bone hierarchy and Generic Avatar.
- [~] Generate Animator Controller and keyframed Idle/Walk/Run/Attack clips on demand.
- [~] Bridge movement/combat input to Animator parameters with root motion disabled.
- [~] Add structural validation and `phase2_test_plan.md`.
- [ ] Run build command locally and verify prefab, mesh bindings, Avatar and controller.
- [ ] Playtest all clips, floor contact, collision and hit feedback.
- [ ] Consider an imported Humanoid character and retargeted clips after the Generic rig works.
**Acceptance:** bone-attached character animates idle/walk/run/attack without missing references or detached parts; local tests pass.

## M3 — Combat prototype
- [~] Prototype health, melee, dodge, telegraphed enemy, HUD and placeholder feedback.
- [ ] Test damage range/facing, cooldown, dodge invulnerability, repeat hits and defeat/reset.
- [ ] Tune stamina, attack timing, enemy recovery and hit feedback.
**Acceptance:** repeatable fair fight; no unintended repeated hit from one attack.

## M4 — Dungeon generation
- [ ] Create 5–8 greybox room prefabs and connectors.
- [ ] Generate connected graph from seed.
- [ ] Validate entrance-to-exit path.
- [ ] Place prefabs and verify no connector mismatch.
**Acceptance:** multiple seeds produce playable layouts.

## M5 — Encounters and persistence
- [ ] Add enemy spawn tables and difficulty budget.
- [ ] Add weighted loot and traps.
- [ ] Save seed, opened chests, boss and unique items.
- [ ] Verify load restores the same run.
**Acceptance:** no reroll exploit or softlock.

## M6 — Vertical slice
- [ ] Hub, dungeon, mini-boss, quest and reward.
- [ ] UI, sound, settings and save/load.
- [ ] Fresh-save playtest and bug list.
**Acceptance:** complete playable loop.

## M7 — Expansion/polish
- [ ] Add content only after slice stability.
- [ ] Profile performance.
- [ ] Audit accessibility, save migration and licenses.
**Acceptance:** release checklist signed off.
