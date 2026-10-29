# Upstream Xbox integration

This branch merges upstream through
[`1f6365b7`](https://github.com/ScratchEverywhere/ScratchEverywhere/commit/1f6365b71caeb38fc8cb4cf8f0e67ae7f1fbecfe),
including [PR 816](https://github.com/ScratchEverywhere/ScratchEverywhere/pull/816):
the native NV2A renderer/window, dedicated Xbox audio, and runtime/memory improvements.
It is a candidate for the fork; hardware qualification is still pending.

## Fork behavior retained

- Back opens the console menu; games keep their Start bindings. A short Start
  press replays a stopped project.
- Return to the game list, release-before-confirmation, pointer help, and the
  Exit / System menu remain available.
- The native input backend accepts all four controllers. A new button/direction
  can take control; another pad's neutral, drift, or repeated held reports do not
  steal it back. Disconnects, read errors and malformed reports release its state.
- Start + Back + both triggers for two seconds requests the configured Xbox
  reboot. The menu/game loop must still be responsive to process this shortcut.
- Authored Xbox project lists remain intact, including large terrain maps.
  Existing costume bookkeeping and frame/thread profiling remain enabled by
  their respective options.
- The legacy SDL renderer retains the reviewed GPU texture-retirement fix from
  [PR 42](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/pull/42).
  Native NV2A has its own retirement mechanism and needs its own visual tests.

Native report snapshots use NXDK's DPC-level synchronization, following its SDL
joystick driver. Reports must contain all 20 bytes before any axes are read.
The new controller regression test covers handoff, drift, hotplug, short reports,
axis signs, reset cancellation, separate-pad chords, and tick-count wraparound.

## Validation and limits

The normal and debug-symbol NXDK builds succeed at 480p with expanded RAM enabled.
Affected host checks pass for list indices/VM stacks, typed arithmetic, Value
conversion/cache reuse, hats/broadcasts, costume cache/lifetime, Scratch 2 SVG
bounds/text, bitmap layers, color transforms, audio resampling, Xbox clocks,
variable tracing, native controllers, and frame/profile build definitions.

A private emulator test uses
[xemu-macos v0.16.4](https://github.com/MichaelJSr/xemu-macos/releases/tag/v0.16.4),
with the release archive checked against GitHub's asset SHA-256. GDB confirms
NV2A renderer/window IDs 3/0; all four emulated USB controller ports move the
launcher selection. Catch Apples launches, Back opens the console menu, and
Return to game list completes without launching another project. These are
emulator checks, not physical Xbox acceptance or an all-games pass.

The installed stock Mac xemu cannot provide Vulkan and falls back to OpenGL.
Its earlier startup used the legacy Xbox renderer (IDs 4/1), so it does not count
as native NV2A evidence. The private Vulkan test explicitly selects NV2A,
equivalent to the app's `--nv2a` option. Existing saved renderer preferences are
respected; installing a build alone does not change a saved `Xbox` preference.

The copied emulator disk has not been audited against the current physical
installation. Catch's initial D-pad probe leaves its basket stationary, consistent
with the older missing-sidecar case documented in [Catch Apples](xbox-catch-apples.md).
Do not count that probe as steering acceptance or assume its archives/profiles
match the final Xbox copies.

Original evidence is ignored under `build-xbox/upstream-nv2a-20261029/` in the
primary checkout. No physical XBE, game archive, controller firmware, or KVM
settings were changed by this integration. The separate frozen Sokoban replay
continues against its original binary and full-set prepared archive.

Before merging: verify the native backend and the intended saved renderer choice
on the Xbox, repeat launcher/game/replay/exit and reset tests, check audio and
texture/pen behavior, and continue every open gate in the
[21-game qualification matrix](xbox-game-qualification.md).
