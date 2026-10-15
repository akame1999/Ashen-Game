# Region Background Art

Original scalable SVG illustrations used by the Python game renderer.

- `drowned_march.svg`
- `ashen_chapel.svg`
- `cinder_bastion.svg`
- `veiled_throne.svg`

These files contain background scenery only. Playable platforms, enemies, player, attacks and HUD are drawn/rendered separately by Pygame. The loader scales the scenes for camera parallax and falls back to procedural scenery if SVG decoding is unavailable.

The SVGs are authored for this project; no third-party sprite or texture pack is required.
