"""Musical correctness of the data in index.html.

Data is read straight from the app (see appdata.py), so these tests follow the
file as it changes. They check what a guitarist / theory teacher would check:
shapes, fingers, the notes each shape sounds, key spellings, roman numerals,
functions, sol-fa, bass positions, song maps and capo transposition.
"""
import re

import pytest

import appdata

D = appdata.load()
CH, FB, KEYS, ST, PAT, FIN = D["CH"], D["FB"], D["KEYS"], D["ST"], D["PAT"], D["FIN"]
SOLFA, TON, PCN, GIG, OPEN = D["SOLFA"], D["TON"], D["PCN"], D["GIG"], D["OPEN"]

STD_TUNING = [40, 45, 50, 55, 59, 64]  # E2 A2 D3 G3 B3 E4
LETTER_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
LETTERS = "CDEFGAB"
ACC = {"": 0, "♯": 1, "#": 1, "♭": -1, "b": -1, "𝄪": 2, "𝄫": -2}


def pc(name):
    name = name.strip()
    return (LETTER_PC[name[0]] + sum(ACC[c] for c in name[1:])) % 12


def spell_note(letter, target_pc):
    """Spell target_pc on the given letter (C..B) with ♯/♭ as needed."""
    d = (target_pc - LETTER_PC[letter]) % 12
    if d > 6:
        d -= 12
    return letter + {0: "", 1: "♯", 2: "𝄪", -1: "♭", -2: "𝄫"}[d]


def parse_chord(name):
    """'F#' -> ('F♯', quality) where quality is one of maj, min, 7, maj7, 5."""
    m = re.fullmatch(r"([A-G])([#b♯♭]?)(m|maj7|7|5)?", name)
    assert m, "unparsed chord name " + name
    root = m.group(1) + {"#": "♯", "b": "♭"}.get(m.group(2), m.group(2))
    q = {None: "maj", "m": "min"}.get(m.group(3), m.group(3))
    return root, q


QUALITY = {  # (letter steps, semitones) above the root
    "maj": [(0, 0), (2, 4), (4, 7)],
    "min": [(0, 0), (2, 3), (4, 7)],
    "7": [(0, 0), (2, 4), (4, 7), (6, 10)],
    "maj7": [(0, 0), (2, 4), (4, 7), (6, 11)],
    "5": [(0, 0), (4, 7)],
}


def correct_spelling(name):
    root, q = parse_chord(name)
    li, rp = LETTERS.index(root[0]), pc(root)
    return [spell_note(LETTERS[(li + st) % 7], (rp + semi) % 12) for st, semi in QUALITY[q]]


def sounding(shape):
    """MIDI notes for a 6-char fret string like 'x02220' (low E first)."""
    return [STD_TUNING[i] + int(f) for i, f in enumerate(shape) if f != "x"]


EXPECTED_SHAPES = {
    "A": "x02220", "E": "022100", "D": "xx0232", "Am": "x02210", "E7": "020100",
    "C": "x32010", "G": "320003", "F": "xx3211", "Fmaj7": "xx3210", "Em": "022000",
    "Bm": "x24432", "F#": "244322", "Amaj7": "x02120", "E5": "02xxxx", "A5": "x02xxx",
    "G5": "35xxxx", "C5": "x35xxx", "D5": "x57xxx",
}


# ---------------------------------------------------------------- shapes

def test_tuning_is_standard():
    assert OPEN == STD_TUNING


def test_eighteen_shapes():
    assert len(CH) == 18
    assert set(CH) == set(EXPECTED_SHAPES)


@pytest.mark.parametrize("name", sorted(EXPECTED_SHAPES))
def test_shape_frets_are_the_standard_voicing(name):
    assert CH[name]["f"] == EXPECTED_SHAPES[name]


@pytest.mark.parametrize("name", sorted(EXPECTED_SHAPES))
def test_shape_spelling_is_correct(name):
    assert CH[name]["t"].split(" ") == correct_spelling(name)


@pytest.mark.parametrize("name", sorted(EXPECTED_SHAPES))
def test_shape_sounds_its_spelling(name):
    c = CH[name]
    notes = sounding(c["f"])
    spelled = c["t"].split(" ")
    assert {n % 12 for n in notes} == {pc(x) for x in spelled}, "shape sounds a different chord"
    assert min(notes) % 12 == pc(spelled[0]), "lowest note should be the root (all shapes are root position)"


