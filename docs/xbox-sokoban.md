# Sokoban puzzle repairs

Gammastr20's [Sokoban](https://scratch.mit.edu/projects/24490009/) has passed
puzzles one through three on the Xbox. The downloaded tenth puzzle contains
a crate at zero-based `(12, 2)` with inaccessible cells immediately right and
below it. The player cannot stand on those cells to push left or up, and cannot
push right or down into them. This is an authored map problem, independent of
Xbox rendering or controller input.

Another crate at `(8, 4)` requires access to its left support cell `(7, 4)`.
That support cell is enclosed by inaccessible cells and the crate itself.

## Separate prepared copy

```sh
python3 scripts/prepare-sokoban.py ORIGINAL.sb2 PREPARED.sb2
python3 scripts/verify-sokoban-solution.py PREPARED.sb2 examples/sokoban-level10-solution.json
```

The default preparation accepts only the tested original archive and refuses an
existing output or replacement of its source. It opens three floor cells:

- `(12, 3)` and `(12, 4)` provide a downward escape for the corner crate.
- `(7, 5)` gives the player access to the other crate's left support cell.

Coordinates start at the upper-left corner. X increases right and Y increases
down. The repair retains the 15-by-8 dimensions, player start, all eleven
crates, all eleven goals, the other twelve puzzles, every script and all nine
asset files. Reverting these three digits restores the original project JSON
exactly. Repeated preparation produced byte-identical archives; wrong-source
and overwrite attempts were rejected.

Original SHA-256:
`6b2ea446a14651efe37bc6589172a05309371d1c8db1d9ce8a267848827e5013`.
Prepared SHA-256:
`efdbc0055c6c97f1c525e4e5dd5273066e88f043127fb1c81d5276196df97f64`.

## Independent solution check

A backward pull search generated the saved route. A separate forward replay
then checked ordinary walking and pushing, without pulling, against every
inaccessible cell and occupied destination. The route takes 698 moves and
171 pushes and fills all eleven goals. The checked-in read-only verifier
repeats that forward check directly from the prepared archive. On the original
archive, the same route fails at step three when Down tries to push the trapped
crate. A failed route alone would not establish impossibility; the original
corner geometry above establishes that crate cannot reach a goal.

Earlier candidate searches that exhausted their time/state limits are retained
as incomplete results. They are not proofs that those candidates are impossible.

## Runtime qualification

An isolated xemu test uses the normal diagnostics-off executable and a separate fixture with
an explicitly added delayed level-ten selection script. That script is absent
from the distributable prepared archive. This is a targeted puzzle test, not
a playthrough of the preceding nine puzzles.

Earlier failed debugger input harnesses are excluded from completion evidence.
The corrected input-poll bypass verified every player position and all 120 map
cells across 698 moves and 171 pushes, filling all eleven goals. The runtime
then advanced naturally to level eleven. After an earlier 78-move prefix,
the original R key restored the initial player position and every crate/map
cell; the cumulative move counter correctly remained 83, including five
preceding walks. No player positions, maps, scores or goals were written by
the debugger.

The backward-search route originally included thirteen unnecessary walks after
all goals were filled. The runtime correctly advanced during that tail, causing
the old assertion at step 699. The saved route now ends at first completion;
the independent verifier rejects trailing moves after completion. The original
assertion and all 698 preceding matched states remain in the evidence, alongside
the completed level-ten state and the level-eleven framebuffer capture.

## Physical Xbox qualification

The separate level-ten fixture passed on the 128MB Xbox using the normal
upstream-synchronized `e332255e` executable, with renderer/game/menu tracing
disabled. Only controller inputs were supplied. After twenty verified moves,
Black restored the original player position and every crate/map cell. A fresh
698-move route then matched every observed player position and all 120 cells,
filled all eleven goals, and advanced naturally to level eleven. The final
physical screen showed level 11 / moves 718 (20 before restart plus 698 after).
The full route took about 64 minutes. This is a targeted tenth-puzzle test,
not a playthrough of puzzles one through nine.

