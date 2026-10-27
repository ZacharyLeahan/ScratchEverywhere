# Zach's Spider Adventure — game 21

[Scratch project 1396458859](https://scratch.mit.edu/projects/1396458859/) by
zacharyleahan, installed October 27, 2026. The project describes jumping on red
spiders, chaining stomps for combo scores, and defeating ten spiders on each of
ten levels. This installation keeps the original project JSON and all 125
assets unchanged; the only addition is an Xbox controller sidecar.

## Xbox controls

- D-pad or left stick Left/Right: move.
- A, D-pad Up, or left stick Up: jump.
- Y: restart (the game's on-screen R prompt).
- Back / Select: shared runtime pause, including Return to game list.

The installed files are `E:\ScratchEverywhere\Zachs-Spider-Adventure.sb3` and
`Zachs-Spider-Adventure.sb3.json`. The archive SHA-256 is
`4d70968739e9aafe19660baed7eb12f153d58189760d37559eafaae1b6fe972c`;
the controller sidecar is checked in as
`examples/spider-adventure-xbox-controls.json`. Both passed full temporary and
final FTP readback. The directory now contains 21 games plus the three existing
Xbox/regression test projects; test fixtures do not count as games.

## Hardware checks

Tested on the 128MB Xbox using the diagnostics-off shared-pointer-help build at
`F:\scratch-pointer-help-20261027\default.xbe` (SHA-256
`98c93665e87f51ce9b503c876b0301155e07084922bb1588dcd777bbbfca807e`).
Normal game-list launch, D-pad movement and A jumping produced actual stomps,
combo scores, and automatic level transitions. Controller play reached Level 6,
Score 7,516, Best combo 6, then the authored GAME OVER screen. This is a gameplay
check, not a complete ten-level victory pass. Y restarted after Game Over;
left-stick movement and jumping worked in the new round. Back / Select opened
the pause menu with shared mouse help, and Return to game list reached the
normal populated browser. A confirmed second browser launch reached Level 1
again; Y reset the round and Back / Select paused it for handoff. One short KVM
A confirmation was missed during browser testing; a neutral interval followed
by a 700 ms press launched successfully. This remains consistent with the
existing KVM delivery limitation, not a demonstrated game script fault.

A 30-second KVM video and 15-second HDMI audio sample are retained under ignored
`build-xbox/game21/`. Audio contained a non-clipping signal (peak 0.09534,
14.99 seconds captured); subjective listening and longer stability remain open.
KVM video is a visual record, not a game frame-rate benchmark.

Original metadata, source JSON, asset cache, hashes, installation receipts and
recordings live under `build-xbox/game21/`. No downloaded game assets are added
to Git.