@pytest.mark.parametrize("name", sorted(EXPECTED_SHAPES))
def test_shape_fingering_is_playable(name):
    c = CH[name]
    f, g = c["f"], c["g"]
    assert len(f) == 6 and len(g) == 6
    fretted = [(i, int(f[i]), int(g[i])) for i in range(6) if f[i] not in "x0"]
    for i in range(6):
        if f[i] in "x0":
            assert g[i] == "0", "open or muted string %d has a finger" % i
    for i, fr, fi in fretted:
        assert 1 <= fi <= 4, "fretted string %d needs a finger 1-4" % i
    frets = [fr for _, fr, _ in fretted]
    assert max(frets) - min(frets) <= 3, "stretch beyond four frets"
    for a in fretted:
        for b in fretted:
            if a[1] < b[1]:
                assert a[2] < b[2], "finger numbers must rise with the fret"
            if a[2] == b[2] and a[0] != b[0]:
                assert a[1] == b[1], "one finger on two different frets"
    # a finger used on two strings at one fret is a barre (or partial barre)
    shared = {fi for _, _, fi in fretted if [x[2] for x in fretted].count(fi) > 1}
    if shared:
        assert "barre" in c, name + " uses one finger on several strings but draws no barre"


@pytest.mark.parametrize("name", [n for n in EXPECTED_SHAPES if "barre" in CH.get(n, {})])
def test_barre_is_consistent(name):
    c = CH[name]
    bf, s1, s2 = c["barre"]
    f, g = c["f"], c["g"]
    assert int(f[s1]) == bf and int(f[s2]) == bf, "barre ends must sit on the barre fret"
    for i in range(s1, s2 + 1):
        assert f[i] not in "x0" and int(f[i]) >= bf, "string under the barre is open, muted or below it"
    for i in range(6):
        if f[i] not in "x0" and int(f[i]) == bf and s1 <= i <= s2:
            assert g[i] == "1", "strings at the barre fret are held by finger 1"
    assert bf == min(int(x) for x in f if x not in "x0")


def test_display_names_use_real_sharps():
    assert CH["F#"].get("name") == "F♯"
    for n, c in CH.items():
        assert "#" not in c.get("name", "") and "#" not in c["t"]


def test_teaching_claims_about_shapes():
    # 'minor' card: A and Am differ by one note on the B string, C♯ (fret 2) vs C (fret 1)
    diff = [i for i in range(6) if CH["A"]["f"][i] != CH["Am"]["f"][i]]
    assert diff == [4] and CH["A"]["f"][4] == "2" and CH["Am"]["f"][4] == "1"
    # 'barre' card: F♯ = E shape up two frets; Bm = Am shape up two frets
    up2 = lambda s: "".join(x if x == "x" else str(int(x) + 2) for x in s)
    assert up2(CH["E"]["f"]) == CH["F#"]["f"]
    assert up2(CH["Am"]["f"]) == CH["Bm"]["f"]
    # Amaj7 = A with the G string dropped a fret (A -> G♯); fingers 2 on D, 1 on G, 3 on B
    diff = [i for i in range(6) if CH["A"]["f"][i] != CH["Amaj7"]["f"][i]]
    assert diff == [3] and int(CH["Amaj7"]["f"][3]) == int(CH["A"]["f"][3]) - 1
    assert CH["Amaj7"]["g"][2:5] == "213"
    # c-g-f tip: Fmaj7 is the small F with the high E let open
    assert CH["F"]["f"][:5] == CH["Fmaj7"]["f"][:5] and CH["Fmaj7"]["f"][5] == "0"


def test_app_root_and_pitch_classes_match_shapes():
    for n, c in CH.items():
        notes = sounding(c["f"])
        assert D["root"][n] == min(notes) % 12
        assert sorted(D["pcs"][n]) == sorted({x % 12 for x in notes})
        assert D["spellOf"][n] == c["t"].split(" ")


# ---------------------------------------------------------------- fretboards

def test_fretboard_note_names():
    for key, d in FB.items():
        groups = d.get("groups") or [[d["title"], d["notes"]]]
        for gname, notes in groups:
            for n in notes:
                s, fr, nm = n[0], n[1], n[2]
                assert (STD_TUNING[s] + fr) % 12 == pc(nm), f"{key} {gname}: {nm} is not on string {s} fret {fr}"
                assert d["from"] <= fr <= d["to"], f"{key}: fret {fr} outside the drawn range"


