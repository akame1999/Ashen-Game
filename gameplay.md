# GAMEPLAY DESIGN

## Core loop
Explore a region → read environmental clues → encounter enemies and hazards → manage health/stamina/resources → find a route or secret → defeat a major threat or complete an objective → return with rewards and new knowledge.

## Camera and movement
Use an elevated isometric-style camera with clear player/enemy silhouettes. Movement should be camera-relative and collision-safe. Choose orthographic or perspective after testing readability and depth. Keep the camera stable during combat and avoid obscuring hazards.

## Combat pillars
- **Commitment:** attacks have readable wind-up, active frames and recovery.
- **Stamina:** dodging and attacks require deliberate resource management.
- **Telegraphing:** enemy attacks must be readable from the elevated camera.
- **Positioning:** facing, range, terrain and enemy grouping matter.
- **Feedback:** hit reactions, sound, VFX and UI communicate success without hiding gameplay.
Start with one weapon, one enemy, one dodge and one reliable hit reaction.

## Progression
Equipment and upgrades should change playstyle rather than only inflate stats. Memory-glass upgrades may require a narrative cost. Introduce mechanics gradually and communicate irreversible decisions.

## Exploration and interaction
Use readable landmarks, optional paths, environmental clues, locked gates, keys and shortcuts. Interactables need consistent prompts and clear feedback.

## Dynamic dungeons
Use handcrafted modular rooms assembled in different valid combinations. Vary layout, encounter groups, traps, loot and environmental modifiers. Preserve critical story rooms where continuity matters. See `dungeon_system.md`.

## UI and accessibility
Prioritize readable health/stamina, interaction prompts, subtitle controls, remappable inputs, audio sliders, camera sensitivity and reduced screen shake. Ensure important hazards do not rely on color alone.

## Minimum vertical slice
One hub, one small dungeon, one basic enemy, one mini-boss, one quest, one reward, one save/load cycle and a complete beginning-to-end play session.
