# Upstream Xbox integration

This branch merges upstream through
[`ec2400eb`](https://github.com/ScratchEverywhere/ScratchEverywhere/commit/ec2400ebca42b7060795ff2c3d426c63a0c89687),
including [PR 816](https://github.com/ScratchEverywhere/ScratchEverywhere/pull/816):
the native NV2A renderer/window, dedicated Xbox audio, and runtime/memory improvements.
The subsequent Halloween menu assets are included too. It is a candidate for
the fork; hardware qualification is still pending.

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
emulator checks, not physical Xbox acceptance or an all-games pass. A separately
verified Catch run steers both ways with the left stick, reaches Score 12 /
Timer 0, restarts on short Start at Score 0 / Timer 29, and returns to the browser.
The earlier incorrectly selected Breakout run is retained separately and does
not supply this Catch evidence. Audio remains an open check.

A controlled Catch Game Over comparison isolates rough SVG lettering to nearest
magnification. Switching only the native backdrop sampler to linear smooths the
text; restoring it reproduces the original frame exactly (zero differing pixels),
with identical uploaded texture bytes. Native SVG drawing now uses linear
sampling across normal, tiled, mosaic, deformed and nine-slice paths. Bitmap
textures retain their selected filtering; explicit pixelate effects use nearest.

The compiled sampler candidate `c94ba467...` reaches the original Catch archive's
natural ending at Score 11 / Timer 0. Its 175,500-pixel lettering crop matches the
controlled linear result exactly; the backdrop texture hash is unchanged. A
read-only trace observes 32 recognized SVG binds, all linear. Short Start replays
at Score 0 / Timer 29, the left stick steers both ways, and Back / Return to game
list redraws the browser. These checks exercise ordinary SVG drawing; tiled,
mesh, pixelate and bitmap visual acceptance still need their own runtime checks.
Both comparison guests report the standard-memory policy despite the emulator's
128MB configuration: the backdrop raster is 334×249 in a 16-bit texture. This
neither qualifies a retail 64MB Xbox nor proves title-visible expanded RAM.

The existing color/pen fixture reaches PASSES=5 / ERRORS=0 / CYCLES=40,
but only 98 of 107 expected image samples pass. The frozen pre-SVG build has
the same values at all 107 samples: these brightness/hue/pen mismatches predate
the SVG fix. Native rendering is not fully qualified.

Pen compositing now avoids multiplying stored alpha a second time. In a paired
fixture with hue and brightness disabled only on the two pen stamps, the
half-transparent red stamp improves from RGB (71,16,25) to (135,16,25), versus
expected (136,16,24); the opaque stamp and all other 106 samples are unchanged.
The full original fixture still passes 98/107: its brightened translucent stamp
improves substantially but remains outside tolerance, alongside eight other
brightness/hue samples. These remain open, as do physical pen/audio checks.

The final post-theme XBE `f79fcd52...` also reaches the native launcher twice,
once after the controller reboot. A 90-video-frame reset hold does not reboot;
release cancels it, and a fresh full hold reaches `XReboot` after 122 frames.
The app starts again and the native launcher redraws correctly. This emulator's
inserted DVD launches the app again; it does not establish physical dashboard
recovery or recovery from a blocked game loop. Inputs were neutral afterwards.

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