def test_c_major_scale_open_position():
    notes = FB["cscale"]["notes"]
    names = [n[2] for n in notes]
    assert names == ["C", "D", "E", "F", "G", "A", "B", "C"]
    midi = [STD_TUNING[n[0]] + n[1] for n in notes]
    assert midi == sorted(midi) and midi[-1] - midi[0] == 12, "one ascending octave"
    assert [b - a for a, b in zip(midi, midi[1:])] == [2, 2, 1, 2, 2, 2, 1]
    for n in notes:  # first position: one finger per fret
        assert n[3] == n[1]


@pytest.mark.parametrize("key,root", [("ctri", "C"), ("ftri", "F"), ("gtri", "G")])
def test_triad_inversions(key, root):
    d = FB[key]
    assert d["root"] == root
    triad = correct_spelling(root)
    labels = {}
    for gname, notes in d["groups"]:
        assert sorted(n[2] for n in notes) == sorted(triad), gname + " is not the " + root + " triad"
        assert [n[0] for n in notes] == [3, 4, 5], "triads sit on the G, B and E strings"
        lowest = min(notes, key=lambda n: STD_TUNING[n[0]] + n[1])
        labels[gname] = lowest[2]
        frets = [n[1] for n in notes]
        assert max(frets) - min(frets) <= 3
    assert labels == {"Root position": triad[0], "1st inversion": triad[1], "2nd inversion": triad[2]}


# ---------------------------------------------------------------- keys

KEY_TONIC = {"A": ("A", "major"), "Am": ("A", "minor"), "C": ("C", "major"),
             "Am6": ("A", "minor"), "Bm": ("B", "minor")}
SCALE = {"major": [0, 2, 4, 5, 7, 9, 11], "minor": [0, 2, 3, 5, 7, 8, 10]}
# Chromatic notes a player expects in these keys, and why.
ALLOWED_CHROMATIC = {
    ("Am", "G♯"): "raised 7th: E7 is the true dominant",
    ("Am6", "G♯"): "raised 7th: E major dominant in A minor",
    ("Bm", "A♯"): "raised 7th: F♯ major dominant in B minor",
    ("Bm", "G♯"): "raised 6th: E major (IV), as in Hotel California",
    ("C", "G♯"): "E7 = V7/vi, leading note of A minor",
}


def key_scale(k):
    t, mode = KEY_TONIC[k]
    li, tp = LETTERS.index(t), pc(t)
    return [spell_note(LETTERS[(li + i) % 7], (tp + SCALE[mode][i]) % 12) for i in range(7)]


def test_key_table_matches_names():
    for k, (t, mode) in KEY_TONIC.items():
        assert KEYS[k]["name"].startswith(t + " " + mode)
        assert TON[k] == [LETTER_PC[t], mode]


def test_key_signatures_spelled_correctly():
    assert key_scale("A") == ["A", "B", "C♯", "D", "E", "F♯", "G♯"]
    assert key_scale("C") == ["C", "D", "E", "F", "G", "A", "B"]
    assert key_scale("Am") == ["A", "B", "C", "D", "E", "F", "G"]
    assert key_scale("Bm") == ["B", "C♯", "D", "E", "F♯", "G", "A"]


@pytest.mark.parametrize("k", sorted(KEY_TONIC))
def test_chord_spellings_fit_the_key(k):
    scale = key_scale(k)
    for chord in KEYS[k]["m"]:
        for note in CH[chord]["t"].split(" "):
            if note in scale:
                continue
            assert (k, note) in ALLOWED_CHROMATIC, f"{chord} in {k}: {note} is not in {scale}"
            assert note[0] in "".join(scale), "chromatic note must be an altered scale letter"


ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7}


def degree_semis(mode, deg):
    # minor keys: natural minor degrees, V and IV may be major (that's the chord's quality, not the root)
    return SCALE[mode][deg - 1]


