# TECHNICAL DESIGN

## Target stack
Unity 6 LTS (pin version), URP, C#, Blender, Git/GitHub. PC-first, single-player, offline-first. Keep dependencies minimal and record package decisions.

## Suggested Unity layout
```
Assets/_Project/
  Art/{Characters,Environments,Materials,VFX}
  Audio/{Music,SFX,Ambience}
  Prefabs/{Characters,Enemies,Interactables,World,UI}
  Scenes/{Bootstrap,MainMenu,Prologue}
  Scripts/{Core,Player,Camera,Combat,Enemies,Interaction,Inventory,Quests,Dungeons,Dialogue,SaveSystem,UI}
  ScriptableObjects/{Items,Enemies,Weapons,Quests,DungeonRooms,DungeonEncounters}
Documentation/
```

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
Measure before optimizing. Use sensible texture sizes, modular assets and simple lighting initially. Never commit credentials. Audit licenses for models, textures, fonts, sounds and plugins. Do not extract copyrighted game assets without permission.
