# PROJECT DECISIONS

Record choices with date, context, alternatives and consequences. Do not silently change established decisions.

## D001 — PC-first, single-player
**Decision:** Start offline-first on PC.  
**Reason:** Keep scope manageable and avoid multiplayer/backend complexity.  
**Review when:** a stable vertical slice exists.

## D002 — Unity URP
**Decision:** Use Unity with URP for the first prototype. Pin the exact supported version in the project.  
**Reason:** Practical 3D workflow, broad learning resources and C# iteration.  
**Review when:** a concrete technical limitation appears.

## D003 — Modular procedural dungeons
**Decision:** Handcraft room modules and generate their arrangement from a validated graph.  
**Reason:** Variation without sacrificing combat readability or level quality.  
**Review when:** repeated seed tests reveal limitations.

## D004 — Seeded runs and persistence
**Decision:** Store the dungeon seed and run state; loading must not reroll the dungeon.  
**Reason:** Reproducible debugging and fair progression.

## D005 — Original intellectual property
**Decision:** “Code Lyoko” is a temporary working title only; the game should use original world, characters, names, logos and assets. Choose a distinct title before public/commercial release.  
**Reason:** Avoid confusion with an existing franchise and protect the project's own identity.
