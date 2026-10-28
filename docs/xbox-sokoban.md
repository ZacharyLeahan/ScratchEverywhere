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

An ordinary level-one start in the private xemu guest has passed puzzles one
through seven, comparing every player position and map cell with the independent
routes. Testing uses the normal `ac3142d7…` Xbox executable from the Appel
optimization candidate, with profiling off. GDB supplies keys before native
key-hat dispatch; project variables, maps, scores and positions are only read.
The full thirteen-puzzle run and natural wrap back to puzzle one remain pending.
Debugger pacing and private host audio output do not establish FPS or sound quality.

**This candidate has not been installed or tested on the physical Xbox.** The
installed default prepared archive remains `efdbc005…`. Later hardware play,
complete normal playthrough and audio qualification remain open. Local source,
independent replay and ongoing runtime evidence are under ignored
`build-xbox/sokoban-full-20261027/` in the primary checkout.
