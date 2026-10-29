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
list redraws the browser. These Catch checks exercise ordinary SVG drawing; broader artwork and sampling
quality still need review beyond the solid-color checks below.
Both comparison guests report the standard-memory policy despite the emulator's
128MB configuration: the backdrop raster is 334×249 in a 16-bit texture. This
neither qualifies a retail 64MB Xbox nor proves title-visible expanded RAM.

Native brightness now adds a signed RGB offset and clamps before transparency,
in one draw pass. It retains the shared 96-step hue cache. Pen compositing uses
its stored premultiplied color without applying transparency a second time.

The compiled brightness candidate `ab2481f2...` passes **107/107** independent
samples in the unchanged [color/pen fixture](../examples/make-color-effects-test.py)
(maximum channel error 7, tolerance 9), with PASSES=5 / ERRORS=0 / CYCLES=40.
The preceding builds passed 98/107, with identical colors before and after the
SVG fix, establishing that these errors predated that change.

The new [brightness draw-path fixture](../examples/make-nv2a-brightness-test.py)
also passes **60/60** solid-center checks with standard memory policy and again
with an explicit expanded-renderer-policy override (maximum errors 9 and 2).
A bounded read-only trace confirms mosaic wrap/grid, pixelate and deformed paths;
the expanded-policy run additionally executes tiled stage/bitmap draws, including
brightness -50, +50, -100 and +100. The standard-policy guest downsizes the large
bitmap, so it does not establish tiled coverage. The override changes only the
disposable guest's renderer policy; it does not validate RAM detection or physical
128MB hardware. Back / Return to game list redraws the menu/browser without a
brightness tint afterwards. Physical rendering, pen/sensing and audio acceptance
remain open.

The native backend now implements the fork's original-color restoration and
pen-query hooks. Color sensing decodes the authored asset when CPU pixels have
been freed, preserving the existing texture dimensions and GPU resources. Pen
queries synchronize queued strokes/stamps and cache only the queried rectangle;
drawing, clearing and cleanup invalidate that cache.

The compiled sensing candidate `2dd1b385...` improves the unchanged
[38-case regression](../examples/make-color-sensing-test.py) from **19 passes /
19 errors** to **38 passes / 0 errors**. The same scripts/assets also pass with
only the ordinary `hq=true` project comment added; GDB verifies a 640×480 pen
canvas at scale 4/3. A frame-paced Start press reaches the actual Green Flag
handler and the following result is again 38/0; both pen modes return cleanly to
the browser. The latest binary retains **107/107** color-effect samples and
PASSES=5 / ERRORS=0 / CYCLES=40. These are emulator checks; physical pen/collision
acceptance and game-specific behavior still need testing.

An ordinary native USB-controller [Breakout run](xbox-breakout-controller.md)
now clears the final prepared archive at Score 1920 with three lives. Three
captures contain no remaining brick colors, and the score stays fixed across
960 additional video frames while the ball crosses the empty field. Natural
Game Over, menu Green Flag replay to observed Score 0 / three lives / restored
bricks, renewed steering and a separately verified fresh-launch browser exit
also pass. These use the frozen sensing candidate and a read-only observer;
physical full-board and normal-browser selection of that final archive remain
open.

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

## Appel SVG growth and complete-project checks

Appel's animated menu exposed a separate Xbox image-cache defect: AUDIO ON and
EDITOR were first rasterized at 20x5 pixels (scale 0.133), then stretched after
the animation reached full size. Xbox frees parsed SVG trees after rasterizing,
so the existing resize path silently skipped growth. Images now retain their
source location and reload the original SVG when a larger raster is requested.
Parsed trees are still released; temporary decode failures retain the previous
pixels/geometry, and failed texture uploads remain retryable.

The complete controller-menu v3 archive (`117188ba...`) retains all 460 original
assets, including 45 audio files. Native candidate `0f04b4ec...` displays readable
title and level-picker labels; the corresponding cached buttons are 216x57,
with no retained SVG document. Actual emulated USB inputs enter Level One, move
both ways, jump, collect four apples and activate the first checkpoint. A spike
collision shows the authored death particles and respawns at that checkpoint;
read-only observation confirms PLAY, four apples and a nonzero spawn index.
Green Flag from the console menu returns to the readable title; a subsequent
Back / Return to game list redraws the populated browser.

A ten-second APU capture has no clipped samples or fully silent 256-sample
blocks. Aligning it with the original music asset gives 0.999990 correlation.
This checks emulated output, not physical TV sound, all game sounds or performance.
The NXDK build and existing costume-cache, cache-lifetime, Scratch 2 text and
real SVG bounds/pixels checks pass. Thin terrain seams, a full Level One clear,
physical smoothness and the remaining game/hardware gates are still open.

Before merging: verify the native backend and the intended saved renderer choice
on the Xbox, repeat launcher/game/replay/exit and reset tests, check audio and
texture/pen behavior, and continue every open gate in the
[21-game qualification matrix](xbox-game-qualification.md).
