# Appel: controller menus and frame pacing

Appel v1.4 by griffpatch originally requires sprite clicks on its title and
level-selection screens. `examples/appel-xbox-controls.json` maps A to Space,
which jumps during gameplay but did not activate those menus.

## Prepared controller copy

```sh
python3 scripts/prepare-appel.py original-Appel.sb3 Appel-controller.sb3
python3 tests/appel_controller_menu_test.py original-Appel.sb3
```

The preparer refuses an existing destination or an already prepared project.
It reuses the authored menu click actions, including sound, score loading,
level setup and state transitions. A/Space activates on release so one held
press cannot enter the level picker and immediately start its selected level.
Gameplay sprites, scripts and all assets are preserved.

- Title: D-pad Up/Down chooses Play, Editor or Audio. A activates the highlighted
  item; Play is selected initially.
- Level picker: D-pad Left/Right changes the level; A activates Select.
  B returns to the title.
- Gameplay: D-pad/left stick moves; A jumps. Back/Select opens the runtime menu.
- The original pointer controls remain available.

The installed original archive is backed up on Xbox as
`E:\ScratchEverywhere\Appel-before-controller-menus.fixture`. The prepared
copy uses the existing `Appel-griffpatch.sb3` name and adjacent controller
profile. Transfers are checked by full FTP readback.

## Measuring performance

Build with `-DSE_XBOX_PROFILE_FRAMES=ON` to log integer frame timings every
120 rendered frames. Reports include mean, median, 95th percentile and maximum
frame period, plus accumulated input, script, render and event-polling costs.
Script time includes scheduler passes between rendered frames. The same option
can also report per-sprite and native-operation costs when
`-DSE_XBOX_PROFILE_THREADS=ON` is enabled. Detailed dispatch measurements overlap
with their parent script time and must not be added to it.
Turn both profiling options off for the final playing build.

Use a continuous KVM stream and bounded controller phases. The KVM capture
rate is below the game's frame rate, so video alone is not an FPS benchmark.
Keep the workload and project constant when comparing binaries, and exclude
startup/level-loading windows from steady-play comparisons. A frame-rate
setting change is not a substitute for reducing execution cost: Appel's
frame-based physics must retain its authored speed.

October 27 baseline: stable windows were approximately 15 FPS (66.7 ms median),
with 86–87 ms 95th-percentile periods and occasional roughly 250 ms frames.
Expanded timing measured about 42 ms of scripts and 21–23 ms of rendering per
rendered frame, with under 1 ms of event polling. The largest script costs were
Player (~19 ms), Wallpaper Tiles (~5 ms), Background (~5 ms), and Foreground
(~5 ms). Correcting the stale executor source optimization glob alone did not
materially improve the result.

Local recordings, exact deployed XBE hashes, controller receipts and retrieved
logs live under ignored `build-xbox/hardware/appel-*`. In particular,
`appel-profile-baseline2.log`, `appel-profile-fulltiming.log`, and
`appel-profile-threads.log` retain the baseline measurements.

The numeric-string cache reduced tile-script costs but did not remove the
15 FPS limit. Listener indexing subsequently reduced Player from ~19 ms to
~5–6 ms and raised the instrumented gameplay result to ~19 FPS. Native timing
then identified redundant costume assignments as the next largest cost.

Long-tail frame periods in diagnostic builds include periodic log-writing
stalls. These must be distinguished from normal-build gameplay; keep final
recordings with profiling disabled and do not present diagnostic maximums as
an unqualified production result.

## Runtime changes

- Cache numeric conversions in interned strings, and avoid formatting numbers
  during numeric/string equality checks. Reused pool slots invalidate cached
  numeric state.
- Index broadcast listeners once per original sprite. Clones use that index
  but still receive independent threads. This preserves every matching hat and
  its original iteration order while avoiding repeated name copying/lowercasing.
- Skip redundant Xbox costume loads only when the loaded costume index,
  requested scale, cached image dimensions and SVG crop offsets still agree.
  Size/viewport changes, eviction and geometry changes take the load path;
  failed resize attempts leave the stamp invalid so they can retry.
- Compile addition, subtraction, multiplication, division, and boolean logic to
  direct typed VM operations. Inputs retain the existing numeric/boolean
  conversions and evaluation order. Bytecode cache version 2 forces old caches
  to rebuild from project sources; an older player may reject the new cache.

The lightweight timing report now accounts for diagnostic report-writing time
separately (`previous_report_us`) and excludes that work from the next sampled
frame interval. Startup/level transitions must still be excluded from steady
comparisons. Detailed per-thread/native tracing remains opt-in.

