# Native Xbox Back taps across slow frames

A short Back tap can arrive and be released entirely between a game's input
polls. The native controller previously kept only the latest USB report, so
the game saw neutral and never opened the console menu. This is separate from
the physical KVM adapters disconnecting.

## Reproduction and fix

On frozen native `807d1928...`, the normal Space Invaders → Mario browser transition
reproduces the miss. Read-only execution hooks record Back in the cached USB
report at video frame 4507 and neutral at 4518. No game input poll runs during
the 12-frame tap; the next poll at 4528 reads neutral. The prior Back-edge flag
is zero, ruling out a stale held flag in this reproduction. A clean first Mario
launch accepts the same tap, so the miss depends on timing.

Each valid controller now retains a rising Back edge until the main input poll
consumes it alongside the live report under the existing DPC-level snapshot.
Release does not erase the pending request; disconnect, invalidation and
reconnection clear it. Only reserved Back is retained. Gameplay buttons and
menu confirmation remain live snapshots, and reset-hold timing is unchanged.

## Validation

- Targeted ASan/UBSan checks cover complete taps between polls, one-shot
  consumption, repeated held reports, another player's activity, disconnect,
  reconnect, malformed packets, unchanged gameplay snapshots and reset holds.
- The normal NXDK 480p build with debug symbols succeeds; profiling and runtime
  trace options remain off. Candidate XBE SHA-256 is
  `4ef49719b046338800c97e9858a4721ff8460039c8c85f2b87cba65a7d2ee1f5`.
- The unchanged full prepared Mario archive `7efb9b52...` passes a clean intro
  tap and three Space Invaders → Mario transition probes in private 128 MB
  Vulkan xemu, through actual emulated USB controls on renderer/window 3/0.
  In the second transition, the tap ends before any input poll; frame 7073
  reads neutral with Back pending, consumes the request, and the
  runtime pause check opens the menu at 7096.
- The third helper initially reports no pause after its 36-neutral-frame budget.
  Its trace nevertheless shows the pending request consumed after release.
  Another 60 neutral frames opens pause without another button press. That raw
  early result is retained: the fix preserves a tap, but a slow render can
  still delay the end-of-frame pause check. It cannot recover a permanently
  stuck game thread and supplies no frame-rate or smoothness acceptance.
- Back resumes and reopens the game menu; neutral input leaves it paused.
  Held-A Exit returns to all 21 games/42 buttons with zero game sprites.
  A fresh 2048 launch, short Back and another held-A Exit also pass.
- A short reset hold does not reboot; release cancels it. A fresh full
  Start+Back+both-triggers hold reaches actual `XReboot` after 121 video frames
  and then fresh application `main`. This verifies that path in the emulator,
  not physical dashboard or frozen-thread recovery.

Ignored receipts, original captures and read-only hook logs are under
`build-xbox/native-mario-early-back-20261029/`; fixed results are in
`fix/review.json`. Both guests close, and the saved shared HDD and normal Mario
archive remain unchanged. The fix is not installed on the Xbox. Physical taps,
controller handoff, audio, pacing and retail 64 MB qualification remain open.
