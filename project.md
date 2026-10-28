# CODE LYOKO — PROJECT OVERVIEW & DEVELOPMENT PLAN

> Working title. “Code Lyoko” is an existing entertainment franchise name; use an original title before public/commercial release and do not use its protected characters, story, logos, or assets without permission.

## Vision
Create an original 3D dark-fantasy, single-player action RPG for PC with an elevated isometric camera, deliberate stamina-aware combat, exploration, meaningful quests, and replayable procedural dungeons. Take broad inspiration from challenging action RPGs, but build original characters, world, art, and mechanics.

## Target and tools
- Engine: Unity 6 LTS (or another supported LTS version; pin the chosen version in the repo).
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
- [ ] Confirm project title is a working title and establish original IP direction.
- [ ] Keep the 13 Markdown files at repository root.
- [ ] Create Unity URP project using the chosen Unity version.
- [ ] Add Unity `.gitignore`; track `Assets/`, `Packages/manifest.json`, `Packages/packages-lock.json`, and `ProjectSettings/`.
- [ ] Add README with setup/version notes.
**Done when:** a clean clone opens in Unity without missing packages or committed cache/build files.

### Phase 1 — Camera and movement prototype
**Owner:** Human integrates/tests; ChatGPT drafts C#; Claude reviews.  
- [ ] Create a greybox test scene with floor, walls, and a capsule player.
- [ ] Configure an orthographic or carefully tuned perspective isometric camera.
- [ ] Implement camera-relative movement, acceleration/deceleration, and collision.
- [ ] Add camera follow and bounds; avoid clipping through walls.
- [ ] Choose one input approach and document it.
**Done when:** movement feels predictable, camera stays readable, and player cannot walk through blockers.

### Phase 2 — Character foundation
- [ ] Replace capsule only after movement is stable.
- [ ] Import one legally usable character model; verify scale, materials, rig and animation.
- [ ] Add idle, walk/run, turn, and stop animations.
- [ ] Ensure animation state matches movement without foot sliding severe enough to distract.
**Done when:** character runs in the test scene on the intended machine.

### Phase 3 — Combat prototype
- [ ] Define health, stamina, hit detection, damage, hit reaction, dodge and recovery.
- [ ] Add one test enemy with telegraphed attacks and a defeat state.
- [ ] Tune lock-on/targeting only if the design needs it.
- [ ] Test hit timing, invulnerability windows, and stamina costs.
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

## First actions
1. Verify repository contains these docs and no accidental secrets.
2. Create/open the Unity URP project and commit the clean baseline.
3. Build only the camera + movement prototype. Do not begin combat or mass asset generation until it passes tests.