@pytest.mark.parametrize("k", sorted(KEY_TONIC))
def test_roman_numerals_and_functions(k):
    t, mode = KEY_TONIC[k]
    tp = pc(t)
    for chord, info in KEYS[k]["m"].items():
        rn, fn = info[0], info[1]
        m = re.fullmatch(r"(i{1,3}|iv|v|vi{0,2}|I{1,3}|IV|V|VI{0,2})(maj7|7)?(?:/(\w+))?", rn)
        assert m, f"{k}: odd numeral {rn}"
        num, ext, of = m.groups()
        root, q = parse_chord(chord)
        if of:  # secondary dominant: V of the target degree
            target = ROMAN[of.upper()]
            target_pc = (tp + degree_semis(mode, target)) % 12
            assert pc(root) == (target_pc + 7) % 12, f"{rn}: {chord} is not V of {of}"
            assert fn == "S"
            assert q in ("maj", "7")
            continue
        assert (pc(root) - tp) % 12 == degree_semis(mode, ROMAN[num.upper()]), f"{k}: {chord} is not {rn}"
        if q in ("maj", "7", "maj7"):
            assert num.isupper(), f"{chord} is major: numeral should be upper case"
        elif q == "min":
            assert num.islower(), f"{chord} is minor: numeral should be lower case"
        if ext:
            assert (ext == "maj7") == (q == "maj7") and (ext == "7") == (q == "7")
        deg = ROMAN[num.upper()]
        # 0.7 (R7): the minor-key subtonic VII is its own neutral function "N", not a dominant
        expected = {1: "T", 3: "T", 6: "T" if mode == "major" else "P", 2: "P", 4: "P", 5: "D",
                    7: "N" if mode == "minor" else "D"}[deg]
        assert fn == expected, f"{k}: {chord} ({rn}) function {fn}, expected {expected}"
        if deg == 7 and mode == "minor":
            assert len(info) > 2 and info[2] == "subtonic", "minor VII should be labelled subtonic"


@pytest.mark.parametrize("k", sorted(SOLFA))
def test_solfa_roots(k):
    t, mode = KEY_TONIC[k]
    do = (pc(t) + (3 if mode == "minor" else 0)) % 12
    syl = {0: "do", 2: "re", 4: "mi", 5: "fa", 7: "so", 9: "la", 11: "ti"}
    for chord, s in SOLFA[k].items():
        root, _ = parse_chord(chord)
        assert syl[(pc(root) - do) % 12] == s, f"{k}: {chord} root should be {syl[(pc(root) - do) % 12]}"


def test_every_stage_chord_has_function_and_solfa():
    for s in ST:
        for c in s["ch"]:
            assert c in KEYS[s["key"]]["m"], f"{s['id']}: {c} has no function in {s['key']}"
            assert c in SOLFA.get(s["key"], {}), f"{s['id']}: {c} has no sol-fa root"


# ---------------------------------------------------------------- bass

def bass_midi(string, fret):
    return {"E": 28, "A": 33, "D": 38, "G": 43}[string] + fret


@pytest.mark.parametrize("name", sorted(EXPECTED_SHAPES))
def test_bass_root_and_fifth_positions(name):
    b = D["bass"][name]
    assert isinstance(b, dict), b
    (rs, rf), (fs, ff) = b["r"], b["f"]
    assert rs in "EADG" and fs in "EADG"
    assert 0 <= rf <= 7 and 0 <= ff <= 9, "keep it in first position"
    root_pc = D["root"][name]
    assert bass_midi(rs, rf) % 12 == root_pc, f"{name}: root is not on {rs} string fret {rf}"
    assert bass_midi(fs, ff) - bass_midi(rs, rf) == 7, f"{name}: fifth is not a perfect fifth above the root"
    # the panel prints spell(c)[0] for the root and spell(c)[2]||spell(c)[1] for the fifth
    sp = D["spellOf"][name]
    assert pc(sp[0]) == root_pc
    assert pc(sp[2] if len(sp) > 2 else sp[1]) == (root_pc + 7) % 12


# ---------------------------------------------------------------- song maps and patterns

def map_chords(song):
    return [c for sec in song["map"] for bar in sec["b"] for c in bar.split(" ")]


@pytest.mark.parametrize("sid", [s["id"] for s in ST])
def test_song_map_chords_belong_to_stage_and_key(sid):
    s = next(x for x in ST if x["id"] == sid)
    for c in map_chords(s["song"]):
        assert c in s["ch"], f"{sid}: {c} in the map but not taught in the stage"
        assert c in KEYS[s["key"]]["m"], f"{sid}: {c} not in key {s['key']}"
    for bar in (b for sec in s["song"]["map"] for b in sec["b"]):
        assert 1 <= len(bar.split(" ")) <= 2
    for c in s["pair"]:
        assert c in s["ch"]
    assert set(map_chords(s["song"])) == set(s["ch"]) - {"Fmaj7"}, "every stage chord should appear in its song"


