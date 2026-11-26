# R13 Framework: per-instrument content in The Guitar Lab

Status: DRAFT for Justin's approval (27 Nov). Drafted by Sonnet; reviewed by the main session (Opus), which corrected the tangos items (tangos is binary, not the 12-count), the bass bossa pattern (flagged for Opus verification) and the "third above" vocal item. No code written. Source read: `/home/claude/guitar-lab/index.html` (v0.8/0.9 baseline, read-only).
Scope: Rudiments, Technique and Invent tabs, stage knowledge cards, the stage-2 riff/TAB note, and the "Also try" and Record list items that depend on them.
Out of scope: Gig tab content, Path band parts (already per instrument), design pass.

---

## 1. Inventory of what is guitar-only today

### 1.1 What already varies by instrument (leave alone)

| Area | Where it lives | Notes |
|---|---|---|
| Part panel on the Path | `partPanel(s,cp)` | bass root/fifth positions (`bassPos`), drum grid (`drumGrid`, `drumPat`, `drumWords`), keys keyboard (`kbd`, `invName`), vocal cue sheet (sol-fa roots, entries, `SOLFA`). Guitar shows chord boxes. |
| Five Path steps | `GSTEPS` (guitar) and `PSTEPS` (other four) | Step 2 and 3 differ per instrument (bass roots + groove, drums groove + fills, keys voicings + changes, vocals pitch + entries). |
| Step headline | inline object in `renderStage` | "hear, find the roots, groove..." per instrument. |
| NSW rubric row labels | `renderStage` (`rub`) | Guitar / drums / vocals / other. |
| Warm-up | `WARMS`, `REFN`, `renderWarm` | Fully per instrument. Already has a drums, keys and vocal "spider" slot. |
| Metronome cells | `metroCard`, `patName`, `countCells` | Drums see a count, not D/U/B/C. Other non-guitar see a note that the letters are the guitar's strum. |
| One-minute changes card | `renderSide` | Hidden for drums and vocals. Shown for bass and keys (pair of roots/chords). |
| Capo wording and sounding key | `renderSide`, `partPanel` | Bass, keys, vocals read the sounding key. |
| Progress keys | `gk`, `kk`, `ik`, `mineKey` | `stage@inst`, `r:id@inst`, `t:id@inst`. Changes and journal carry `inst`. |
| Journal placeholders | `JPH` | Per instrument. |
| Band mute buttons, band synth | `PARTS`, `bass()`, `keys()`, `drum()` | Already four instrument voices. |

### 1.2 What is guitar-only but shown to everyone

| Tab / area | Structure and function | Guitar-specific content | What other instruments see today |
|---|---|---|---|
| Rudiments | `RUD` (10 items, `st` 0-4), `renderRud`, `itemCard(it,'r:','r')`, `mkTab` | Pulse on low E, string crossing, spider 1-2-3-4 TAB, pendulum strum, lift-hover-land, palm muting (A5 TAB), hammer-on/pull-off, finger independence 1-3/2-4, slides, thumb and fingers (p i m a). | Whole guitar list, with one grey line: "written for guitar, anything you log is kept for [instrument] only". A drummer can tick "Palm muting". |
| Technique | `TECH` (12 items, `st` 1-5), `renderTech`, groups `core` + four `FIN` Finishes, `box()`, `fretboard()`, `FB` data | Core: power chords, C scale position 1, I-IV-V triads (fretboard). Rock: boogie shuffle, backbeat accents. Flamenco: rasgueado, golpe, Andalusian cadence. Bossa: Amaj7/E7 grips. Metal: gallop, tremolo picking, bends. | Same guitar list plus the same grey line. |
| Invent | `renderInvent`, `CHG` (7 change prompts), `learned()`, `box()`, `playSeq` | Chord-box loop of four chords; prompts "Swap the strum", "Swap one voicing: F for Fmaj7", "Swap one voicing: E for E7". | Chord boxes (guitar shapes) and strum prompts. Loop playback works for all. Journal entry is tagged `Invent` with `inst`. |
| Path knowledge cards | `KNOW` (12 entries), `ST[i].know`, `renderSide` | `strings`, `parts`, `boxes`, `tab`, `minor` ("one fret on the B string"), `barre`. Mixed: `e7`, `func`, `four`, `six`, `vii`, `sec` are mostly theory, with small guitar phrasing ("chord boxes", "Axis of Awesome" aside is fine). | All twelve, shown as `<details>` cards on every instrument. |
| Stage-2 riff/TAB | `ST[1].song.riff` (title + `ev`), rendered in `renderStage` via `mkTab` | Six-line boogie riff, string numbers, "move up a string set". | Guitar TAB under the song card for all instruments. |
| Also try / tip | `ST[].also`, `ST[].tip` | "Riptide ... from your Guitar Book; capo 1"; "Can't get the small F to ring". | `also` shows to all (partly guitar-flavoured). `tip` only inside the guitar branch (fine). |
| Record tab | `renderRecord`: `RUD.concat(TECH).filter(lvl(ik(...))>=2)` | Lists "Rudiments and techniques at Consistent" from the guitar lists. | Reads the guitar arrays, so it must switch to the instrument's lists. |
| Finish strip and Technique groups | `FIN` (rock, flamenco, bossa, metal), `renderTech` | Finish changes the band feel for everyone (`bandPat`), but Technique content for each Finish is guitar-only. | Same. |
| Bass (partial coverage) | Path steps, part panel, warm-up are good. | Rudiments "pulse" and "spider" suit bass as written; "pendulum strum", "hover", "hammer", "thumb and fingers", all Technique items, Invent and `KNOW` are still guitar. | Mixed. |

