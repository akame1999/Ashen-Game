# TECHNICAL DESIGN

## Target stack
Unity 6.6 Update (`6000.6.7f1` currently used), URP, C#, Blender, Git/GitHub. PC-first, single-player, offline-first. Keep dependencies minimal and record package decisions.

## Suggested Unity layout
```
Assets/_Project/
  Art/{Characters,Environments,Materials,VFX}
  Audio/{Music,SFX,Ambience}
  Prefabs/{Characters,Enemies,Interactables,World,UI}
  Scenes/{Bootstrap,MainMenu,Prologue}
  Scripts/{Core,Player,Camera,Combat,Enemies,Interaction,Inventory,Quests,Dungeons,Dialogue,SaveSystem,UI}
  ScriptableObjects/{Items,Enemies,Weapons,Quests,DungeonRooms,DungeonEncounters}
```

## Phase 1 architecture
- `IsometricPlayerController`: camera-relative input, facing, acceleration/deceleration, walk/run, gravity and CharacterController collision.
- `IsometricCameraFollow`: orthographic follow camera and fixed elevated framing.
- `PlayerLocomotionAnimator`: visual-only placeholder gait; must not own gameplay movement.
- `PrototypeDebugOverlay`: F1 runtime diagnostics for input, horizontal speed, grounded state, position and camera follow.
- `PrototypeSceneSetup`: editor menus to create/repair/setup/validate the greybox and add combat test objects.
- `phase1_test_plan.md`: repeatable manual acceptance test matrix.

## Phase 2 character architecture
- `Phase2CharacterBuilder`: editor-only generator for an original articulated character, Generic Avatar, materials, bone-attached primitive meshes, animation clips, Animator Controller and prefab.
- `VeyrWanderer.prefab`: generated character asset with bone hierarchy and mesh parts parented to their controlling bones.
- Animator uses `MoveSpeed` (0 idle, 0.5 walk, 1 run) plus an `Attack` trigger.
- `PlayerLocomotionAnimator` bridges movement/combat input to the Animator while retaining the old procedural placeholder fallback.
- Root motion stays disabled so the existing CharacterController remains authoritative for movement/collision.
- This is a custom Generic rig with rigid mesh parts for the prototype, not yet a continuous skinned humanoid or Avatar for one-click retargeting.
- `phase2_test_plan.md` defines the local generation and visual acceptance tests.

## Graphics pass architecture
- `GraphicsUpgradeSetup`: Editor tool that rebuilds a `GraphicsPassRoot` containing 49 paving slabs, grout/cracks, perimeter trim, ruined pillars, braziers and lights, rubble and a central rune.
- New materials are generated under `Assets/_Project/Graphics/Materials/`; an optional global URP volume profile lives under `Assets/_Project/Graphics/Profiles/`.
- Original `TestFloor` and four wall colliders are preserved. Decorative geometry has no colliders and does not change gameplay collision.
- Render settings use cool ambient light, soft directional shadows, warm point-light pools and linear fog.
- URP bloom/vignette/color grading are set up via reflection and are optional; the base environment pass still works if those types are unavailable.
- `phase3_graphics_test_plan.md` covers readability, collision, Console and performance checks.

## Architecture principles
- One component, one clear responsibility.
- Use ScriptableObjects for reusable definitions where appropriate.
- Separate data from runtime behavior and narrative from combat logic.
- Avoid one giant player script.
- Document inspector references and package dependencies.
- Fail clearly for missing required references.
- Keep third-party assets separate and record their licenses.
- Make save data versionable and tolerate missing optional fields.

## Dungeon components
- `DungeonDefinition`: theme, room constraints, difficulty and allowed pools.
- `DungeonGenerator`: creates a graph from a seed and validates connections.
- `DungeonRoomData`: room type, connectors, dimensions, tags and spawn anchors.
- `DungeonAssembler`: places room prefabs and joins compatible connectors.
- `EncounterDirector`: chooses enemies/hazards within a difficulty budget.
- `LootTable`: weighted rewards with guaranteed progression drops where required.
- `DungeonRunState`: seed, generation version, opened chests, boss state and collected unique items.

Generate and validate a connected graph first, then place compatible room prefabs. Never assume random placement is valid.

## Save/load
Persist only what the vertical slice needs: checkpoint, player state, quest choices, key items and dungeon run state. Test missing/corrupt saves and version changes.

## Debugging
Reproduce → capture full error → identify responsible component → make one focused change → compile → test original case and edge cases → commit when verified.

## Performance and safety
Measure before optimizing. Use sensible texture sizes, modular assets and simple lighting initially. Never commit credentials. Audit licenses for models, textures, fonts, sounds and plugins. Do not commit Unity's Library/Temp/Logs or local IDE files. Do not extract copyrighted game assets without permission.