Targeted checks:

```sh
python3 tests/appel_controller_menu_test.py original-Appel.sb3
python3 tests/broadcast_index_test.py
python3 tests/value_numeric_cache_test.py
python3 tests/xbox_costume_cache_test.py
python3 tests/bytecode_typed_arithmetic_test.py
python3 tests/xbox_frame_profile_test.py
```

The numeric-cache check uses the locally fetched Catalog headers and Ryu source
under `build-xbox/.cache/catalog`; build Xbox once before running it. Native
runtime checks compile with AddressSanitizer and UndefinedBehaviorSanitizer.

Further isolation: music-disabled gameplay still showed ~25 FPS and recurring
~215–230 ms stalls, so music was not the main recurring hitch. The remaining
cache defect was that `flushCostumeImages` decremented an image's lifetime on
inactive frames without resetting it when that image became active again.
Cycling HUD digits could therefore expire despite repeated use. Cache hits and
active images now refresh their lifetime; only consecutive inactivity ages them
out. `tests/costume_cache_lifetime_test.py` cycles ten digits for 300 frames
against a 30-frame timeout, then verifies actual inactive eviction and mask
invalidation. This also retains the existing immediate memory-pressure cleanup.

## October 27 hardware result

Representative steady-play windows in the first section of Level 1, with music
on and the same project/rules:

| Build stage | Mean rendered FPS | Typical frame period | Typical window p95 |
| --- | ---: | ---: | ---: |
| Baseline | 15.00 | 66.66 ms | 86.38 ms |
| Broadcast index (detailed tracing) | 18.56 | 49.98 ms | 69.54 ms |
| Redundant-costume fast path | 21.58 | 33.39 ms | 68.89 ms |
| Direct arithmetic/logic | 23.40 | 33.39 ms | 67.74 ms |
| Inactivity-based image lifetime | **29.67** | **33.35 ms** | **34.66 ms** |

The final row spans eight 120-frame windows (960 frames). The period and p95
columns are medians of the per-window statistics, not pooled percentiles.
`appel-frame-comparison.json` stores the selected raw windows. Startup, menu and
level-loading samples are excluded; this is not a whole-game worst-case or
all-level performance certification. The recurring ~230 ms stalls disappeared
from the final steady windows; isolated longer frames remain visible elsewhere
in the full log and must not be described as zero stutter.

The measured final diagnostic XBE has SHA-256
`db8388e51edcc64eb78bfd5da797043d931d03fa26b6ef2e8fe997bfd23a70f8`.
It uses `SE_XBOX_PROFILE_FRAMES=ON`, `SE_XBOX_PROFILE_THREADS=OFF`. The playing
build is rebuilt with both options OFF. No audio file resampling, music muting,
physics changes or increased game frame-rate setting is used by the final fix.

Final normal-build deployment:
`F:\scratch-appel-smooth-20261027\default.xbe`, SHA-256
`7bb956b4337ef657b13ca637d27aa84181072434a2d1814c29c59df8b275a3ed`.
Both profiling options are OFF and FTP readback matches the local XBE.

Normal-build smoke check: 2048 launched, A started it, Up/Left/Down changed the
board and reached Score 12, and Back/Select opened the runtime pause menu.
Return to game list worked. Appel then launched from that list; A opened its
level picker and A selected Level 1 without pointer controls. The console was
left in Appel with controller reports neutral and KVM input ownership released.

## Normal-build route qualification — October 27

Extended controller play on the physical 128MB Xbox used the later shared-help
normal build, `F:\scratch-pointer-help-20261027\default.xbe`, SHA-256
`98c93665e87f51ce9b503c876b0301155e07084922bb1588dcd777bbbfca807e`.
Both profiling options are OFF. The prepared controller-menu archive is
`69a2a2767d85620b09ccfa228e7ec62cc7896db10725bd23a03af0a41ceb16ad`;
its gameplay scripts and assets are preserved. Existing full FTP readback
receipts identify these artifacts; no new readback was possible during play.
This run used HDMI images and Player Two controller reports, with no debugger,
live game-variable reads or game-state writes.

Verified progress:

- Entered Level 1 through the controller menus and activated checkpoints one
  and two. Repeated jumps landed on both moving blue platforms and the roof.
- Entered the authored hidden passage, collected its apples and reached
  **14/35**. Releasing jump, moving left and then jumping restored the visible
  player; subsequent jumps climbed the staircase back onto the roof.
- Cleared the upper-ledge enemy with two short follow-up A presses, crossed the
  lower spikes and activated **checkpoint three at 16/35**. The next higher
  platform and lower passage brought the count to **18/35**. Further platform
  jumps reached **19/35**, repeated on another attempt.
