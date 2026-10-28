# TASKS AND MILESTONES

Use [ ] for not started, [~] for in progress, [x] for verified complete. Do not mark tasks complete until tested.

## M0 — Repository baseline
- [ ] Confirm Unity version and add README/setup instructions.
- [ ] Configure Unity .gitignore and Git LFS policy if needed.
- [ ] Confirm documentation and no secrets/build outputs.
**Acceptance:** clean clone opens in Unity.

## M1 — Camera and movement
- [ ] Create greybox scene and floor/walls.
- [ ] Implement camera follow and isometric framing.
- [ ] Implement camera-relative movement and collision.
- [ ] Test corners, walls, slopes and camera bounds.
**Acceptance:** predictable movement without wall clipping.

## M2 — Character
- [ ] Import one licensed character.
- [ ] Verify scale, materials, rig and animation controller.
- [ ] Add idle, locomotion and turning.
**Acceptance:** animation follows movement without broken references.

## M3 — Combat
- [ ] Add health and stamina.
- [ ] Add one attack, dodge and hit reaction.
- [ ] Add one enemy with telegraphed attack.
- [ ] Test damage timing and defeat/reset.
**Acceptance:** repeatable fair fight.

## M4 — Dungeon generation
- [ ] Create 5–8 room greyboxes and connectors.
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