def numerals(key, chords):
    return [KEYS[key]["m"][c][0] for c in chords]


def test_twelve_bar_is_a_twelve_bar_blues():
    s = next(x for x in ST if x["id"] == "twelve-bar")
    bars = s["song"]["map"][0]["b"]
    assert len(bars) == 12
    assert numerals("A", bars) == ["I", "I", "I", "I", "IV", "IV", "I", "I", "V", "IV", "I", "V"]
    assert D["TB"] == bars


def test_four_chord_stage_is_I_V_vi_IV():
    s = next(x for x in ST if x["id"] == "four-chords")
    assert s["fret"] == "I V vi IV"
    assert numerals("C", s["ch"]) == ["I", "V", "vi", "IV"]
    verse = map_chords(s["song"])[:4]
    assert numerals("C", verse) == ["I", "V", "vi", "IV"]


def test_stage_labels_match_their_chords():
    by = {s["id"]: s for s in ST}
    assert by["a-e"]["ch"] == ["A", "E"] and by["a-e"]["key"] == "A"
    assert numerals("A", by["twelve-bar"]["ch"]) == ["I", "IV", "V"]
    assert numerals("Am", by["am-e7"]["ch"]) == ["i", "V7"]
    assert numerals("C", ["C", "G", "F"]) == ["I", "V", "IV"]
    assert by["beyond"]["key"] == "Bm" and by["beyond"]["pair"] == ["Bm", "F#"]


def test_dominants_resolve():
    """E7 (V7 of Am, or V7/vi in C) should resolve to Am wherever it appears."""
    for s in ST:
        seq = map_chords(s["song"])
        for a, b in zip(seq, seq[1:]):
            if a == "E7":
                assert b == "Am", f"{s['id']}: E7 goes to {b}"


def test_andalusian_cadence():
    t = next(x for x in D["TECH"] if x["id"] == "andaluz")
    assert t["ch"] == ["Am", "G", "F", "E"]
    assert numerals("Am6", t["ch"]) == ["i", "VII", "VI", "V"]
    # Phrygian on E: iv III II I
    assert [(pc(parse_chord(c)[0]) - 4) % 12 for c in t["ch"]] == [5, 3, 1, 0]


METRE = {4: "4/4", 3: "3/4", 6: "6/8"}


@pytest.mark.parametrize("sid", [s["id"] for s in ST])
def test_time_signature_matches_pattern(sid):
    s = next(x for x in ST if x["id"] == sid)
    assert s["song"]["time"].startswith(METRE[PAT[s["pat"]]["m"]])


def cells(p):
    return p["c"] if isinstance(p["c"], list) else list(p["c"])


@pytest.mark.parametrize("pk", sorted(D["PAT"]))
def test_strum_patterns_fill_the_bar(pk):
    p = PAT[pk]
    assert len(cells(p)) == p["b"] * p["s"]
    assert all(0 <= a < len(cells(p)) for a in p["a"])
    if p["m"] == 6:
        assert p["b"] == 2 and p["s"] == 3, "6/8 counts two dotted crotchets of three quavers"
    else:
        assert p["b"] == p["m"]


def test_finish_patterns_fill_the_bar():
    for f in FIN:
        for m, p in f["p"].items():
            assert len(cells(p)) == p["b"] * p["s"], f"{f['k']} {m}"
            assert all(0 <= a < len(cells(p)) for a in p["a"])
    flam = next(f for f in FIN if f["k"] == "flam")
    assert flam["p"]["3"]["a"] == [2, 5, 7, 9, 11], "12-beat compás accents 3 6 8 10 12"
    bossa = next(f for f in FIN if f["k"] == "bossa")["p"]["4"]
    c = cells(bossa)
    assert c[0] == "B" and c[4] == "B" and c[3] == "C" and c[6] == "C", "thumb 1 and 3, chords and-of-2 and 4"


def test_boogie_riff_is_root_fifth_root_sixth():
    s = next(x for x in ST if x["id"] == "twelve-bar")
    for ev in s["song"]["riff"]["ev"]:
        (s1, f1), (s2, f2) = ev
        lo, hi = STD_TUNING[s1] + f1, STD_TUNING[s2] + f2
        assert lo % 12 == pc("A") and hi - lo in (7, 9)