Start-hold pause and a short A confirmation returned to the populated browser.
After the controller dashboard reset, the prepared archive was installed as
`E:\ScratchEverywhere\Sokoban-Gammastr20.sb2`. Temporary upload, final archive
and original-backup readbacks all matched. The original is retained as
`sokoban-original-6b2ea446.fixture`; the existing controller profile is unchanged
(SHA-256 `7bf8c7b14210d9d1fc3ebeaf232f7265db7d0815e048f1de5b7e9d2d6d77dac3`).
The temporary level-ten project and profile were removed, restoring twenty
games plus XboxTest in the browser. The regular Games launcher remains the
preceding `2b8b5778` executable.

The installed prepared archive then passed ordinary browser selection,
puzzles one through three, Black restart and a short-confirmation Exit.
A fresh browser launch showed level one / moves zero; a crate push and Black
restart again matched the complete first-puzzle map and player position.
A repeated short-confirmation Exit returned to the populated browser.
Later puzzles, complete normal playthrough, and subjective audio remain open.

An eight-second music capture contained one full-scale stereo frame at index
zero, followed by normal levels (peak 0.06983); the raw file is retained.
A repeat eight-second capture had peak 0.04514 and no full-scale frames.
The initial capture-frame anomaly remains a shared audio-capture investigation,
not a claimed music or decoder failure. The earlier 120-second source-matched
loop check uses the same unchanged music asset.

Local preparation, solver, archive-comparison and runtime evidence is in ignored
`build-xbox/hardware/sokoban-*` and `build-xbox/xemu-sokoban-level10/`.

## Optional complete puzzle set — candidate

The default command and its `efdbc005…` archive remain unchanged. Add
`--all-puzzles` to prepare the additional authored-project repairs:

```sh
python3 scripts/prepare-sokoban.py --all-puzzles ORIGINAL.sb2 FULL.sb2
python3 scripts/verify-sokoban-solution.py FULL.sb2 examples/sokoban-all-puzzles-solutions.json
python3 tests/sokoban_all_puzzles_test.py ORIGINAL.sb2
```

This option still starts from the tested original `6b2ea446…` archive. It keeps
the puzzle-ten access repair and adds:

- **Completed-goal scan:** the authored loop increments its index before reading
  a tile. Starting at one skips the first cell and reads past the end. Starting
  at zero makes it visit cells one through N. Puzzles nine and twelve have a
  goal in that first cell: the previous loop counts nine of ten and three of
  four completed goals, respectively.
- **Puzzle twelve height:** its header declares nine rows of seven cells, while
  its data contains ten rows. Height ten draws every existing row. All seventy
  tiles, crates and goals are retained.
- **Puzzle thirteen start:** `(9, 7)` is an inaccessible tile. The player starts
  one cell up at `(9, 6)`, on existing floor. Its map, crates and goals are retained.

These are Scratch project adaptations, with no engine or Xbox-only code change.
The optional copy changes three puzzle records and one loop initializer; all
nine assets and every other project value are preserved. Reversing those four
edits restores the original parsed project. The candidate SHA-256 is
`8253ed9a8dc8106525d1121880549bfa24de969223f0a360e4cc331ec880d05b`.

The saved thirteen routes independently replay **2,728 moves / 628 pushes**.
The verifier checks complete, unique puzzle coverage, legal walking/pushing,
first completion and archive identity. Its existing single-puzzle command is
preserved. The regression check also interprets the actual finite goal-count
loop, verifies corrected counts on every solved map, checks asset/project
preservation and rejects overwrite and wrong-source attempts.

An ordinary level-one start in the private xemu guest completed **all thirteen
puzzles and the natural wrap to puzzle one**. A separate audit replayed all
**2,728 moves / 628 pushes**, comparing every recorded player position, map
cell, solved puzzle and natural transition with independent routes. This
includes puzzle nine and twelve recognition after filling their previously
skipped first-cell goals, and the corrected puzzle-thirteen start. A final
read-only check verified the live first-puzzle map and player with the
cumulative counter at 2,728; its original framebuffer shows Level 1 / Moves 2728
and independently matches all 25 tiles and the player.

