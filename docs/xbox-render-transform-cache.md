# Xbox sprite transform cache — candidate

The Xbox transform calculation invalidated rotation after computing size, then
invalidated size after computing rotation. Even an unchanged sprite therefore
repeated both calculations on its next render. A probe of the pre-change
function counted 1,000 angle conversions across 1,000 unchanged calls.

This candidate separates size, rotation and position invalidation. It tracks
rotation style, image dimensions and rotation center, bitmap resolution/quality,
SVG selection, viewport/project dimensions, render mode and global scale.
Same-index image reloads and SVG crop changes therefore still update position.
The position cache retains the source double coordinates instead of rounding
its keys to floats. An explicit validity flag also handles a first position
that happens to equal the old sentinel value.

This is **Xbox-specific**, although its guarded code lives in the shared
renderer and `RenderInfo` files. The other-platform preprocessed transform
function is unchanged. Game scripts, update rate, physics and the transform
formulas are unchanged. The compiled Xbox `RenderInfo` grows from 44 to 120
bytes: 76 additional bytes per sprite for the explicit cache keys.

## Validation

```sh
python3 tests/xbox_render_transform_cache_test.py
```

The test compiles the actual function and Xbox `RenderInfo` under ASan/UBSan.
It compares cached results with forced recomputation across 30,000 mixed
changes, including rotation styles, same-index image geometry changes,
viewport/quality changes, fractional coordinates and copied clones. Known
position/flip cases check the formula independently. Unchanged and scrolling
calls reuse the angle calculation, while rotation/style changes and explicit
invalidation still refresh it. The non-Xbox path also compiles.

An optional `--reference /path/to/previous-renderer.cpp` comparison checks the
same cases against the pre-change function. This passed with commit
`89e186b9`; its old sentinel collision is explicitly excluded because the
candidate intentionally fixes that first-render case. Separately preprocessing
both versions without `__XBOX__` produces identical function tokens.

Normal and enhanced-profile NXDK Release builds pass. The normal executable
contains no frame-profile format string. The enhanced profile can separate
CPU drawing/queueing from SDL presentation and count long event polls; see the
[Appel pacing notes](xbox-appel.md#next-pacing-diagnostic).

**Physical performance and visual acceptance remain pending.** Work-count and
host checks do not establish an Xbox speedup. The running Xbox has not been
changed. Candidate binaries, build/source manifests, the optional reference,
preprocessing proof and private emulator checks are kept locally under ignored
`build-xbox/appel-transform-cache-20261027/`.
