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