Bass verdict: roughly 3 of 10 rudiments transfer as they stand (pulse, string crossing, spider). Everything else needs a bass version.

### 1.3 Harmonic route (shared spine, all instruments)

`ST` has eight stages; `pat` is the Path pattern, `tgt` the target tempo, the numbered `st` on RUD/TECH items is a 0-based index into this list ("opens with stage st+1").

| # | `id` | Chords (key) | Feel / time | Song (public domain or chord map only) | Target | Harmonic job (the teaching point) |
|---|---|---|---|---|---|---|
| 1 | `a-e` | A, E (A) | four crotchets, 4/4 | Skip to My Lou | 90 | I and V; do and so; bright pair. |
| 2 | `twelve-bar` | A, D, E (A) | swung shuffle, 4/4 | 12-bar in A | 100 | I-IV-V; 12-bar as three lines of four bars; swing. |
| 3 | `am-e7` | Am, E7 (Am) | straight quavers | Joshua Fit... | 100 | Minor home (la); dominant pull E7 to Am; one note changes the colour. |
| 4 | `c-g-f` | C, G, F/Fmaj7 (C) | 3/4 waltz | Amazing Grace (pickup) | 90 | I-IV-V in C; do-fa-so; 3 beats; pickup. |
| 5 | `four-chords` | C G Am F (C) | pop 4/4, syncopated | Let It Be (map only) | 76 | I-V-vi-IV; relative minor; one loop, many songs. |
| 6 | `six-eight` | Am G E C (Am) | 6/8, two beats of three | Greensleeves | 50 (dotted crotchet) | Compound time; subtonic G vs leading-note-bearing E. |
| 7 | `hallelujah` | C Am F G E7 (C) | 6/8 felt as 12/8 | Hallelujah (map only) | 50 | Secondary dominant, V of vi; long phrases; breath. |
| 8 | `beyond` | Bm F# A E G D Em (Bm) | pop 4/4 | Hotel California (map only) | 74 | Moving shapes; minor key with sharps; bigger form. |

`SOLFA` already gives do-based names for A, C and la-based for Am, Am6, Bm. Per-instrument content below hangs off these eight ids.

---

## 2. Proposal: what each instrument sees instead

Principles (apply to every instrument):
1. Same eight stages, same gates, same level names (Not started, Exploring, Consistent, Applied). Nothing new to learn about how the app works.
2. Kodály order everywhere: embody (move, clap, hand sign, sway) then aural (sing it, hear it) then visual (grid, TAB, keyboard, sol-fa line). Every strand opens with "clap and say it" before the instrument.
3. Sol-fa and rhythm syllables (ta, ti-ti, ta-a, ti-ti-ti for 6/8 groups) are the shared language, on every instrument.
4. British/Australian terms: quavers, crotchets, bars, semitones, tonic.
5. Our own words and our own exercises. No lyrics, no method-book wording, no named method programs. Songs stay as chord maps plus a recording link, as now.
6. Safety first for the voice (Stage 4 changing voices) and for hands, wrists and hearing (drummers).

### 2.1 Shared items (stay shared unless the teacher says otherwise)

