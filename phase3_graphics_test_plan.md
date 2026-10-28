# Graphics Pass — Dark-Fantasy Courtyard Test Plan

**Status:** editor setup code is committed; generate and visually test the pass in local Unity before marking complete.

## Apply
1. Stop Play mode and open `Assets/_Project/Scenes/Prototype_Scene.unity`.
2. Wait for script compilation; resolve red Console errors before continuing.
3. Select **Tools → Code Lyoko → Graphics → Apply Dark Fantasy Graphics Pass**.
4. Select **Tools → Code Lyoko → Graphics → Validate Graphics Pass** and read the Console report.
5. Save if the scene is marked dirty, then enter Play mode.

## Test matrix

| ID | Test | Expected result | Result |
|---|---|---|---|
| GFX-01 | Inspect floor | Varied slate paving has clearly visible joints | Not tested |
| GFX-02 | Inspect arena perimeter | Ruined pillars and trim define the space without covering the player | Not tested |
| GFX-03 | Inspect braziers | Four amber light pools provide warm contrast without washing out materials | Not tested |
| GFX-04 | Inspect central rune | Spectral-blue accent is visible but not brighter than the character | Not tested |
| GFX-05 | Use normal Game view | Player and enemy silhouettes remain readable | Not tested |
| GFX-06 | Move around the floor and into walls | Original movement and wall colliders still behave as before | Not tested |
| GFX-07 | Fight the training enemy | Enemy telegraph and hit/dodge effects remain readable | Not tested |
| GFX-08 | Inspect distance and shadows | Fog adds depth without hiding routes or enemies | Not tested |
| GFX-09 | Inspect Console | No errors from graphics generation, materials or optional Volume setup | Not tested |
| GFX-10 | Compare runtime responsiveness | No unacceptable slowdown from added lights/renderers | Not tested |
| GFX-11 | Run validation command | At least 49 tiles, four pillar sets, four braziers, rune, floor/wall colliders and camera detected | Not tested |
| GFX-12 | Run setup a second time | No duplicate root or double set of decorations | Not tested |
| GFX-13 | Reopen Unity after graphics setup | GlobalVisualVolume references a saved profile with persisted overrides | Not tested |
| GFX-14 | Walk into environment props | Pillars and brazier structure block movement; paving/rubble remain decorative | Not tested |

## Acceptance criteria
- All tests are run and failures documented/fixed.
- Player, enemy and attack telegraphs remain readable at the normal gameplay camera scale.
- Decorative items do not change gameplay collision.
- No new red Console errors.
- Optional post-processing may be unavailable; lighting and material improvements should still work.

## Limitations
The pass uses generated primitive geometry and flat materials. It does not provide high-poly architecture, hand-painted texture maps, decals, bespoke terrain, volumetric light shafts or final production VFX. Those can be added after camera composition and tone are accepted.