Testing used the normal `ac3142d7…` Xbox executable from the runtime improvement
now merged in PR #33, with profiling off. GDB supplied keys before native
key-hat dispatch; project variables, maps, scores, RNG and positions were only
read. The same guest and verified prefix were retained across two bounded
debugger segments. Native input was restored before detaching. Debugger pacing
and private host audio output do not establish FPS or sound quality.

**An emulator visual issue remains open.** Pixel classification of the thirteen
initial framebuffers matched 793 of 796 cells and every player. Three samples
in the puzzle-ten image differed from its correct logical map. A separate
explicit delayed-puzzle-ten fixture on the same executable matched all 120
cells and the player in five captures, including a frozen repeat and later
native input polls. A second explicitly prepared pre-win-puzzle-nine fixture
used one ordinary Left move to advance naturally to ten; all six captured
maps/players matched (696 sampled cells). Both targeted probes use the same
executable and retain all assets. These clean results do not explain the earlier
mismatch or establish a visually clean full run. All original images are
preserved. The disposable guests and debuggers are closed.

### October 28 rendering follow-up

A fresh, unseeded repeat used the same candidate archive and normal executable.
The observer now waits for both level initialization and the authored drawing
flag to finish before settling and capturing. The first seven boards' sampled centers matched;
puzzle eight's initial image missed two floor cells (265 of 267 sampled cells
across eight boards matched). The repeat was stopped after **169 verified
moves**, at puzzle eight, to investigate this earlier reproduction. It did not
repeat the complete thirteen-puzzle run.

With input restored to neutral, a read-only debugger check matched the complete
logical map and player against the independent route. Initialization and drawing
were both complete. Two identical, settled framebuffer captures still disagreed
with four cells. A separate read-only dump of the pen render target contained
the same four wrong cells: three were transparent and one showed floor instead
of a goal. The defect therefore exists in the drawing surface before final
screen composition; the exact cause remains open.

An ordinary R restart produced a clean 72-cell board. A subsequent bounded
restart probe reproduced a missing floor tile on its second captured restart: 71 of 72
cells matched, with the logical map and player still correct. Extra tracing
changes timing, so a clean traced redraw does not establish a fix.

A fresh private guest then reproduced the problem with the same normal
executable and a separate fixture containing only one added script: select
puzzle eight after a one-second delay. All assets and the remaining project
were verified unchanged. Tile-center checks passed the first fourteen captured
restarts, then found two missing floor cells on capture fifteen. A stronger
comparison of all **174,936 board pixels**, against a visually reviewed clean
reference, also found smaller defects on captures six and fourteen. Center
samples alone therefore undercount the visual failures. The fixture SHA-256 is
`ef1678b2f5918608f37e6df23a6b8795c79d401f194bd254ae5bd394872c9650`.

A separate current-main experiment invalidated the GPU vertex buffer cache
before each geometry draw. The changed dependency source and compiled command
were verified; matching symbols supplied all debugger addresses. Its first
restart still had a correct logical map/player but 4,212 differing board pixels
and a missing floor sample. **That experiment was rejected and its source
change reverted.** It was neither merged nor installed on the Xbox. The short
reproduction makes further investigation possible without another multi-hour
playthrough; the actual rendering fix remains open.

These are private emulator findings, not physical controller, performance or
audio acceptance. Original images, logical states, direct pen-surface bytes,
compiled Xbox structure-layout offsets and input-restoration receipts are in
ignored `build-xbox/sokoban-visual-repeat-20261028/` in the primary checkout.
The physical Xbox's installed archive and executable were not changed.

**This candidate has not been installed or tested on the physical Xbox.** The
installed default prepared archive remains `efdbc005…`. A complete physical
playthrough, full-set visual acceptance and audio qualification remain open. Local source,
independent replay and completed runtime evidence are under ignored
`build-xbox/sokoban-full-20261027/` in the primary checkout; the separate visual
probe is under `build-xbox/sokoban-stamp-forensics-20261027/`.
