# Jumper on Xbox

[Jumper by Depicklator](https://scratch.mit.edu/projects/103069687/) has prior
physical-Xbox checks through levels 1–4, with level 5 rendered, lava death and
respawn, Black level restart, Y+Black full restart, Green Flag replay and browser
return. The controller-ready prepared copy maps A to Play/Up and preserves the
original gameplay and assets; see `scripts/prepare-jumper.py`.

## Native emulator progress — October 31, 2026

Normal main XBE `eb3492c2…`, native NV2A graphics and a 128 MB snapshot guest
clear **courses 1–19 and reach the final stage, course 20**. This is ordinary
controller play guided by read-only observations. It covers jumps, wall jumps,
magenta boosts, water ascent/descent, narrow passages, platform landings and
natural lava deaths/respawns. The only debugger write selects the native
renderer before loading the project. No position, level, collision or velocity
state is written, and no saved gameplay state is loaded.

The final stage's opening two ledges and lower underpass/floor-lava running jump
also pass. Its next narrow lava gap remains unfinished. **Victory, the stopped
timer and post-victory replay are unverified.** There are twenty playable courses;
the twenty-first platform costume is the authored “You Win!!!” scene.

Failed routes remain in the evidence. A short jump request missed once; a longer
A press is confirmed in both the emulator input state and subsequent movement.
Backing up, wall jumping and adding a running start cleared later obstacles.
No game or engine repair was needed for this progress. Some early death
verifiers also mistook the authored next-level position reset for a death before
the level handler completed; no exact total death count is claimed.

The shared emulator disk initially contained the original Jumper archive and
profile. A private disk copy was updated from the physical-console backups,
with old-hash guards and full FTP readback:

| Fixture | SHA-256 |
| --- | --- |
| Installed prepared Jumper archive | `48f4577fa315e8f915c7713f36dfa0dab859b16f987871f6cc3fd57ef351a62e` |
| Installed controller profile | `454f1e88c619982febbd146a10301255c2ef7f2833758a3b1124474b44c7aa5a` |

Provisioning used a separate maintenance guest, which was closed before the
normal snapshot run. The shared disk and private gameplay base retain their
before-run hashes. This fixture correction changes neither the physical console
nor game code. Other projects' extended results retain their documented fixtures.

Private evidence: ignored `build-xbox/jumper-native-fullrun-20261031/`, especially
`fixture-install-receipt.json`, `review-progress.json`, controller/QMP histories,
original screenshots and failed-route reviews.

## Still needed

- Complete the final stage and verify the visible win, timer stop and replay.
- Repeat later-course gameplay on the physical Xbox. Emulator frame budgets are
  not Xbox FPS, smoothness, audio or retail 64 MB qualification.
- Repeat the historical second-Exit handoff on current native hardware; prior
  readiness-guard checks pass quick A start and two exits in the emulator.
- Verify subjective/long-run audio and the separate
  [numeric monitor repair](xbox-monitor-number-formatting.md) on hardware.