def test_gig_songs_in_A():
    for g in GIG:
        assert g["key"] == "A"
        for c in map_chords(g["song"]):
            assert c in ("A", "D", "E")
        if g.get("loop"):
            assert numerals("A", ["A", "D", "E"]) == ["I", "IV", "V"]
        else:
            assert g["song"]["map"][0]["b"] == D["TB"]


# ---------------------------------------------------------------- capo

MAJOR_KEYS = {0: ["C"], 1: ["D♭"], 2: ["D"], 3: ["E♭"], 4: ["E"], 5: ["F"], 6: ["F♯", "G♭"],
              7: ["G"], 8: ["A♭"], 9: ["A"], 10: ["B♭"], 11: ["B"]}
MINOR_KEYS = {0: ["C"], 1: ["C♯"], 2: ["D"], 3: ["E♭", "D♯"], 4: ["E"], 5: ["F"], 6: ["F♯"],
              7: ["G"], 8: ["G♯"], 9: ["A"], 10: ["B♭"], 11: ["B"]}


def test_capo_named_examples():
    S = D["sounds"]
    assert S["a-e:0"] == "A major"
    assert S["a-e:1"] == "B♭ major"
    assert S["a-e:2"] == "B major"
    assert S["c-g-f:3"] == "E♭ major"
    assert S["four-chords:1"] == "D♭ major"
    assert S["am-e7:1"] == "B♭ minor"
    assert S["beyond:2"] == "C♯ minor"


@pytest.mark.parametrize("sid", [s["id"] for s in ST])
def test_capo_sounding_key_and_spelling(sid):
    s = next(x for x in ST if x["id"] == sid)
    tp, mode = TON[s["key"]]
    for c in range(8):
        got = D["sounds"][f"{sid}:{c}"]
        name, md = got.rsplit(" ", 1)
        assert md == mode
        allowed = (MAJOR_KEYS if mode == "major" else MINOR_KEYS)[(tp + c) % 12]
        assert name in allowed, f"{sid} capo {c}: {got}, expected one of {allowed}"


# ---------------------------------------------------------------- register 0.7 (tests/reports/spec07/SPEC_07.md)

def test_R6_greensleeves_verse_bar_3_is_A_minor():
    """Traditional harmony: the melody's G♯ in bar 3 sits against Am, not F."""
    s = next(x for x in ST if x["id"] == "six-eight")
    verse = next(m for m in s["song"]["map"] if m["s"] == "Verse")
    assert verse["b"] == ["Am", "G", "Am", "E", "Am", "G", "Am E", "Am"]
    assert verse["b"][2] == "Am"
    assert numerals("Am6", verse["b"][:4]) == ["i", "VII", "i", "V"]
    refrain = next(m for m in s["song"]["map"] if m["s"] == "Refrain")
    assert refrain["b"] == ["C", "G", "Am", "E", "C", "G", "Am E", "Am"]
    # nothing in the stage is left over from the old bar: chords taught == chords charted
    assert "F" not in map_chords(s["song"])
    assert set(s["ch"]) == set(map_chords(s["song"])) == {"Am", "G", "E", "C"}
    assert s["pair"] == ["Am", "E"]
    # the Andalusian cadence card still has its F, with a function and a sol-fa root in A minor
    assert KEYS["Am6"]["m"]["F"][:2] == ["VI", "P"] and SOLFA["Am6"]["F"] == "fa"


def test_R7_subtonic_is_not_a_dominant():
    FN = D["FN"]
    for k, chord, dom in [("Am6", "G", "E"), ("Bm", "A", "F#")]:
        rn, fn, lab = KEYS[k]["m"][chord]
        assert (rn, lab) == ("VII", "subtonic")
        assert fn != "D" and FN[fn][0] == "subtonic"
        assert FN[fn][1] not in (FN["D"][1], FN["T"][1], FN["P"][1], FN["S"][1]), "subtonic needs its own colour"
        assert KEYS[k]["m"][dom][1] == "D", f"{dom} is the true dominant in {k}"
    assert KEYS["Am"]["m"]["E7"][1] == "D" and KEYS["A"]["m"]["E"][1] == "D"
    # only a subtonic carries the neutral function
    for k, v in KEYS.items():
        for chord, info in v["m"].items():
            assert (info[1] == "N") == (len(info) > 2 and info[2] == "subtonic"), f"{k}: {chord}"
