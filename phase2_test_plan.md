# Phase 2 — Rigged Character and Animation Test Plan

**Character:** Veyr Wanderer, an original stylized segmented/skinned mesh with a Generic Avatar.
**Status:** builder source is in GitHub; generated Unity assets and visual tests remain pending.

## Build
1. Stop Play mode and open `Assets/_Project/Scenes/Prototype_Scene.unity`.
2. Wait for compilation; resolve red Console errors first.
3. Select **Tools → Code Lyoko → Phase 2 → Build Rigged Character and Animations**.
4. Confirm Unity generated the character prefab, Generic Avatar, materials, mesh assets, Animator Controller and four clips under `Assets/_Project/Characters/VeyrWanderer/`.
5. Select **Tools → Code Lyoko → Phase 2 → Validate Character Rig** and review every `[Phase 2 ...]` Console line.

## Controls
- WASD / arrows: move.
- Shift: run.
- J / left click: attack if combat setup exists.
- Space: dodge if combat setup exists.

## Test matrix

| ID | Action | Expected result | Result |
|---|---|---|---|
| P2-01 | Inspect character prefab | Animator, valid Generic Avatar, SkinnedMeshRenderers and bone assignments present | Not tested |
| P2-02 | Run rig validation menu | No missing mesh/bone references, controller parameters or clips | Not tested |
| P2-03 | Stand idle for 5 seconds | Idle breathing/sway loops without severe deformation or flicker | Not tested |
| P2-04 | Walk forward/back/left/right | Walk clip loops and legs/arms swing oppositely | Not tested |
| P2-05 | Hold Shift while moving | Run clip has a visibly faster cadence and longer stride | Not tested |
| P2-06 | Release movement | Blend Tree returns to idle smoothly | Not tested |
| P2-07 | Press J or left-click near the training enemy | Attack clip plays and returns to locomotion | Not tested |
| P2-08 | Inspect feet and floor | Feet remain close to the floor; no major hover/sink | Not tested |
| P2-09 | Move against all four walls | Existing CharacterController collision still works | Not tested |
| P2-10 | Receive an enemy hit | Character visual reacts briefly without breaking Animator playback | Not tested |
| P2-11 | Exit and re-enter Play mode twice | No duplicate visual prefab and no new Console errors | Not tested |
| P2-12 | Reopen scene and validate again | Character prefab/controller/clips remain assigned | Not tested |

## Acceptance criteria
- Structural validation passes.
- No missing-script or animation-binding errors.
- Idle, walk, run and attack visibly play in Play mode.
- CharacterController remains responsible for gameplay movement; Animator root motion is disabled.
- Manual results are recorded before Phase 2 is marked complete.

## Scope note
The generated Veyr Wanderer is an original stylized prototype, not a high-detail AAA character. Body/armor sections use skinned mesh renderers with a Generic bone hierarchy and authored keyframed clips. It is not yet a Humanoid Avatar for broad Mixamo retargeting, and its segmented rigid weights need further deformation polish.
