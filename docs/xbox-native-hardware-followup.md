# Native Xbox hardware follow-up — October 29, 2026

The 128 MB physical Xbox now has a limited native-backend gameplay result on
unchanged main. **Startup reliability and all-21-game qualification remain
open.** No initialization experiment from this investigation was merged.

## Normal main build

The separate executable is SHA-256
`207edc251d01fb9ddfba341b2ab67557f278b2c5ea514bf3287efddb4bd86f08`.
It was built from the code merged in [PR 43](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/pull/43);
main `2760ff8c…` adds documentation to that code. All tracing, GPU probes and
frame/thread profiling are off. The test requests NV2A graphics/windowing and
Xbox audio; the recovered log confirms those actual backends.

After a longer startup observation, the native browser appeared. A separate
8-second HDMI stream retained 71 frames. Catch Apples then passed:

- Selection from the normal game list and actual archive loading.
- Normal timer expiry at **Score 13 / Timer 0**, with Game Over visible.
- Short Start replay to **Score 0 / Timer 30**.
- D-pad Right and Left while the replay timer advanced; the score reached 2.
- Back pause, held-A confirmation and one clean return to the populated browser.
- Start + Back + both triggers held three seconds, followed by XBMC recovery.

The replay/steering recording retains **148 original JPEG frames over 6.82
seconds**. These are capture measurements, not game FPS. A separate Left input
after timer expiry is excluded from steering evidence. This is one native Catch
launch/exit cycle; it does not establish repeated handoff reliability, audio
quality, smoothness, another game's behavior or retail 64 MB support.

The same executable also passed a separate legacy Xbox-renderer Catch trial:
timer ending, short-Start replay, recorded Right/Left steering, one browser
return, and the System menu's Restart Xbox confirmation. Its saved audio choice
was SDL3, but its log identifies the actual fallback backend as Xbox audio.

## Purple startup and the rejected experiment

Earlier captures of normal main and a logging-only variant showed purple even
though their logs reached the browser. The logging-only variant continued
finishing frames and accepted a three-second controller reboot. Therefore
purple did not, by itself, establish an unresponsive application.

A diagnostic variant passed all 14 GPU pixel probes on this console, including
viewport/scissor, off-screen target restoration, alpha and subrect composition.
That is a separate instrumented build, not evidence of reliable normal startup.

An experiment forcing the existing main-target restoration at construction
reached the browser twice and ran Catch, but another early capture was purple.
That trial was reset before a longer observation. Unchanged main subsequently
reached the browser under the longer observation too. **The experiment has no
demonstrated benefit and was discarded.** Neither extra probe drawing nor an
arbitrary startup delay is being shipped as a fix.

Short KVM captures can include old frames. Continue with an explicit observation
window, longer live streams, backend logs and a controller/navigation response
before classifying a startup failure. The intermittent startup issue remains
under investigation; no GPU register or timing cause has been established.

## Recovery and remaining checks

The application's reset threshold is two seconds. The shared test runner's
original maximum hold was exactly that threshold, so its failed two-second
attempt was not proof of a hard hang. A privately validated runner copy allowed
a three-second hold and recovered both the purple logging-only trial and normal
main to XBMC. Shared tracked tooling and KVM firmware were unchanged.

All test executables were uploaded to separate folders with complete FTP
readback. The primary dashboard executable and game archives/control profiles
were preserved. After testing, the exact original settings were restored with
readback verification; their SHA-256 is
`adc181b7f41955ab7356dcc88329e6416c650bd50c301bd00c647b25e78454d2`.

Next: repeated observed native starts, the other twenty games on the current
native build, longer gameplay/audio and measured Appel performance. The
[hardware checklist](xbox-game-qualification.md) retains all outstanding gates.

Private evidence is in the shared ESP-KVM observations run
`scratch-p1-reconnected-20261029T231759Z`: `main-native-long-video/`,
`main-native-catch-steering-video/`, `main-native-catch-exit/`, and the final
reset/FTP receipts. `initial-target-rejection.json` preserves the discarded
experiment; no diagnostic payloads or game archives are bundled here.
