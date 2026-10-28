# CODE LYOKO — PROJECT OVERVIEW & DEVELOPMENT PLAN

> Working title. “Code Lyoko” is an existing entertainment franchise name; use an original title before public/commercial release and do not use its protected characters, story, logos, or assets without permission.

## Vision
Create an original 3D dark-fantasy, single-player action RPG for PC with an elevated isometric camera, deliberate stamina-aware combat, exploration, meaningful quests, and replayable procedural dungeons. Take broad inspiration from challenging action RPGs, but build original characters, world, art, and mechanics.

## Target and tools
- Engine: Unity 6.6 Update, editor version `6000.6.7f1` currently in use.
- Rendering: Universal Render Pipeline (URP).
- Code: C#.
- Art: Blender; AI-assisted concept and 3D tools where licensing/export permits.
- Version control: Git/GitHub. Use Git LFS for large binary assets if needed.
- Initial target: Windows PC, offline single-player.
- Budget: prioritize free tools and original or properly licensed assets.

## Roles and responsibility
| Owner | Responsibility |
|---|---|
| Human developer (project owner) | Final decisions, Unity editor setup, playtesting, accepting changes, asset-license checks, releases and commits |
| ChatGPT | Break down tasks, draft scripts, explain Unity setup, debug from actual logs, maintain documentation |
| Claude | Independent code review, architecture critique, edge cases, narrative consistency |
| Gemini | Alternative approaches, visual/reference analysis, design research and second opinions |
| Unity | Runtime integration, scene/prefab configuration, compilation and playtests |
| Blender / asset tools | Create, clean, rig, optimize and export art assets; validate each in Unity |

AI roles are suggestions, not guarantees. No AI should claim a feature is tested unless it was actually run. The human developer owns final verification.

## Development rules
1. Keep `main` stable. Work in short feature branches when possible.
2. Read the relevant documentation and existing code before changing anything.
3. One task per change; avoid unrelated rewrites.
4. Every feature needs acceptance criteria and a reproducible test.
5. Prefer placeholders and greyboxing until mechanics work.
6. Do not commit credentials, generated builds, caches, or unlicensed assets.
7. Record important choices in `decisions.md`; keep task status in `tasks.md`.
8. Build a small playable vertical slice before scaling the world.

## Milestones and task ownership

### Phase 0 — Repository and project baseline
**Owner:** Human; ChatGPT can guide.
- [~] Unity URP project opened locally and docs/scripts are in GitHub.
- [ ] Fresh-clone validation and package/network error cleanup.
**Done when:** a clean clone opens in Unity without missing packages or committed cache/build files.

### Phase 1 — Camera and movement prototype
**Owner:** Human integrates/tests; ChatGPT drafts C#; Claude reviews.
**Implementation delivered; local acceptance tests still pending.** See `phase1_test_plan.md`.
- [x] Greybox test scene with floor, perimeter walls and player.
- [x] Orthographic isometric follow camera.
- [x] Camera-relative WASD/arrow movement and rotation toward travel direction.
- [x] Acceleration/deceleration and separate walk/run speeds.
- [x] CharacterController collision with boundary colliders.
- [x] F1 diagnostics overlay for input, speed, grounded state, position and camera follow.
- [x] One-click setup and validation editor commands.
- [ ] Test behavior at corners, walls, different frame rates, and with keyboard focus in Game view.
- [ ] Run automated structural validation and complete manual test matrix.
**Done when:** movement is predictable, camera stays readable, and player cannot walk through blockers. Only mark accepted after local playtest passes.

### Phase 2 — Rigged character and locomotion animations
**Owner:** ChatGPT builds the editor pipeline; human runs generation and visual tests in Unity.
**Implementation delivered as an editor generator; local asset generation and acceptance tests pending.** See `phase2_test_plan.md`.
- [x] Generate original Veyr Wanderer bone-attached mesh parts with a bone hierarchy and Generic Avatar.
- [x] Generate Animator Controller and keyframed Idle/Walk/Run/Attack clips.
- [x] Connect movement/combat input to Animator parameters.
- [x] Add structural rig/controller/clip validation.
- [ ] Generate character assets in local Unity and inspect mesh bindings/materials.
- [ ] Verify idle, walk, run and attack in Play mode, foot placement and no Console errors.
- [ ] Decide whether to import a dedicated Humanoid rig and retargetable animation library after the generic rig passes.
**Done when:** Phase 2 tests pass on the target machine and the character animates cleanly in the arena.

### Phase 3 — Combat prototype
- [~] Prototype health, melee, dodge, telegraphed enemy, HUD and placeholder hit feedback are implemented.
- [ ] Test hit timing, ranges, invulnerability windows and defeat/reset.
- [ ] Tune balance and stamina before productionizing.
**Done when:** player can reliably fight and defeat one enemy; no repeated hits from a single attack unless intended.

### Phase 4 — Modular dungeon and generation
- [ ] Create 5–8 greybox room prefabs with consistent door connectors.
- [ ] Define room metadata and allowed connections.
- [ ] Generate a connected room graph from a seed before placing rooms.
- [ ] Validate entrance-to-exit reachability and connector compatibility.
- [ ] Instantiate rooms, then add spawn points, doors and exit.
- [ ] Keep a seed visible in debug UI for reproduction.
**Done when:** many seeds generate playable layouts without disconnected exits, overlapping doors, or softlocks.

### Phase 5 — Dynamic encounters, loot and persistence
- [ ] Use encounter budgets to select enemy groups and hazards.
- [ ] Add weighted loot tables with guaranteed progression items where needed.
- [ ] Persist seed, generation version, opened chests, defeated boss and collected unique items.
- [ ] On load, restore the same run instead of rerolling it.
- [ ] Add environmental modifiers only after baseline generation is stable.
**Done when:** entering a dungeon creates variation and reloading a run preserves its state.

### Phase 6 — Vertical slice
- [ ] One small hub, one dungeon theme, one mini-boss, a short quest, one reward and one save/load loop.
- [ ] Add basic sound, lighting, UI, pause menu and failure/retry flow.
- [ ] Playtest with fresh saves and collect issues.
**Done when:** a new player can complete the slice from start to reward without developer intervention.

### Phase 7 — Expand and polish
- [ ] Add content only after the slice is stable.
- [ ] Profile CPU/GPU and memory; optimize based on measurements.
- [ ] Add accessibility, settings, input remapping and reliable save migration.
- [ ] Audit asset licenses and credits before any public build.

## Weekly work cycle
1. Select one task from `tasks.md`.
2. Define expected behavior and acceptance tests.
3. Ask one AI for a focused implementation; provide related files and Unity version.
4. Ask another AI for review if the change is substantial.
5. Integrate in Unity, compile, playtest and fix issues.
6. Update docs/task status and commit a small verified change.

## Next steps
1. Pull latest `main` into local project and wait for script compilation.
2. Open `Prototype_Scene.unity`; run `Setup Phase 1 Prototype`.
3. Run `Validate Phase 1 Prototype`; review Console.
4. Press Play and complete `phase1_test_plan.md` before expanding the world.
