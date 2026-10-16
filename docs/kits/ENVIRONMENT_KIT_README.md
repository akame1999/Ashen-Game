# Ashen Veil — Godot 4 Environment Background Kit

This is a ready-to-open Godot 4 project containing four distinct dark-fantasy environment background plates for Ashen Veil. The images are 1672 × 941 (near 16:9) and are optimized JPEGs intended for opaque environment scenery. Three unique scenes came from the supplied images; one upload was a duplicate, so a new companion eclipse-necropolis scene was added for the fourth biome.

## Environments

| File | Region | Visual direction |
|---|---|---|
| `assets/backgrounds/01_drowned_march.jpg` | The Drowned March | Moonlit water, ruins and cool blue mist |
| `assets/backgrounds/02_ashen_chapel.jpg` | The Ashen Chapel | Red-orange dusk, lit cathedral windows |
| `assets/backgrounds/03_cinder_bastion.jpg` | The Cinder Bastion | Volcanic fortress, lava and embers |
| `assets/backgrounds/04_veiled_throne.jpg` | The Veiled Throne | Violet eclipse, ancient gothic skyline |

## Open the environment gallery

1. Extract the folder.
2. Open Godot 4.x.
3. Choose **Import** and select this folder (the one containing `project.godot`).
4. Open the project and press **F6** or **F5**.

Controls:
- `1`–`4`: choose an environment.
- `A` / `D` or `Left` / `Right`: previous / next environment.
- `F11`: toggle fullscreen.
- The on-screen Previous / Next buttons also work.

## Use a background in your game

### Easiest option — add a Sprite2D background

1. Copy the `assets/backgrounds/` folder and `scripts/environment_backdrop.gd` into your game project.
2. In your main level, add a `Sprite2D` as a child of the world root, then attach `environment_backdrop.gd` (or instance `scenes/environment_backdrop.tscn`).
3. Move the backdrop behind playable platforms; it defaults to `z_index = -100`.
4. Select `Region Index` in the Inspector to choose the environment.
5. Keep your player, enemies and platforms on higher z-index values.

The helper fits the image to the current viewport, uses a small camera-follow parallax offset, and re-fits on viewport size changes. The supplied images are complete scene plates, so this is **single-plane parallax** rather than independently moving foreground/midground/far layers. For long levels, use room-sized backdrops or create separately painted layers to avoid exposing image edges.

### Import settings

Godot should import JPEGs automatically. Recommended for backgrounds:
- **Mipmaps:** optional; useful when the artwork is scaled down.
- **Filter:** Linear.
- **Repeat:** Disabled (the images are not seamless tiles).
- Do not use these as collision geometry; they are visual backgrounds only.

## Folder structure

```text
AshenVeil_Godot_Environment_Kit/
├── project.godot
├── scenes/
│   ├── background_gallery.tscn
│   └── environment_backdrop.tscn
├── scripts/
│   ├── background_gallery.gd
│   └── environment_backdrop.gd
└── assets/
    ├── backgrounds/
    │   ├── 01_drowned_march.jpg
    │   ├── 02_ashen_chapel.jpg
    │   ├── 03_cinder_bastion.jpg
    │   └── 04_veiled_throne.jpg
    └── previews/
        └── environment_contact_sheet.jpg
```

Art files were supplied by the project owner in this conversation and converted to optimized JPEGs for game-background use. This package does not include character sprites, collision meshes, music, sound effects, or third-party libraries.
