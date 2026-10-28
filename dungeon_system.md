# DYNAMIC DUNGEON SYSTEM

## Goal
Each entry can produce a different dungeon layout and encounter mix while remaining navigable, fair and reproducible. Use handcrafted modular rooms plus procedural assembly; do not generate every detail without design constraints.

## What changes per run
- Room order and branch structure
- Optional rooms, locked doors and shortcuts
- Enemy groups and patrol/ambush placement
- Trap selection and environmental modifier
- Loot/chest locations and reward rolls
- Boss modifier or arena variant, where fair

Story-critical rooms, key clues and progression items should remain reachable and deterministic enough to prevent softlocks.

## Generation pipeline
1. Choose a seed and DungeonDefinition.
2. Build a room graph with entrance, required route, optional branches and exit.
3. Enforce room-count, difficulty and connector constraints.
4. Validate entrance-to-exit reachability and required key/door dependencies.
5. Select compatible room prefabs and align connector anchors.
6. Spawn encounters using a difficulty budget.
7. Place loot, traps and interactables using authored spawn anchors.
8. Run validation and retry a bounded number of times if invalid.
9. Store seed, generator version and persistent run state.

## Room data
Each room needs a stable ID, type/tags, dimensions, door connectors, spawn anchors, loot anchors, hazard anchors and navigation assumptions. Connectors need matching type/orientation. Keep collision and gameplay routes readable from the isometric camera.

## Encounters and loot
Use weighted tables and difficulty budgets rather than unrestricted random choice. Ensure every required key or quest item can be acquired. Enemies need clear telegraphs, safe spawn distances and sufficient arena space. Rewards should match risk and player progression.

## Persistence
Store seed, generator version, visited rooms if needed, opened chests, defeated boss, collected unique items, door/key state and exit state. Reloading the same run must not regenerate it. Version the data so changes to room pools can be handled safely.

## Test matrix
- [ ] Entrance always reaches exit.
- [ ] All required objectives are reachable.
- [ ] No incompatible connectors or blocked doors.
- [ ] No critical spawn inside geometry.
- [ ] Enemies do not spawn inside walls or immediately on player.
- [ ] Key and loot requirements cannot softlock progress.
- [ ] Repeated seed reproduces layout.
- [ ] Different seeds produce meaningful variation.
- [ ] Save/load preserves run state.
- [ ] Generation terminates within bounded attempts.
