# Phase 1 — Camera and Movement Test Plan

**Purpose:** verify the camera-relative movement foundation in Unity 6.6 (`6000.6.7f1`) / URP before adding more content.

**Status:** implementation is in GitHub. Manual acceptance tests remain pending until run in the local Unity Editor. Record actual results; do not assume a test passed because scripts compile.

## Before testing
1. Close Play mode.
2. Open `Assets/_Project/Scenes/Prototype_Scene.unity`.
3. Wait for compilation. Resolve red Console errors first.
4. Run **Tools → Code Lyoko → Setup Phase 1 Prototype**.
5. Run **Tools → Code Lyoko → Validate Phase 1 Prototype**.
6. Open the Game tab, enter Play mode, click inside Game view so it receives keyboard focus.
7. Press F1 if needed to show or hide the diagnostics panel.

## Controls
- WASD or arrow keys: move relative to the camera.
- Hold Shift + movement: run.
- F1: toggle the Phase 1 debug overlay.
- Combat controls are outside this test's acceptance scope.

## Test matrix

| ID | Action | Expected result | Result |
|---|---|---|---|
| P1-01 | Enter Play mode and stand idle for 5 seconds | Player stays on floor; camera stays framed; speed approaches 0 | Not tested |
| P1-02 | Tap W briefly | Player begins moving forward relative to camera; no teleport | Not tested |
| P1-03 | Hold W for 3 seconds | Player moves steadily; camera follows smoothly | Not tested |
| P1-04 | Hold A, S, D individually | Each direction is camera-relative and repeatable | Not tested |
| P1-05 | Hold W+D | Diagonal movement is not faster than straight movement | Not tested |
| P1-06 | Hold W+Shift, then release Shift while keeping W | Movement accelerates toward run speed, then slows to walk speed | Not tested |
| P1-07 | Release all movement keys while moving | Player decelerates smoothly and settles into idle animation | Not tested |
| P1-08 | Move into each of the four walls | CharacterController cannot pass through a wall | Not tested |
| P1-09 | Move into each corner at an angle | Player slides/collides without passing through or becoming trapped indefinitely | Not tested |
| P1-10 | Press F1, inspect values while moving/stopped | Input, speed, grounded state, position and camera status are readable and plausible | Not tested |
| P1-11 | Temporarily click elsewhere, then click Game view | Keyboard input responds again only when Game view is focused | Not tested |
| P1-12 | Exit and re-enter Play mode twice | No duplicated player/camera/wall objects; no new Console errors | Not tested |
| P1-13 | Run editor validation menu again after scene reload | No missing scripts; camera, player, floor and wall references are found | Not tested |

## Acceptance criteria
Phase 1 passes only when:
- P1-01 through P1-13 have been run and failures are fixed or documented.
- The Editor Console has no new red errors attributable to the prototype.
- Player movement is predictable, camera stays readable and boundary collisions work.
- `Tools → Code Lyoko → Validate Phase 1 Prototype` reports zero structural issues.

## Record a failure
For any failed test, capture:
1. Test ID and steps taken.
2. Expected versus actual result.
3. Console error text (full message and stack trace if present).
4. Screenshot or short recording of the issue.
5. Whether the issue repeats after exiting and re-entering Play mode.