| Item | Proposal |
|---|---|
| Warm-up tab | Stays per instrument as built. Add one line per instrument pointing to its Rudiments strand. |
| Function in this stage card, metronome, one-minute changes | Stay. |
| `KNOW` theory cards: `func`, `four`, `six`, `vii`, `sec` | Stay shared, but strip guitar wording ("chord box"). `e7` stays shared (pure theory). |
| Gig tab, Record tab layout | Stay; Record reads the instrument's own lists. |

### 2.2 Bass

Rudiments (key `r:bs-...@bass`, gate `st` = stage index it opens with)

| id | Name | `st` | Content (our wording) | Criteria unit |
|---|---|---|---|---|
| `bs-pulse` | Pulse on one string | 0 | Open E, crotchets then quavers; sing "ta, ti-ti" as you pluck. | quavers, 60/100 |
| `bs-alt` | Two-finger alternation | 0 | Index, middle, index, middle on one note; even volume; rest the thumb on the pickup or string above. | quavers, 60/100 |
| `bs-cross` | String crossing and octave | 0 | Root, then the octave on the next string pair (E to E up on D string fret 2), up and back. | quavers, 60/100 |
| `bs-spider` | Fretting spider | 0 | One finger per fret on each string, frets 1-4, up and back. (From the guitar spider; kept because it suits bass.) | quavers, 60/100 |
| `bs-mute` | Muting: stop the ring | 1 | Left hand lifts to stop a note; right-hand thumb or fingers damp the strings below. Play a bar, rest a bar, clean silence. | crotchets, 70/110 |
| `bs-slide` | Hammer-on and slide | 2 | Hammer from fret 0 to 2 on the E string; slide 2 to 4 with pressure kept. | crotchets, 60/90 |
| `bs-lock` | Lock to the count | 3 | Play on every beat while a partner or the app plays the kick on 1 and 3; make the two sounds one. | crotchets, 60/100 |
| `bs-oct` | Octave shapes | 4 | Root with the octave two strings up, two frets across; move the shape to any root. | crotchets, 60/90 |

Technique

| id | Group | Name | `st` | Content |
|---|---|---|---|---|
| `bs-roots` | core | Roots on 1 | 1 | The root of each chord on beat 1; hear it as the lowest do. |
| `bs-rootfifth` | core | Root and fifth | 2 | Root on 1, fifth on 3; the fifth sits one string up and two frets along (see `bassPos`). |
| `bs-octaves` | core | Root and octave | 3 | Root, octave, root, octave in quavers; feel the bounce. |
| `bs-approach` | core | Approach notes | 4 | A semitone below or above the next root on the last beat of the bar, e.g. G♯ into A. |
| `bs-walk` | core | Walking four | 5 | Root, third, fifth, approach note, one per crotchet, over a bar of one chord. |
| `bs-kicklock` | rock | Locking with the kick | 1 | Root on 1 with the kick; root on the and of 3 for a push into the next bar. |
| `bs-shuffle` | rock | Boogie walk | 1 | Root, third, fifth, sixth, fifth, third, swung (the stage 2 part). |
| `bs-gallop` | metal | Palm-muted gallop | 3 | One quaver, two semiquavers on the root, short and tight. |
| `bs-bossa` | bossa | Bossa bass | 4 | Root on 1, fifth on 3 (the two-feel), with the dotted-crotchet/quaver push into each; kept light. Exact rhythm to be verified at R13-2 (Opus). |
| `bs-compas` | flam | Tangos roots | 3 | Roots on 2, 3 and 4 with the tangos weight, beat 1 left light or rested; rests are part of the part. (Optional; see decision 9.) |

Invent: roll the stage's chords, then "build one bar of bass". Prompts: change the rhythm of the root; add the fifth; move the root to the octave; add an approach note into the next chord; leave out the root on beat 1 once and listen; double the note length. Playback uses the band bass voice, so the student hears the loop with their line.

Stage knowledge cards (replace `strings`, `parts`, `boxes`, `tab`, `minor`, `barre`; keep the shared theory cards)

