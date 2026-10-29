# Space Invaders on Xbox

[RokCoder's game](https://scratch.mit.edu/projects/253610111/) uses Left/Right
and Space. The Xbox sidecar maps D-pad/stick steering and A to start/fire.
Release A after starting so the title's press/release sequence can finish.

## Normal hardware follow-up, October 28

The diagnostics-off `ac3142d7…` executable ran the unchanged archive
`09e3816b18a66a34bd9b696442ae0ec8eba340ef994f6793c9a987160bbc0753`
on the physical 128MB Xbox. Directed controller play demonstrated firing through
damaged shields, alien removal, saucer scoring, life loss and natural endings.
Manually reviewed ending frames show scores **260** and **1,230** in separate
rounds. The project returned to the populated browser after testing. Full FTP
readback later confirmed both the archive and normal executable identities.

A full wave is **still open**. The original has 55 aliens; their points total
990, but saucer bonuses can push a partial wave above that score. Neither 990
nor 1,230 proves a clear. The captures do not show the remaining aliens cleared
and a new group of 55 appearing with the score retained. Several camera-guided
attempts ended in losses; one stopped safely when video became stale. A trial
HUD reader misread a known 260 score and was excluded as a verification gate.

A 120-second HDMI recording contains 5,760,000 stereo frames at 48 kHz,
peak 0.0752 and RMS 0.0101. Capture wall time was 122.58 seconds. It includes
active play and ending footage; this is evidence of audio signal, not 120
uninterrupted seconds of gameplay or a subjective sound-quality pass.

Local evidence: `build-xbox/hardware/space-wave-attempt1-20261028-frames/`
and the guided-run frame folders retain original JPEGs and executed helpers;
`space-first-ending-score-detail-20261028.png` shows 260,
`space-edge-column-title-ready-20261028.jpg` shows 1,230, and
`space-wave-round2-audio-20261028.json` records capture accounting.
`catch-scoring-deploy-20261028/receipt.json` contains the subsequent full
readbacks; its saved `debug.txt` records Space Invaders loading and cleanup.
No Space Invaders scripts or runtime behavior changed for these tests.