- Enemy/spike collisions showed the breakup animation and returned to
  checkpoint two with fourteen apples retained. Later deaths returned to
  checkpoint three with all nineteen apples retained on the later attempts.
- Back/Select opened runtime pause and B resumed repeatedly.
- The ground route beneath the later platforms and a jump over its enemy
  reached the final structure. Down+Right crouched through its low opening;
  jumping into the bonus alcove and moving left collected both apples,
  reaching **21/35**. Crouching back through the opening also worked. The
  subsequent backtrack died beside the spiked wall; checkpoint three restored
  the player with all twenty-one apples retained. This was not a finish.
- Direct TV listening confirmed clean music without crackles or dropouts in
  this normal-build session. The KVM recordings still contain transport gaps.

The transparent player outline inside the green ledge is the game's hidden
tunnel, not evidence of death or missing terrain. Holding jump there can keep
the player against its ceiling; see the earlier [tunnel investigation](xbox-game-qualification.md#checkpoint-three-and-lower-route--october-26-evening).

Local evidence is under ignored `build-xbox/hardware/`: the
`appel-normal98-lift1-gated1`, `lift2-gated2` and `roof-gated1` recordings;
`appel-normal98-tunnel-follow8`, `tunnel-exit8`, `tunnel-exit9`,
`tunnel-escape10`, `stairs-climb12` and `roof-return13`; and
`appel-normal98-recovery21` / `checkpoint-final23`. The later enemy crossing,
checkpoint and recovery recordings are `appel-normal98-upper-cross24`,
`spike-drop25`, `checkpoint3-jump26`, `high-platform28`, `lower-advance30`
and `cp3-death-recovery37`. Nineteen-apple landings are retained in
`edge-gap56`, `raised-route65` and `edge-jump70`; `upper-recover72` shows
checkpoint-three recovery with nineteen apples. Each full directory name
uses the `appel-normal98-` prefix and retains original JPEGs, timestamps,
hashes and executed controller/observer sources.

The ground route, enemy clearance, crouch passage, bonus apples and return are
recorded in `appel-normal98-ground-advance85`, `ground-route86`,
`ground-enemy87`, `crouch-opening88`, `crouch-through89`, `notch-step90`,
`notch-apple91` and `notch-return92`. The failed backtrack is `backtrack93`.
Checkpoint recovery is `recover21-94`. These names also use the
`appel-normal98-` prefix. The local
`appel-normal98-crouch-bonus-verification.json` records the evidence inventory
and JPEG hash checks; image review establishes the gameplay results.

The later platform gaps and route to the finish remain unfinished. Failed jumps
and falls are retained. **Normal-build Level 1 completion and victory replay
remain open**, along with longer audio continuity verification. The direct TV
listening result is saved in `appel-normal98-tv-listening-confirmation.json`;
it applies to this Appel session. The earlier diagnostic Level 1
win is a separate result. These recordings do not extend the frame-rate
benchmark or establish retail 64MB support. See the [capture transport limits](xbox-audio-resampling.md#capture-transport-limits--october-27)
before interpreting long network-audio recordings as playback continuity.

## Movement smoothness follow-up — candidate, October 27

Direct TV feedback during normal play described movement/scrolling as less
smooth, rather than the whole scene freezing. The earlier first-section result
of about 30 rendered FPS does not establish fluid movement throughout the level.

A new **shared-runtime candidate** removes two sources of repeated work:

- List indexing checks string-only keywords through borrowed interned text.
  Numeric terrain/collision indices no longer make a number → string → number
  round trip. Reads, replacements, deletions and insertions retain the existing
  conversions, bounds and random-index behavior.
- Input/timer/broadcast hat lookups reuse their opcode strings. Missing hats
  are looked up without inserting empty entries into every sprite/clone.
  Matching listeners, their ordering, key-repeat and pause behavior are retained.

The actual VM cases pass differential checks against the previous behavior,
including empty/missing lists, fractional and nonfinite indices, keyword case,
booleans/colors, random-call counts, stack state and the 200,000-item limit.
Actual dispatch functions pass key-repeat/pause/timer/clone-listener checks.
Both new checks use AddressSanitizer and UndefinedBehaviorSanitizer:

```sh
python3 tests/bytecode_list_index_test.py
python3 tests/hat_dispatch_allocation_test.py
```

A host-only empty-scene test with 400 sprites and 100 input/timer/broadcast
polls counted 80,100 allocations in the previous code and zero after warm-up in
the candidate; absent hat maps also remain empty. A host-only numeric lookup
microbenchmark removed 1,000,000 number-formatting calls per trial. These are
work-count/microbenchmark results, **not Xbox FPS or whole-game speedups**.
The numeric-cache, typed arithmetic and broadcast-index regression checks pass,
and the normal NXDK Release build succeeds with profiling disabled. The candidate
also boots Appel to its title screen in an isolated xemu guest, using the
installed prepared project JSON and nonaudio assets. Audio assets were omitted
only in that guest fixture because its BIOS exposes 64MB; this is a startup
correctness check, not a hardware performance or audio result.

The candidate preserves Appel's project, authored update rate, physics and
audio. The physical comparison below shows an opening-area improvement.
**Subjective movement confirmation and broader-level frame pacing remain open;
this candidate is not a complete smoothness fix.**

### Candidate gameplay regression in xemu

The normal candidate (`ac3142d7…`, profiling OFF) passed a further private-guest
check with the installed prepared project JSON and nonaudio assets. Diagnostic
keys went through the native input and key-hat functions; no project variables,
positions, maps or scores were written. Space press/release entered the level
through its prepared menus. Right entered normal play, movement and jumping
worked, and releasing jump returned the player to the ground with zero vertical
velocity. The first apple registered.

Holding Right against the first raised ledge kept the player at the same wall
position across both observations. Right+Space then cleared it, collected the
second apple and landed on top with zero vertical velocity. Original framebuffer
images and read-only state snapshots support these results; the input vector was
restored before detaching and the private guest was closed.

This covers 108 diagnostic input polls through the menus and 186 in the movement
sequence. Debugger input changes pacing: these counts are **not FPS or physical
controller evidence**. Audio was omitted only in the guest fixture; this adds no
audio, full-level-completion or hardware-smoothness result. Local evidence is
`build-xbox/appel-movement-smoothness/emulator-gameplay-verification.json` and
its referenced original images, snapshots and executed input-probe source.

### Physical movement comparison, October 27

On the 128MB Xbox, the matched diagnostic builds used identical frame profiling
with thread profiling OFF. Both loaded the unchanged installed controller-menu
v3 project (`117188ba…`), with all music/assets present. The saved v2 identity
was stale; a full FTP readback identified v3 before installation. Its differences
from v2 are confined to the prepared menus and their controller-mode variable.

Both controlled runs began at the same first wall with one apple. Eight
Left 1.5-second / Right 2-second cycles stayed in that opening area and ended at
the same wall. Only normal controller reports were sent; no game state was
read or written through a debugger. No video connection ran during either
28-second action.

| Controlled movement metric | Main baseline | Candidate |
| --- | ---: | ---: |
| Complete 120-frame windows | 4 (480 frames) | 6 (720 frames) |
| Rendered FPS | 24.48 | 27.65 |
| Mean frame period | 40.85 ms | 36.16 ms |
| Median of window p95 periods | 68.68 ms | 52.70 ms |
| Longest observed frame in selected windows | 185.76 ms | 166.71 ms |
| Mean input/hat phase per rendered frame | 2.55 ms | 1.17 ms |
| Mean script phase per rendered frame | 17.78 ms | 16.53 ms |

The selection includes **every complete reporting window fully inside each
action**, excluding partial windows at either edge. Percentiles are reported
per 120-frame window, then their median is shown; these are not pooled frame
percentiles. Diagnostic reporting overhead is recorded separately and excluded
by the profiler. An earlier replay reached different apple counts/positions and
is explicitly excluded from this comparison.

This is about 13% more rendered frames per second in one short movement test,
with fewer slow frames. The remaining long frames and roughly 53 ms window p95
mean **it still does not establish consistently smooth movement, 60 FPS, Mac
equivalence or whole-level performance**. Several separate event-poll stalls
also occurred during exploratory navigation; they need further isolation.

Full upload/readback verification covered separate baseline (`0071466a…`),
candidate (`8cfba7fa…`) and normal (`ac3142d7…`) executables. The primary dashboard
launcher (`b75e9beb…`) and installed Appel file were preserved. The normal
candidate is installed separately at
`F:\scratch-appel-motion-20261027\default.xbe`, with profiling and UDP diagnostics
OFF. TV movement acceptance is still pending.

Local raw evidence and the reproducible selection script are under
`build-xbox/appel-movement-smoothness/`: `hardware-comparison-results.json`,
`analyze-comparison.py`, both referenced UDP logs/controller receipts, start/end
JPEGs, the full Xbox runtime logs and `hardware-comparison-install.json`.