| Stage | Bass card(s) |
|---|---|
| 1 | Your four strings (E A D G, one octave below the guitar's lowest four); Hands and anchor (thumb, pluck, fret, floating thumb); The root and the fifth (A: open A string; its fifth E is on the D string, fret 2). |
| 2 | Bass TAB: four lines, G on top; Boogie walk in A (TAB below); Where the kick lives: root with the kick. |
| 3 | The root alone does not say major or minor: the third does; E7's root pulls to Am. |
| 4 | One note a bar in 3/4, left to ring; do, fa, so in the bass register. |
| 5 | A loop with one lowest-note path: C G A F, and why the line steps down then up. |
| 6 | 6/8 roots on 1 and 4; G or E under Am: stepping down vs the pull of the fifth. |
| 7 | Walking into a chord: approach notes and the fifth-below pull (E7 to Am). |
| 8 | Moving one shape: the same shape is a different root on a different fret; shape for Bm and F♯. |

Stage 2 part note (replaces the guitar riff for bass): a four-line TAB of the boogie walk. In A: A string open, fret 4, D string fret 2, fret 4, back down; on D move the shape up a string; on E move it down. Rendered by a new `mkTabBass` (four lines) from the same `ev` data shape. Check in section 6 (Opus).

### 2.3 Drums (grid-first, notation optional)

Rudiments

| id | Name | `st` | Content | Criteria unit |
|---|---|---|---|---|
| `dr-grip` | Grip, stool, rebound | 0 | Stool height, matched grip, let the stick bounce; ten taps each hand, a quiet pad is fine. | taps, evenness |
| `dr-single` | Single strokes | 0 | R L R L, two then four per click; same height, same sound. | quavers, 60/100 |
| `dr-pulse` | Hat pulse, kick on 1 | 0 | Hi-hat in crotchets, kick on 1; then quavers on the hat. | crotchets/quavers, 60/100 |
| `dr-double` | Double strokes | 1 | R R L L, two bounces per hand; build even. | quavers, 60/90 |
| `dr-shuffle` | Swung hat (long-short) | 1 | Hat in triplet-swing, saying "long-short" or "ta-ti" with the stick. | crotchets, 70/110 |
| `dr-para` | Paradiddle | 2 | R L R R, L R L L; accent the first note of each group. | quavers, 60/90 |
| `dr-flam` | Flam | 3 | A quiet grace stroke just before a main stroke, hands at different heights; right and left versions. | crotchets, 60/90 |
| `dr-accent` | Accent and ghost | 3 | Play quavers with accents on 2 and 4 and soft ghost notes between. | quavers, 70/100 |
| `dr-limbs` | Limb independence | 4 | Kick and snare together with the hat, then the kick alone, then the snare alone, each four bars. | bars, steady |

Technique

| id | Group | Name | `st` | Content |
|---|---|---|---|---|
| `dr-8beat` | core | 8-beat rock groove | 1 | Hat quavers, kick on 1 and 3, snare on 2 and 4. Counting aloud. |
| `dr-shuffle2` | core | Shuffle groove | 1 | Same backbeat, hat in swung quavers. |
| `dr-waltz` | core | 3/4 groove | 3 | Kick on 1, hat on all three, snare or rim click on 2 and 3. |
| `dr-fill` | core | One-bar fill into a section | 3 | Last bar: quavers around snare and toms, crash on 1 of the next section. |
| `dr-68` | core | 6/8 feel | 5 | Two big beats of three: kick on 1, snare on 4, hat in sixes. |
| `dr-ghost` | core | Dynamics and sections | 4 | Quieter verse (hat or side-stick), louder chorus (open hat or crash). |
| `dr-backbeat` | rock | Backbeat power | 1 | Same backbeat, heavier snare, same tempo. |
| `dr-tangos` | flam | Tangos on cajón or kit | 3 | Tangos is in four (binary), not the 12-count: beat 1 light, weight on 2, 3 and 4 (matches `FIN`, Justin 26 Nov). |
| `dr-bossa` | bossa | Side-stick bossa | 4 | Side-stick and a light hat; the kick on 1 and 3 stays soft. |
| `dr-gallop` | metal | Kick gallop (optional) | 3 | Quaver then two semiquavers on the kick under steady hats; teacher checks for tension. |

Invent: "Roll a groove". A 4-row, 8-cell grid (hat, snare, kick, open hat) pre-filled with the stage groove, student moves one kick, then plays it. Change-one prompts: move one kick to the and of 2; open the hat on the and of 4; swap the backbeat to half-time; play the same groove in 6/8; add a one-bar fill in bar 4; leave the hat out for one bar.

Stage knowledge cards

| Stage | Drum card(s) |
|---|---|
| 1 | The kit: kick, snare, hat, ride, crash, toms; Grip and posture; Count it: crotchet and the bar (ta, ti-ti). |
| 2 | The 12-bar is three lines of four bars (call, answer, close); Shuffle: long-short; Reading the grid. |
| 3 | Straight quavers; backbeat on 2 and 4; softer minor, same groove (colour is dynamics). |
| 4 | Three beats; pickup bar and what the drummer plays before the melody; Rim click. |
| 5 | Fills: lead the band into the next section; four-bar phrases mark where fills go. |
| 6 | 6/8: two beats of three; the dotted crotchet pulse. |
| 7 | Building a ballad: quiet verse, bigger chorus; crash on the cadence. |
| 8 | Driving four with open hat; keeping time when the band gets big. |

Stage 2 part note: the 12-bar "form card" in place of TAB: a 12-cell bar strip (three lines of four) with a fill marker in bars 4, 8 and 12, and a swung groove grid. Uses `drumPat`/`drumGrid`.

### 2.4 Keys

Rudiments

| id | Name | `st` | Content | Criteria unit |
|---|---|---|---|---|
| `kb-place` | Find your place | 0 | Middle C and the black-key groups; find A, E, C, G, F in two octaves. | notes found |
| `kb-five` | Five-finger position | 0 | C D E F G with fingers 1-5, right then left, then hands together an octave apart. | crotchets, 60/100 |
| `kb-touch` | Touch: legato and staccato | 0 | Same five notes, connected then short. | crotchets, 60/90 |
| `kb-triad` | Triad shape | 1 | Root, third, fifth by skipping a finger: 1-3-5. | changes a minute, 30/45 |
| `kb-hover` | Lift, hover, land | 1 | Change chords by lifting the whole hand, hovering, landing together. | changes a minute, 30/45 |
| `kb-scale` | C scale, thumb under | 3 | Right hand, then left; say the sol-fa as you play. | quavers, 60/90 |
| `kb-arp` | Broken chord | 3 | 1-3-5-3, each note one quaver, hands separately. | quavers, 60/100 |
| `kb-comp` | Comping hands together | 4 | Left hand roots, right hand triads, a chord a bar, then a chord a beat. | bars, steady |

Technique

| id | Group | Name | `st` | Content |
|---|---|---|---|---|
| `kb-inv` | core | Triads and inversions | 3 | C, F, G in root position and both inversions; choose the one nearest the last chord. |
| `kb-vl` | core | Smallest step (voice leading) | 4 | Move between chords keeping common notes still (C to Am: keep C and E). |
| `kb-lh` | core | Left-hand patterns | 3 | Root alone; root and fifth; octave. |
| `kb-comp2` | core | Comping rhythms | 4 | Whole bar, crotchets, "ta ti-ti ta" rhythm, backbeat stabs. |
| `kb-waltz` | core | Waltz comp | 3 | Bass on 1, chord on 2 and 3. |
| `kb-roll` | core | 6/8 rolling arpeggio | 5 | Low, middle, high, repeated twice a bar; sustain pedal optional. |
| `kb-shuffle` | rock | Boogie left hand | 1 | Root-fifth then root-sixth in swung quavers; one hand, then add chords. |
| `kb-stab` | rock | Backbeat chords | 1 | Short chords on 2 and 4. |
| `kb-maj7` | bossa | Maj7 and 7th grips | 4 | Fmaj7, Amaj7 and E7 as four-note grips, left hand on the root. |
| `kb-phrygian` | flam | Andalusian line | 5 | Am G F E as chords, right hand stepping down; E is home. |
| `kb-power` | metal | Octave and fifth power | 3 | Left hand octaves, right hand open fifths; clipped. |

Invent: roll the chords, choose a comping rhythm and an inversion. Prompts: change the rhythm; invert one chord; drop the left hand to octaves; add the seventh; spread the chord into a broken chord; hold the pedal for a bar.

Stage knowledge cards

| Stage | Keys card(s) |
|---|---|
| 1 | The keyboard map; Fingers 1-5; A and E as triads (A C♯ E, E G♯ B). |
| 2 | Left-hand shuffle (root-fifth, root-sixth); Reading a chord chart; 12 bars as three lines. |
| 3 | Lower the third: A C♯ E becomes A C E; E7's G♯ and D point to Am. |
| 4 | Inversions: three ways to play one chord; Waltz feel. |
| 5 | Common notes and smallest steps through C G Am F. |
| 6 | Rolling in six: the arpeggio as the pulse; G or E under Am. |
| 7 | E7 as V of vi: the black-key G♯ pointing to A. |
| 8 | Sharps: F♯, B minor, and why the shapes feel different on the black keys. |

Stage 2 part note: the left-hand boogie bar on a keyboard (`kbd`-style) with the right-hand sixth leap marked; same swung `ev` shape.

### 2.5 Vocals (sol-fa throughout, hand signs optional)

Rudiments

| id | Name | `st` | Content | Criteria |
|---|---|---|---|---|
| `vx-breath` | Breath and posture | 0 | Four counts in through the nose, eight out on a quiet "s"; feet flat, shoulders loose. | counts |
| `vx-sovt` | Straw and lip trill | 0 | A trill or a straw or "ng" through a low-to-high slide, three times, gently. | three clean slides |
| `vx-vowel` | Vowel shaping | 0 | One note, five vowels (ah eh ee oh oo), same tone, jaw soft. | five matched |
| `vx-match` | Pitch matching with sol-fa | 1 | Sing do, so, do from the keyboard note; point with a hand sign. | notes matched |
| `vx-scale` | do re mi fa so and back | 2 | Step by step, rhythm syllables ta, ti-ti. | tempo 60/100 |
| `vx-leap` | Leaps: do-so, do-mi-so | 2 | Hear it first, then sing; check the note on the keyboard. | notes matched |
| `vx-reg` | Register: low, middle, high | 3 | Slide across your own break gently; choose a comfortable octave. | comfort (teacher) |
| `vx-dyn` | Soft to loud to soft | 4 | One note, getting louder then softer; stay in tune. | steadiness |

Technique

| id | Group | Name | `st` | Content |
|---|---|---|---|---|
| `vx-roots` | core | Roots in sol-fa | 1 | Sing each chord's root name through the stage map. |
| `vx-entry` | core | Entries and breaths | 2 | Breathe in the bar before; pickup entries (Amazing Grace). |
| `vx-phrase` | core | Phrasing a long line | 4 | Mark a breath at the end of each four-bar line; sing connected. |
| `vx-third` | core | Singing a third above | 4 | A partner (or the keyboard) holds do; you sing mi above it, then so above mi: the chord built from your own voices. |
| `vx-68` | core | Singing in six | 5 | Three-note groups: ta-ti-ti or three syllables; lean on 1 and 4. |
| `vx-si` | core | so and si | 5 | In la-minor the raised so: G♯ against the E7 chord (hear the lift). |
| `vx-rock` | rock | Light edge, forward vowels | 1 | Bright, forward vowels, no pushing; teacher present. |
| `vx-bossa` | bossa | Soft onset, behind the beat | 4 | Gentle start, relaxed; slightly late on the beat. |
| `vx-flam` | flam | Descending line | 5 | Sing the Andalusian line down in sol-fa (la so fa mi); decoration is optional. |
| `vx-metal` | metal | Teacher-led only | 5 | Placeholder card, "ask your teacher"; no harsh sounds taught in the app (decision 8). |

Invent: roll a four-note sol-fa motif from do-re-mi-so-la (la-based in the minor stages) and a rhythm cell (ta, ti-ti, ta-a), sing it over the loop. Prompts: change the rhythm; start on a different note; answer your phrase (call, response); leap then step; end on home (do, or la in minor); sing it an octave lower.

Stage knowledge cards

| Stage | Voice card(s) |
|---|---|
| 1 | How the voice makes sound (breath, vibration, resonance); Finding your comfortable range; do and so (home and the pull). |
| 2 | 12 bars in sol-fa: do do do do, fa fa do do, so fa do so; Where to breathe. |
| 3 | Minor is la-based: home la, the E7 root is mi; the raised so is si. |
| 4 | Three beats; the pickup breath; do-fa-so. |
| 5 | Melodies lean on chord notes (do, mi, so); a third above. |
| 6 | Syllables in six; G is so, G♯ is si. |
| 7 | Long phrases and breath planning; chest and head register; pick your capo for your voice. |
| 8 | Blend and balance with the band; range and comfort in a bigger song. |

Stage 2 part note: the vocal blues line in sol-fa (the twelve-bar strip with sol-fa roots), replacing guitar TAB.

---

## 3. Decisions needed (teacher)

1. Depth: ship all four instruments at the full size above (about 8 Rudiments, about 8 Technique, Invent, 8 knowledge-card stages each), or ship a thinner first release (4 Rudiments, 4 Technique per instrument) and grow?
2. Gates: do per-instrument Technique and Rudiment items unlock on the same stage gates as guitar (`st`), or does each instrument keep its own gate table?
3. Drums: grids and word descriptions only, or add a notation view (stave, percussion clef) for the groove and fills? If notation, from which stage?
4. Vocals: sol-fa used for everything (roots, melodies, exercises), or sol-fa plus note names? Hand signs: draw them, describe them, or leave to the classroom?
5. Shared items: confirm the Warm-up tab, Function card, one-minute changes and the theory `KNOW` cards stay shared, with the guitar-only wording removed.
6. Keys: use the sustain pedal in the content, or leave it out for school keyboards? Keep the keys part in C white-key shapes and let the capo setting transpose, or write each stage in its own key?
7. Finish groups: show every Finish's Technique group to every instrument (flamenco, bossa, metal moves), or only core + rock + the current Finish?
8. Vocals: any Finish-specific vocal technique at all (rock edge, metal)? Proposal: none in the app, "ask your teacher" only.
9. Bass flamenco: keep a flamenco bass group (roots only) or omit it for bass?
10. Voice safety: should the app say anything about changing voices and range for Stage 4 students, and a "sing in your own octave" default?
11. Orphan data: students who logged guitar items while on another instrument (keys like `r:cross@drums`). Hide them quietly, or list them in Record as "from guitar items"?
12. Wording and names: any phrases you do not want (the app must not copy method books or name method programs)?
13. Priority order for the four instruments (suggested: bass, drums, vocals, keys), and who reviews each for musical accuracy?

---

## 4. Data and architecture note

Constraints: keep the localStorage key `shredder`; keep `DEF`/`loadState` validation (`kindOK`) happy; keep every existing key shape; do not touch guitar content.

1. New constant, one block, alongside `RUD`/`TECH`:

   ```
   INSTC = { bass:{rud:[],tech:[],know:{},part2:{},invent:{}}, drums:{...}, keys:{...}, vocals:{...} }
   ```
   Guitar keeps `RUD`, `TECH`, `KNOW`, `ST[].song.riff` as they are. Prefer a JSON `<script type="application/json" id="instData">` (like `chordData`) so tests can read it in Python without running the page.
2. Accessors: `rudOf()`, `techOf()`, `knowOf(id)`, `part2Of(stage)`, `inventOf()`, each `S.inst==='guitar' ? <existing> : INSTC[S.inst]...`. Used by `renderRud`, `renderTech`, `renderInvent`, `renderSide`, `renderStage`, `renderRecord`.
3. Item ids: always prefixed (`bs-`, `dr-`, `kb-`, `vx-`), never reuse a guitar id. Reason: existing saves already hold per-instrument stray keys (`r:pulse@bass`, `t:power@drums`) written by the old guitar list. Reusing `pulse` would turn a stray tick into a false "Done". New prefixed ids start at Not started.
4. Progress keys: no change. `ik('r:'+id)` already appends `@inst`, so `r:bs-pulse@bass` is a valid key with no new `DEF` field. `S.lv`, `S.best` stay flat maps. Unlocks stay via `unlocked(it.st)` over that instrument's own `passed(stage)` (`kk` is per instrument).
5. `itemCard` generalised, not forked: item gets optional `crit` (strings), `unit`, and a `kind` renderer (`tab4` for bass, `grid` for drums, `kbd` for keys, `solfa` for vocals). Guitar items pass through unchanged. The best-tempo input is shown only where the item has a tempo unit (not for vocals items measured by "matched").
6. Page copy: the grey "written for guitar" line in Rudiments/Technique goes away for the four instruments (their own list is shown). Guitar stays word-for-word.
7. `KNOW`: split the shared theory entries from guitar-only; `s.know` is the guitar list. For non-guitar read `INSTC[inst].know[stageId]` (array of `{t,b}`) followed by the shared cards listed in section 2.1.
8. Invent: `renderInvent` branches by instrument, but the roll logic (pool from `learned()`, `CHG`) stays one code path where possible. Saves into `S.journal` with `inst` and `tag:'Invent'` as now.
9. Record: `RUD.concat(TECH)` becomes `rudOf().concat(techOf())`.
10. Migration: none needed for the four new lists. Add a small guard in `loadState` that ignores unknown ids on render rather than deleting them, so a backup from a newer build imported into an older build loses nothing.
11. Backup/import: `bkCount` and `validate` keep working; a backup made on this build has extra `@inst` keys, which older builds already tolerate.
12. Size: estimated +30 to 45 KB. Check page load on a school Chromebook after the first instrument ships.

---

## 5. Test plan (new `test_R13_*` plus data tests)

Test ids below are X1–X13 in the spec (to avoid clashing with register items T1–T5 already in the suites); read "T" here as "X".

Run with the existing suites: `tests/test_ui.py` (Playwright) and `tests/test_chords.py` (data).

| # | Test | Proves |
|---|---|---|
| T1 | Guitar snapshot: hash the rendered `innerHTML` of Rudiments, Technique, Invent and each of eight stage side panels for guitar, before and after R13. | Guitar is byte-for-byte unchanged. |
| T2 | For each non-guitar instrument and each tab, collect rendered item names; assert they equal the ids in that instrument's data block, and none are guitar ids. | Each instrument sees only its own items. |
| T3 | Guitar-only tokens denylist per instrument and tab (e.g. "palm muting", "rasgueado", "chord box", "TAB", "pendulum", "spider" on drums and vocals; "fret" excluded for bass). | No guitar wording leaks. |
| T4 | Every stage's `know` list for each instrument is non-empty, and no stage shows a guitar-only card (`strings`, `parts`, `boxes`, `tab`, `minor`, `barre`). | Knowledge cards are per instrument. |
| T5 | Stage 2 note: guitar sees TAB with six lines; bass sees four-line TAB; drums see the form strip; keys and vocals see their own part note; none sees another's. | The riff/TAB note is per instrument. |
| T6 | `localStorage` key is still exactly `shredder`; setting a level for a new item writes `r:<id>@<inst>` and nothing else changes shape. | Save format unchanged. |
| T7 | Load fixtures from `tests/appdata.py` (pre-R13 saves, including saves with stray `r:cross@drums`): they load, guitar progress intact, stray keys do not mark new items Done. | No broken saves; no false progress. |
| T8 | Gates: item with `st=3` shows "Opens with stage 4" until that instrument passes stages 1-3; passing on bass does not open it for drums. | Unlocks are per instrument. |
| T9 | Switching instrument on the Path changes Rudiments, Technique and Invent on next view; level controls are independent. | Selector drives content. |
| T10 | Invent: for each instrument, roll then save; journal entry has the right `inst`, tag and no guitar prompt text. | Invent per instrument. |
| T11 | Data tests (Python): sol-fa names valid and la-based in minor stages; every bass tab fret/string maps to the named note; keys inversions spell the chord; drum grids' length matches `PAT` beats; approach notes are a semitone from the next root. | Theory correct. |
| T12 | Content policy tests: no lyrics (long quoted lines), no names on a teacher-supplied denylist, British terms (no "eighth note", "measure", "whole note"). | Our own content only. |
| T13 | Render matrix (existing 8 stages x 7 tabs x 5 instruments x 3 widths x light/dark): still no console errors or horizontal overflow with the new items. | No layout regression. |

---

## 6. Suggested build split and model routing

| Stage | Work | Model |
|---|---|---|
| R13-0 | Teacher approves this framework and answers the decisions list. | (teacher) |
| R13-1 | Plumbing: `INSTC` block, accessors, `itemCard` generalisation, Record switch, guitar snapshot test (T1, T6, T7). No new content. | UI: Fable |
| R13-2 | Theory logic: bass TAB renderer and positions, approach notes, keys inversion/voice-leading data, sol-fa motif generator for minor/major, drum grid validators; data tests (T11). | Opus |
| R13-3 | Bass content (Rudiments, Technique, Invent, cards, stage-2 note). | Content and UI: Fable |
| R13-4 | Drums content. | Fable |
| R13-5 | Vocals content, with the safety wording decided in decision 10. | Fable |
| R13-6 | Keys content. | Fable |
| R13-7 | Full test pass (T1-T13) and fix. | Fable |
| R13-8 | Independent check: given only the approved spec and the build output (no build conversation), runs the test plan, reads the content for accuracy and policy (lyrics, names), reports pass/fail. | Fable (spec + output only) |
| R13-9 | Teacher sign-off per instrument; merge after the independent check. | (teacher) |

Order is flexible: after R13-1 and R13-2, each instrument is independent and can ship alone, so students on that instrument get relief as soon as theirs is ready.
