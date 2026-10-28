# PacMan hardware qualification

The cdaniels7088 project uses four arrow directions, mapped to the Xbox D-pad
and left stick. It has no authored sound playback. Earlier work repaired its
Game Over name handling; power-pellet scoring and frightened costumes now pass. Eating a frightened
ghost and a complete board remain unverified.

## Combined pen/exact-pixel engine regression, October 27

Normal candidate `b75e9beb` selected and launched PacMan from the browser.
Holding Up at the initial corridor left the player below the cage wall at
Score 0 while ghosts continued moving. Right collected pellets for Score 20;
Up turned into the next corridor for 40, then Left reached 70. A later original
capture shows 80, followed by a visible natural Game Over. Short Start replay
restored Score 0 and the initial player position, and another Right hold
scored 20. Exit returned to the populated game list.

A fresh browser selection and launch again started at zero. Left moved through
the opening corridor and scored 20; a second Exit returned to the populated
browser. These checks used only HDMI observation
and ordinary controller reports; no debugger, watch state or game-state writes
were used.

A host helper's attempted upper-left bonus route failed. Its global yellow
bounding box included disconnected image noise and later the large yellow
Game Over illustration, so its reported waypoint positions are excluded.
Neither a bonus collection nor frightened/eaten ghosts is established by that
attempt. A replacement connected-component detector requires one player-sized
shape and rejects the ending illustration; six stored-image checks pass, but
that is host-detector validation, not new gameplay evidence.

Ignored evidence is in `hardware/pen-regression-pacman-*.jpg`, the associated
controller reports, `pen-regression-pacman-verification.json`,
`pen-regression-pacman-power-excluded.json` and
`pacman-connected-detector-check.json`. The shared intermittent KVM delivery
issue remains open.


## Power pellet on normal Xbox, October 28

On diagnostics-off `ac3142d7…`, ordinary P3 controller input reached the
upper-left power pellet. The native score changed **100 → 200**, the large
pellet disappeared, and both previously red/cyan ghosts visibly turned blue.
The original project and runtime were unchanged; this test used HDMI pixels
and controller reports, without debugger or game-state writes.

The original maze requires a detour around the lower vertical wall. In video
coordinates, the successful route continued from `(279,253)` through
`(279,210)`, `(225,210)`, `(225,85)`, `(135,85)` to the pellet at `(135,40)`.
A preceding attempt to go directly from the starting corridor to X=225 stopped
at X=279 with Score 20: that was a real wall, not a runtime movement failure.
The first short-B resume attempt had not visibly left the pause menu and is
also excluded. The connected detector rejected both menu and ending artwork.

Original before/after frames are
`build-xbox/hardware/pacman-power-route3-20261028-frames/waypoint-3.jpg`
and `route-complete.jpg`. The folder retains the exact executed helpers;
`pacman-power-physical-verification-20261028.json` records the review and
hashes. The earlier globally thresholded route remains excluded. Eating a
frightened ghost and clearing all 92 dots/bonuses still need normal hardware
proof; a blue costume alone does not establish either result.

A subsequent continuous Green Flag run collected that pellet again (Score
190 with blue ghosts) and traversed the upper corridor to Score 250. By then
the ghosts had returned to normal costumes; the next contact ended the round.
Two other attempts ended earlier. These are ordinary loss/progression checks,
not ghost-eating passes. `pacman-power-hunt3-20261028-frames/` retains the
original frames and full controller/camera route. No project or runtime fix
was needed for the verified power-pellet behavior.

The final Exit returned to the populated browser. The homebrew controller
reset combo restored XBMC for log retrieval. Full FTP readback verified the
unchanged PacMan archive
`283feafd4c25cec72c09e9de3b76722aba3997c788342e340212f797fc7081d9`
and recorded its controls, while also rechecking the installed Catch repair,
rollback archive, normal `ac3142d7…` test executable and unchanged primary
`b75e9beb…` launcher. The native log records both game loads, cleanup and
browser returns without runtime errors. Evidence is
`build-xbox/hardware/pacman-followup-readback-20261028/receipt.json` and
`normal-log.txt`; `pacman-followup-browser-20261028.jpg` shows the final Exit.
