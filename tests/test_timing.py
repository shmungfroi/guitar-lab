"""Timed playback check.

An init script (uihelp.AUDIO_JS) wraps AudioScheduledSourceNode.start, so every
oscillator and buffer the band schedules is recorded with its start time, the
context clock at the moment it was scheduled, and what it is (click, hat,
guitar pluck, bass). We then check the schedule against the beat grid.

Sound identification (from the app's synth code):
  count-in / metronome click: sine oscillator at 1000 or 1500 Hz
  guitar pluck: buffer source of ~2.2 s (Karplus-Strong)
  hats, snare, kick noise: buffer source of 0.3 s (noise buffer)
  bass: triangle oscillator
"""
import pytest

from uihelp import starts

TOL = 0.002  # 2 ms: schedule times are computed, so this is generous


def run(app, stage, bpm, seconds, extra=None, double=False):
    st = {"stage": stage, "bpm": bpm}
    st.update(extra or {})
    pg = app(state=st, hash_=stage)
    js = "()=>{const b=document.getElementById('playMap');b.click();%s}" % ("b.click();" if double else "")
    pg.evaluate(js)
    pg.wait_for_timeout(int(seconds * 1000))
    ev = starts(pg)
    pg.evaluate("()=>{const b=document.getElementById('playMap');if(b&&b.textContent==='Stop')b.click()}")
    assert not pg.errors, pg.errors
    return ev


def clicks(ev):
    return sorted(e["when"] for e in ev if e["kind"] == "osc" and e["type"] == "sine" and e["freq"] in (1000, 1500))


def hats(ev):
    # every grid cell gets a hat; kick and snare noise share the same buffer length, so de-duplicate by time
    t = sorted(e["when"] for e in ev if e["kind"] == "buf" and e["dur"] is not None and e["dur"] < 0.5)
    out = []
    for x in t:
        if not out or x - out[-1] > TOL:
            out.append(x)
    return out


def plucks(ev):
    return sorted(e["when"] for e in ev if e["kind"] == "buf" and e["dur"] is not None and e["dur"] > 1)


def bass(ev):
    return sorted({round(e["when"], 6) for e in ev if e["kind"] == "osc" and e["type"] == "triangle"})


def on_grid(times, origin, step, tol=TOL):
    bad = []
    for t in times:
        k = round((t - origin) / step)
        if abs(origin + k * step - t) > tol:
            bad.append((round(t - origin, 4), k))
    return bad


def check_not_late(ev):
    late = [e for e in ev if e["when"] and e["when"] < e["now"] - 0.005]
    assert not late, f"{len(late)} events scheduled in the past, e.g. {late[0]}"


@pytest.mark.parametrize("bpm", [120, 200])
def test_four_four_straight(app, bpm):
    """Stage 1, four downs in 4/4: count-in 1 . 3 . | 1 2 3 4, then a strum, a hat on every beat, bass on 1 and 3."""
    beat = 60 / bpm
    ev = run(app, "a-e", bpm, 8 * beat + 2.2)
    check_not_late(ev)
    c = clicks(ev)
    assert len(c) == 6, f"count-in should be 6 clicks, got {len(c)}"
    t0 = c[0]
    assert [round((x - t0) / beat, 3) for x in c] == [0, 2, 4, 5, 6, 7], "count-in rhythm 1 . 3 . 1 2 3 4"
    down = t0 + 8 * beat
    h = hats(ev)
    assert h and abs(h[0] - down) < TOL, "first hat on the downbeat after the count-in"
    assert not on_grid(h, down, beat)
    assert len(h) >= 4
    # each strum is the six strings 16 ms apart; the first string of each strum is on the beat
    p = plucks(ev)
    heads = [x for i, x in enumerate(p) if i == 0 or x - p[i - 1] > 0.05]
    assert not on_grid(heads, down, beat), "strums off the beat grid"
    assert len(heads) >= 4
    b = bass(ev)
    assert b and not on_grid(b, down, 2 * beat), "bass should land on beats 1 and 3"


def test_shuffle_is_swung(app):
    """Stage 2 boogie shuffle: quavers swung 2:1 within each beat."""
    bpm = 150
    beat = 60 / bpm
    ev = run(app, "twelve-bar", bpm, 8 * beat + 2.0)
    check_not_late(ev)
    c = clicks(ev)
    assert len(c) == 6
    down = c[0] + 8 * beat
    h = hats(ev)
    assert len(h) >= 6
    for t in h:
        pos = ((t - down) / beat) % 1
        assert min(abs(pos), abs(pos - 2 / 3), abs(pos - 1)) * beat < TOL, f"hat at {pos:.3f} of a beat: not swung"
    offs = [((t - down) / beat) % 1 for t in h]
    assert any(abs(o - 2 / 3) * beat < TOL for o in offs), "no swung off-beats"


def test_six_eight(app):
    """Greensleeves in 6/8: tempo counts the dotted crotchet; count-in is six quavers; hats on every quaver."""
    bpm = 90
    beat = 60 / bpm
    q = beat / 3
    ev = run(app, "six-eight", bpm, 2 * beat + 2.2)
    check_not_late(ev)
    c = clicks(ev)
    assert len(c) == 6
    assert not on_grid(c, c[0], q)
    assert abs(c[-1] - c[0] - 5 * q) < TOL
    down = c[0] + 2 * beat
    h = hats(ev)
    assert h and abs(h[0] - down) < TOL
    assert not on_grid(h, down, q)


def test_three_four(app):
    """Amazing Grace in 3/4: count-in 1 2 3, then bars of three beats."""
    bpm = 160
    beat = 60 / bpm
    ev = run(app, "c-g-f", bpm, 3 * beat + 2.2)
    check_not_late(ev)
    c = clicks(ev)
    assert len(c) == 3 and not on_grid(c, c[0], beat)
    down = c[0] + 3 * beat
    h = hats(ev)
    assert h and abs(h[0] - down) < TOL and not on_grid(h, down, beat)
    b = bass(ev)
    assert b and not on_grid(b, down, 3 * beat), "waltz bass on beat 1 of each bar"


def test_S2_second_play_tap_does_not_stack(app):
    """S2: two taps on Play in quick succession must not start two overlapping bands."""
    bpm = 200
    beat = 60 / bpm
    ev = run(app, "a-e", bpm, 8 * beat + 1.6, double=True)
    c = clicks(ev)
    assert len(c) <= 6, f"{len(c)} count-in clicks scheduled: a second band was stacked"
    raw = sorted(e["when"] for e in ev if e["kind"] == "buf" and e["dur"] is not None and e["dur"] < 0.5)
    # kick noise and hat share a time on beat 1; three or more noise hits at one instant means two schedules
    from collections import Counter
    per = Counter(round(t, 3) for t in raw)
    assert max(per.values(), default=0) <= 2, "duplicate drum hits: overlapping schedules"
    p = plucks(ev)
    heads = [x for i, x in enumerate(p) if i == 0 or x - p[i - 1] > 0.05]
    if c:
        down = c[0] + 8 * beat
        assert not on_grid(heads, down, beat), "strums from a second, offset schedule"
