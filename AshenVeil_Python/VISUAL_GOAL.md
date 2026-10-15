# Ashen Veil — Visual Goal

The reference screenshots in [assets/reference_art](assets/reference_art/) define the target direction. The current Pygame prototype is a gameplay foundation; it is **not yet at the visual quality shown by the references**.

## Target experience

Build a polished 2D side-scrolling dark-fantasy Metroidvania with deliberate Soulslike combat, high-contrast painterly environments, responsive weapon animations, and a clear, ornate game HUD.

## Visual priorities

### 1. Environment and lighting
- Use layered hand-painted or carefully authored background art for moonlit gothic cities, ruined cathedrals, ravines, bridges, waterfalls, towers, and distant castles.
- Separate far skyline, mid-ground ruins, foreground arches and playable platforms into parallax layers.
- Add restrained fog, ember particles, torch pools, reflective water where appropriate, tattered banners, chains, vines, broken masonry, and environmental silhouettes.
- Keep platforms and hazards readable against the artwork; scenery must not hide enemies or critical ledges.
- Make the four biomes visually distinct: Drowned March (cold blue moonlight), Ashen Chapel (ember reds), Cinder Bastion (volcanic orange), and Veiled Throne (violet eclipse).

### 2. Player, enemies, and animation
- Replace procedural stick-like silhouettes with consistent character sprite sheets or rigged 2D animation.
- Provide idle, run, start/stop, jump, fall, land, dodge, hurt, death, light-combo, heavy, skill, and Soul Burst states.
- Give the player a recognisable cloak, armor silhouette, readable weapon shape, and facing direction.
- Create distinct hollow, archer, shield, elite, and boss designs. Use clear telegraphs before attacks.
- Keep visual sizes independent from collision geometry, and tune sprites to sit firmly on platform surfaces.

### 3. Combat feel
- Weapon swings need a clear wind-up, active hit window, and recovery. Continue to allow movement during compatible attacks.
- Use curved directional slash trails, sparks, restrained blood/impact particles, damage numbers, hit-stop, and optional screen shake.
- Make enemy hit reactions and health bars legible. Keep attacks accurate to facing and vertical position.
- Preserve three distinct weapon identities: Rookfang longsword, Gravetide twinblades, and Oathbreaker greatblade.

### 4. HUD and presentation
- Design an ornate high-contrast HUD for health, stamina, Soul Burst/skill resource, healing items, weapon selection, souls, area name, and a useful minimap.
- Add clear boss health/phase presentation and consistent iconography.
- Keep control hints out of the way of the playable area. Support fullscreen/windowed modes and resolutions without misaligning the world or UI.

### 5. Metroidvania level design
- Build interconnected rooms and vertical routes, not one long flat arena.
- Add ladders, drops, bridges, lifts, secrets, checkpoints, shortcuts, locked routes, and abilities that open previously unreachable areas.
- Use environment landmarks to communicate route choices, safe spaces, enemy ambushes, and boss entrances.
- Add room/area transitions, a reliable map, exploration rewards, and persistent progression.

## Implementation order

1. **Foundation:** keep the existing crash fix and input regression tests; preserve gameplay physics while improving art.
2. **First polished room:** one hand-authored background with parallax, proper player animation, two enemy types, torches/fog, and a readable combat HUD.
3. **Combat vertical slice:** all three weapon movesets, robust hitboxes, animation timing, hit reactions, healing, and one boss encounter.
4. **Exploration slice:** a connected set of rooms with vertical traversal, a checkpoint, a secret, and a shortcut.
5. **Expand biomes:** reuse the validated art/room pipeline for the other regions.
6. **Release polish:** settings, key remapping, audio, accessibility, performance tests, packaging and save/progression tests.

## Asset note

The checked-in screenshots are compact visual-reference thumbnails. They are not runtime art assets and should not be stretched into game backgrounds. Use them to guide original game artwork and composition. The scalable SVG scenes under `assets/backgrounds/` are the current runtime backgrounds and should be replaced progressively with higher-detail, layered art.
