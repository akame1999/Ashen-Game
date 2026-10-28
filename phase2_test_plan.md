# Phase 2 — Character and Animation Test Plan

**Character:** Veyr Wanderer, an original stylized articulated character with a Generic Avatar and bone-attached mesh parts.
**Status:** generator code is in GitHub; generated Unity assets and visual tests require local generation and testing.

## Build
1. Stop Play mode and open `Assets/_Project/Scenes/Prototype_Scene.unity`.
2. Wait for compilation; resolve red Console errors first.
3. Select **Tools → Code Lyoko → Phase 2 → Build Rigged Character and Animations**.
4. Confirm Unity generates a prefab, armature hierarchy, character materials, Animator Controller and four clips under `Assets/_Project/Characters/VeyrWanderer/`.
5. Select **Tools → Code Lyoko → Phase 2 → Validate Character Rig** and review the `[Phase 2 ...]` Console report.

## Controls
- WASD / arrows: move.
- Shift: run.
- J / left click: attack if combat setup exists.
- Space: dodge if combat setup exists.

## Test matrix

| ID | Action | Expected result | Result |
|---|---|---|---|
| P2-01 | Inspect character prefab | Animator, valid Generic Avatar, armature, and multiple mesh parts exist | Not tested |
| P2-02 | Run rig validation menu | Meshes are valid and attached within armature; controller parameters and clips exist | Not tested |
| P2-03 | Stand idle for 5 seconds | Idle breathing/sway loops without severe gaps or parts flying away | Not tested |
| P2-04 | Walk forward/back/left/right | Walk clip moves arms and legs in opposing phases | Not tested |
| P2-05 | Hold Shift while moving | Run clip has visibly faster cadence and longer stride | Not tested |
| P2-06 | Release movement | Blend Tree returns to idle smoothly | Not tested |
| P2-07 | Press J or left-click near training enemy | Attack clip plays and returns to locomotion | Not tested |
| P2-08 | Inspect feet and floor | Feet remain close to the floor; no major hover/sink | Not tested |
| P2-09 | Move against all arena walls | CharacterController collision still works; visual rig does not move gameplay root | Not tested |
| P2-10 | Receive an enemy hit | Character visual reacts without detaching parts | Not tested |
| P2-11 | Exit and re-enter Play mode twice | No duplicate visual prefab and no new Console errors | Not tested |
| P2-12 | Reopen scene and validate again | Character prefab/controller/clips remain assigned | Not tested |

## Acceptance criteria
- Structural validation passes.
- No missing-script or animation-binding errors.
- Idle, walk, run and attack visibly play in Play mode.
- CharacterController remains responsible for gameplay movement; Animator root motion remains disabled.
- All mesh pieces remain attached to their intended bones and don't separate during movement.
- Manual results are recorded before Phase 2 is marked complete.

## Scope note
This version uses rigid mesh parts parented to a bone hierarchy, which is more reliable than the previous generator's failed bind-pose setup for this stylized prototype. It does not provide smooth skin deformation at the joints. The next character-art milestone is a single continuous mesh with proper skin weights or a licensed Humanoid model; neither should be treated as complete until imported and tested.
