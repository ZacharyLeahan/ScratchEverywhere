#!/usr/bin/env python3
"""Verify diagnostic totals include multiple scheduler passes per frame."""
from pathlib import Path
import subprocess
import tempfile
root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='xbox-frame-profile-') as tmp:
    tmp = Path(tmp)
    (tmp / 'timer.hpp').write_text('''#pragma once
class Timer { double startTime = 0; public:
inline static double now = 0;
void start() { startTime = now; }
double getTimeMsDouble() { return now - startTime; }
};
''')
    (tmp / 'log.hpp').write_text('''#pragma once
#include <string>
#include <vector>
namespace Log { inline std::vector<std::string> lines; inline void log(std::string s) { lines.push_back(s); } }
''')
    (tmp / 'test.cpp').write_text('''#define SE_XBOX_PROFILE_FRAMES
#define SE_XBOX_PROFILE_THREADS
#include "xbox_frame_profile.hpp"
#include <cassert>
int main() {
for (int i=0;i<120;++i) {
    XboxFrameProfile::poll(.1);
    XboxFrameProfile::work(.2,4.5);
    XboxFrameProfile::work(0,1.5);
    XboxFrameProfile::thread("Player",6,false);
    Timer::now += 40;
    XboxFrameProfile::sample(7);
}
assert(Log::lines.size()==2);
const auto &s=Log::lines[0];
for (const auto *expected : {"fps_x100=2500", "mean_us=40000", "p95_us=40000", "input_us=199", "scripts_us=6000", "render_us=7000", "poll_us=99", "passes=240"}) {
    // Sub-microsecond floating-point rounding is allowed for fractional totals.
    if (std::string(expected)=="input_us=199") assert(s.find("input_us=199")!=s.npos || s.find("input_us=200")!=s.npos);
    else if (std::string(expected)=="poll_us=99") assert(s.find("poll_us=99")!=s.npos || s.find("poll_us=100")!=s.npos);
    else assert(s.find(expected)!=s.npos);
}
assert(Log::lines[1].find("frame_us=6000 calls=120")!=std::string::npos);
assert(XboxFrameProfile::count==0 && XboxFrameProfile::passes==0 && XboxFrameProfile::threads.empty());
}
''')
    subprocess.run(['c++', '-std=c++17', '-I'+str(tmp), '-I'+str(root/'include'), str(tmp/'test.cpp'), '-o', str(tmp/'test')], check=True)
    subprocess.run([str(tmp/'test')], check=True)
print('PASS: integer timing units, percentiles, scheduler totals, sprite costs, reset')
