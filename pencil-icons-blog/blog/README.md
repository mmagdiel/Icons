# pencil-icons / blog — hand-drawn graphite icon set

Built with the `pencil-icon-style` Mavis skill. **Vector masters are in `svg/`** — the PNGs are previews, not sources.

```
/Users/magdielmarquez/Documents/mmagdiel/Icons/pencil-icons-blog/   <- este set (el "blog")
/Users/magdielmarquez/Documents/mmagdiel/Icons/pencil-icons/        <- el set base del que se deriva
```

The set lives in the **mmagdiel/Icons** repo, deliberately outside any client
project: it is a reusable brand asset, not part of an app.

## Contents
```
svg/          31 vector masters @ 1024x1024  <- the real assets
png-256/      raster previews @ 256
png-512/      raster previews @ 512
png-1024/     raster previews @ 1024
source-d.json original source path data per icon
manifest.json full parameter set + validator result + warnings per icon
preview.html  browser gallery (open directly, no server)
contact-sheet.png  all 31 on one sheet
```

Four things sit **next to** this folder, one level up:

- `rect-corregido.svg`, `square-corregido.svg`, `search-corregido.svg` — the supplied
  drawings, cleaned: Inkscape's metadata stripped, the transform baked into the path and
  the viewBox pulled tight to the ink. See [the corrected rectangle](#the-corrected-rectangle),
  [the square](#the-square) and [the search](#the-search).
- `sources/` — the original Inkscape exports, untouched. The provenance of the three above.
- `assets/` — the four **prebuilt** masters (`rectangle-rounded.svg`, `square.svg`,
  `search.svg`, `mail.svg`) plus `source-24.json`, the assembled paths in the 24-unit space.
  These four icons do not come out of the stroke pipeline; they are copied verbatim by the
  build. See [the rectangle, used verbatim](#the-rectangle-used-verbatim).

## Shared parameters
```python
w_start = 0.32
w_end = 1.18
fillet_per_w = 2.0
fillet_samples = 80
trim_extra = 0.4
```

## What came from where

**11 icons are the base set, reproduced from their own `source-d`** — `chevron`, `plus`,
`arrow-right`, `zigzag`, `heart`, `menu`, `arrow-up`, `list`, `align-justify`,
`hash`, `x-close`. They are not reprocessed: their source `d` is byte-identical, so the build
renders the same masters. (The `heart`'s **cut** was changed in the base set itself — see
[the heart](#the-heart) — so the two folders still match byte for byte.)

**4 icons are prebuilt** — they are finished SVGs copied into the set verbatim, not
pipeline output:

| icon | what it is |
|---|---|
| `rectangle-rounded` | the supplied rectangle, corrected and used **as-is** — its own path, its own transform, its own look |
| `square` | the supplied square, corrected and used **as-is** |
| `search` | the supplied magnifier, corrected and used **as-is** |
| `mail` | that same rectangle + the flap, which is the base `chevron` **mirrored** |

**4 icons are new, derived from the base set:**

| icon | how it was derived |
|---|---|
| `arrow-left` | mirror of `arrow-right` |
| `arrow-down` | `arrow-up` rotated 180° |
| `arrow-up-right` | `arrow-up` rotated 45° — the V head becomes a corner head, which is the right glyph for ↗ anyway |
| `linkedin` | bar + `n` arch + the dot as a short stroke |

**6 more are the same idea, a rotation of the source path around the canvas centre (12, 12):**

| icon | how it was derived |
|---|---|
| `chevron-left` | the base `chevron` rotated 90° CCW |
| `chevron-right` | the base `chevron` rotated 90° CW |
| `chevron-down` | the base `chevron` rotated 180° |
| `arrow-up-left` | `arrow-up-right` rotated 90° CCW |
| `arrow-down-right` | `arrow-up-right` rotated 90° CW |
| `arrow-down-left` | `arrow-up-right` rotated 180° |

The rotation is applied to the **source path** and the pipeline re-strokes it, so the taper
travels with the shape: `chevron-left` is `chevron` turned on its side, not a new drawing
that happens to look like it. The four diagonal arrows are the four corners of the same
stroke, and they read as one family.

**6 more came from Feather** (the sources are in `sources/feather-*.svg`):

| icon | how it was derived |
|---|---|
| `github` | Feather's octocat, in **two strokes**: the head near-uniform, the tail tapering to its tip |
| `copy-link` | Feather's `link` at 100 % + a plus badge at the bottom-right |
| `code` | Feather's `code`, verbatim — two chevrons |
| `terminal` | Feather's `terminal`, verbatim — a chevron and a prompt line |
| `external-link` | Feather's `external-link`, verbatim — a box with an arrow leaving it |
| `coffee` | Feather's cup, re-cut and re-stroked — see [the coffee](#the-coffee) |

The `d` of each one is extracted from the SVG by `feather_to_d.py`, not typed by
hand: a mistyped arc flag turns into a spike, and there is no way to see it in the
source.

### The `rectangle-golden` is retired

`rectangle-golden` was in the base set, but it is **no longer part of this set** — it is
replaced by `rectangle-rounded`. The base set keeps its own golden rectangle as the skill's
reference.

The golden one failed on its own terms: at a 90° corner fillet it reads
`min curvature R/(w/2) ≈ 0.96` — the offset chains overlap at the corner. The corrected
rectangle is not that construction any more; it is the supplied drawing, so the reading
does not apply.

So the two folders now differ on **two** icons — `rectangle-golden` (retired) and `square`
(yours, not the pipeline's) — and share the other **11** byte for byte. Say the word and the
base set is synced too.

## The heart

The heart now uses the **same cut recipe as the search**:

```json
"cut_closed": true,
"cut_gap": 1.6,
"cut_strategy": "perpendicular_to_prev",
"cut_chamfer_fillet": false,
"cut_at": "start",
"cut_right_angle_gap": 1.6
```

`perpendicular_to_prev` retracts each arm of the bottom cusp along its own direction, so the
point survives and the opening reads as two clean strokes. `bisector` (what the heart used to
ship with) splits the two ends **radially** instead, which at a cusp pushes one end past the
outline and leaves the tip looking blunt.

The change was made in the **base set** too (`~/Documents/mmagdiel/Icons/pencil-icons/`), because the
heart is the reference icon of the skill — so both folders ship the same heart, byte for byte.

### The cleft is rounded in the source

The heart's source used to meet two lobe arcs at a hard cusp, `(12, 8.4)`, with the tangent
reversing. The engine fillets corners, and the fillet length is capped by the length of the
*straight run* next to the vertex — next to an arc there is no straight run, so the fillet
collapsed to a couple of hundredths of a unit. The turn became a hairpin whose inner offset
folded over itself, and the leftover of that fold is the little nick that showed up in the notch.

It was worse than a cosmetic flaw: **the nick was a lottery**. `cut_gap` 1.6 / 1.8 / 2.0 crossed
with `curvature_safety` 1.25 / 1.5 / 1.6 / 1.9 gave a different notch each time — some with a
nick, some without — and the validator's verdict flipped with it, on a shape that had not changed.

Rounding the cleft with a 0.4-unit arc removes the corner, so there is nothing left for the
fillet to collapse on:

```
before:  M12 21s-7-4.5-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 11c0 5.5-7 10-7 10z
after:   M12 21s-7-4.5-7-10A4 4 0 0 1 11.7 8.0597A0.4 0.4 0 0 0 12.3 8.0597A4 4 0 0 1 19 11c0 5.5-7 10-7 10z
```

The result: the notch is a **clean pencil point** instead of a flat-bottomed V, the inner offset
never folds, and all 36 parameter combinations render the same and pass. The shape barely moves
— 3.2% of the inked pixels — because the two lobe arcs are only shortened by 1.7 degrees each.

`cut_gap = 1.6` still ships, unchanged.

## The mail

The body is **the supplied rectangle, used exactly as it was sent** — same path, same
transform, same look. Only the flap is ours.

The flap is the base set's `chevron` (`M 6 15 L 12 9 L 18 15`, pointing up) **rendered and
then mirrored vertically**. The shape is exactly the base chevron turned over: same arms,
same 45° apex angle, same length. The **taper is flipped** — the thick end is on the right.
That is not a drawing decision, it is arithmetic: the rectangle's top border is not uniform.
Measured on the render, it runs from **0.375 u** thick at the left (just past the cut) to
**0.751 u** at the right, because the stroke tapers along the whole loop:

```
x =  4     6     8    10    12    14    16    18    20
     0.375 0.469 0.516 0.563 0.610 0.633 0.680 0.727 0.751   (u)
```

The thick end's round cap has radius `w_end / 2 = 0.59`. A cap of 1.18 u across **cannot
fit inside a border that is 0.73 u thick** — the geometry does not allow it. So the foot
has to sit low enough that the cap stays within the border's outer edge, and that is
only possible on the **thick** side. The mirror puts the heavy arm there (thin left, thick
right) without deforming the V.

### Why the flap is not simply re-stroked

This is the interesting part. The first attempt drew the flap from the source
`M 6 6.163 L 12 12.163 L 18 6.163` and let the pipeline stroke it. The V came out with a
**kink at the apex** — a flat shelf and a step, exactly like a bad corner. The base
`chevron` has no such kink. The difference is the **wobble**:

```
                    iterations   samples relaxed   min R/r
pico  (the chevron)        9              24        1.166
valley (the same, flipped) 24              27        1.002
```

The wobble is a 2.3-wave sinusoid applied to the centreline **after** the fillet, so it
perturbs the filleted corner instead of being smoothed by it. Whether that hurts depends on
the direction the stroke travels: the same V, traversed the other way round
(`M 18 9 L 12 15 L 6 9`), is clean again — 9 iterations, same as the peak. The engine is
not mirror-symmetric, and a "valley" that happens to be traversed the unlucky way lands on
the wrong side of the wobble and needs 24 iterations of curvature relaxation to recover.
That is what the kink was.

**The fix is to not re-stroke it at all.** The flap is the base chevron's *rendered
silhouette*, mirrored. Whatever the wobble did to the chevron's corner, the mirror carries
it over unchanged — and the chevron's corner is clean.

### Two things the mirror breaks, and how they are fixed

**The winding direction.** A mirror reverses the orientation of a contour. With the
`non-zero` fill rule, two contours with **opposite** orientations cancel where they
overlap (winding `+1` and `−1` sum to `0`), and that overlap turns **white**. The first
mirrored version opened a round bite exactly where the flap met the border. The fix is to
reverse the path after mirroring — `reverse_subpath()` in the assembler does that, flipping
the arcs' `sweep` as well.

**The height.** The wobble moves the chevron's end point, so the foot does not land where
the arithmetic says. The flap is therefore anchored by **geometry, not by a number**: the
top of its cap is aligned with the rectangle's outer edge *at the x where the cap lands*
(the top border is not flat — it slopes from 5.75 u on the left to 5.57 u on the right, so
the global minimum is not the right reference). The cap ends up flush: it neither pokes
above the silhouette nor leaves the arm hanging.

### Why the previous version looked deformed

The first fix tilted the flap ~4° so the heavy end could duck under the border. It solved
the poke, but a V whose two feet sit at different heights is not a V anymore — it reads
as a mistake, and the right arm ended up floating free of the top edge. Dropping the
flap so **both** feet sit at the same height fixes the silhouette *and* keeps the symmetry.
The tilt is gone.

The general rule this falls under: the **thick** end decides where the silhouette breaks,
and a stroke that ends on another stroke's edge pokes past it unless it is tucked inside
the band.

### Why the body is not a pipeline rectangle any more

The first attempt drew the body from the pipeline as a rounded rectangle. It was close,
but not the same drawing: the corner was a blob (the pipeline's fillet ate the arc), and
the whole thing read as "a rectangle that the pipeline drew" rather than as *the* rectangle.

Re-deriving it could not reproduce the supplied file either — an IoU search over
arc-vs-cubic corners × radius {0.8 … 2.0} × wobble {0, 0.05} plateaued at **0.844**, and
the cubics never went past ~0.58. So the rectangle is now an **asset**: the supplied path,
carried through unchanged, with only the viewBox and the canvas fit fixed.

## The rectangle, used verbatim

Four of the 31 icons do not come out of the stroke pipeline. `rectangle-rounded`,
`square`, `search` and `mail` are **finished SVGs** that the build copies in as-is:

```json
{ "name": "rectangle-rounded", "prebuilt": "assets/rectangle-rounded.svg" }
{ "name": "square",            "prebuilt": "assets/square.svg" }
{ "name": "search",            "prebuilt": "assets/search.svg" }
{ "name": "mail",              "prebuilt": "assets/mail.svg" }
```

`build_icon_set.py` copies the referenced file into `svg/<name>.svg` verbatim, records
`"prebuilt": "<path>"` in `manifest.json`, and skips the geometry analysis for it.

**Why:** a pre-baked outline is not a stroke. Re-stroking it would re-derive the whole
thing and change it — the fillet, the width profile and the corner are already decided in
the supplied file, and that is exactly what should be preserved. The build's job is to
place it, not to redraw it.

The assembly lives in `assemble_prebuilt.py` (one level up). It:

1. reads the cleaned file (`*-corregido.svg` — no transform, no metadata, viewBox tight to
   the ink) and scales it into the 24-unit space, to the long side that icon occupies in
   the set;
2. draws the flap by rendering the base `chevron` and **mirroring** it (see
   [the mail](#the-mail));
3. fits everything to the 1024×1024 canvas with the pipeline's own rule, and writes the
   masters.

`assets/source-24.json` keeps the assembled paths in the 24-unit space, so
`source-d.json` stays in **one unit for every icon**. For these four, the value is the
final geometry rather than a recipe to re-stroke.

### The validator flags these four — and that is expected

All four report `non-canonical structure: ... Expected two dense offset chains separated
by cap arcs.`

That check looks for the **signature of a pipeline output**: two dense offset chains (the
two sides of a stroke) separated by cap arcs. The supplied drawings are filled outlines —
one closed band, already expanded — so they have no offset chains to find. The check is
answering a different question than the one being asked, and it is reading the *shape* of
the file, not a defect in the drawing.

The `mail` flap, which **is** pipeline output, passes every geometry check; only the
rectangle subpath is flagged.

## The square

Your drawing, cleaned and **squared**. The export came out of Inkscape with a
transform matrix whose x and y scales are different (`0.0755577` against
`0.07398388`), and that anisotropy stays baked into the path: the ink came out
**14.978 × 14.513 u** — 3.1 % taller than wide, so a square read as a rectangle.

The correction stretches **only the y axis**, around the vertical centre of the ink,
so the ink is exactly 120 × 120 and the viewBox is `0 0 120 120`:

```
antes:      viewBox 0 0 120 116.273      tinta 14.978 x 14.513 u   (h/w 0.96894)
despues:   viewBox 0 0 120 120          tinta 14.978 x 14.978 u   (h/w 1.00000)
```

Two things worth knowing if you do this again:

- **A square viewBox does not make a square.** Making the viewBox square while the
  ink stays rectangular just gives you a rectangle with a tighter top and bottom
  margin. The ink itself has to be stretched.
- The 3.1 % is not all the export's fault: 2.1 % is the matrix and the remaining
  1 % is the shape as you drew it. The correction absorbs both, because the
  instruction is "it is a square, it must be square".

The path itself is untouched otherwise — no re-derivation, no re-stroking.

## The search

The magnifier is **your drawing**, cleaned and used as-is — it replaces the one the
pipeline built.

`search-corregido.svg` (one level up) is the supplied file with the Inkscape page and its
metadata removed:

```
before:  width="210mm"  height="297mm"  viewBox="0 0 210 297"
         + <sodipodi:namedview>, <defs>, inkscape:* , sodipodi:*, el comentario
         de cabecera y el path con un transform encima

after:   width="120"  height="118.067"  viewBox="0 0 120 118.067"
         un solo <path>, sin transform, con la tinta empezando en (0,0)
```

**The path is untouched** — only the wrapper. The transform is *baked into* the path
coordinates, not dropped: the matrix is what gives the drawing its shape, and applying it
is the only way to keep it. `clean_svg.py` does that, and it is the same script that
produced the corrected rectangle and square, so the three files are consistent.

The master lands at 16.950 u of long side — the same footprint the pipeline's magnifier
occupied, so it weighs the same as the rest of the set.

### What the pipeline version used to be

For the record, the version before this one was drawn by the pipeline: a lens ring drawn
with four quarter-circle **arcs** and cut with `perpendicular_to_prev` at `cut_gap = 1.6`,
plus a straight handle. Two details of that construction are worth keeping in the skill,
even though the drawing they produced is gone:

- **A ring's cut is not a corner's cut.** The bisector (the heart's recipe) is *radial* on
  a ring, so one end goes 0.77 inside and the other 0.78 outside — that is the bump.
  `perpendicular_to_prev` retracts both ends *along* the ring, so the only new thing is
  the white space between them. The two axes are perpendicular, not opposite: mixing them
  composes, it does not cancel.
- **An arc does not survive a cut.** Moving the endpoint re-derives a different circle, so
  the two arcs next to the cut land at r = 5.26 instead of 6.00 — the ring pinches inward
  exactly where it opens. Cubics (`C 16.086 7.600 16.086 11.400 …`) keep the ring
  perfectly round but lose that pinch. The pinch was kept on purpose: it is the looseness
  the eye reads as "drawn by hand".

The general rule that came out of it: **a geometric gap can never read as a cut**, because
the round caps eat it. The visible opening is `cut_gap − w_end`, and the floor is about
`1.2 × w_end` (1.42 at `w_end = 1.18`). Below the floor the two caps bridge the gap and
the cut silently stops existing — the icon renders as an unbroken line and **nothing
errors**.


## The linkedin dot

The real mark's dot is a 1.4-radius circle. At `w_end = 1.18` the stroke is 84% of that
radius — the dot fills in and the validator reports four failures. Drawing the dot as a
**short stroke** instead (`M 4.7 4.3 L 5.3 4.3`) gives a dot that reads correctly and passes.
A filled dot is not available in this style: everything is a stroke.

## The github

Feather's octocat, in **two strokes**: the head + body near-uniform (`w 0.82 → 1.0`) and the
tail tapering to its tip (`w 0.40 → 0.80`). One gesture cannot carry both — a single taper
along the head makes the head thin at the top and fat at the neck, and it stops reading as a
closed shape. The spec uses the `strokes` key, one entry per gesture:

```json
{ "name": "github",
  "strokes": [
    { "d": "<head>", "w_start": 0.82, "w_end": 1.0, "wobble": 0.07 },
    { "d": "M 9 19 C 4 20.5 4 16.5 2 16", "w_start": 0.40, "w_end": 0.80,
      "wobble": 0.05 }
  ] }
```

### Its corners are rounded IN THE SOURCE

Feather's path is full of corners that the engine **cannot** fillet. The engine caps the
fillet length by the length of the *straight* run next to the vertex
(`fl = min(Li_full, Lo_full, w_end * per_w) * 0.5`), and next to an arc or a cubic there is
no straight run — the walk-back stops after two samples. The fillet collapses to a hundredth
of a unit, the turn becomes a hairpin, the inner offset folds over itself and the outer
offset grows a **spike**. The first version of this icon had a visible thorn at the neck.

The fix is not a parameter: it is to take the corner away from the engine. Each sharp junction
is replaced by a **cubic fillet, tangent-continuous with both sides** — the engine then has
no corner to fillet and the offset never folds.

| corner | turn | how |
|---|---|---|
| both cheek notches (arc + cubic) | 127° and 70° | cubic fillet, radius 1.0 |
| both "shoulders" (arc + arc) | 9° | cubic fillet, radius 0.8 |
| both ear bases (cubic + arc) | 49° | cubic fillet, radius 0.9 |

The tooling is `fillet_source.py`, in the skill's `scripts/` folder
(`~/.minimax/skills/pencil-icon-style/scripts/`). It truncates each side **on its own
curve** — an arc keeps its circle, a cubic is split with de Casteljau — and joins them with a
Hermite cubic whose tangents are the *actual* tangents of the two curves at the cut points.

One formula matters and is easy to get backwards: the distance from the vertex to the
tangency point is **`R * tan(θ/2)`**, not `R / tan(θ/2)`. With the inverted formula, any
turn over 90° puts the tangency points too close to the vertex: the chord comes out short,
the cubic loops back on itself and you get a curl instead of a rounding.

The result passes the validator, and the stroke could then be widened from 0.76 to 1.0 —
the ear bases were what held it back.

## The copy-link

Feather's `link` at 100 % plus a **plus badge** at the bottom-right, in the free corner of
the diagonal chain. The alternatives were worse: `link` alone does not say "copy", and
`link-2` reads as two brackets. The badge is the standard "add link" construction.

## The coffee

The last of the Feather batch, and the one that took the most work. It is four strokes:

| stroke | weight | what it is |
|---|---|---|
| the cup | `0.32 → 1.18` | Feather's cup, **cut open** at the top-left corner |
| the handle | `0.32 → 1.18` | Feather's handle, trimmed so it stops at the cup's wall |
| two steam lines | `0.20 → 0.38` | two thin wavy lines instead of Feather's three dashes |

### Why the cup is cut

A closed loop with a strong taper **always shows its seam**: the thick end cap and the
thin start land on the same point, so one side of the seam is a lump and the other is a
hairline. The first version had a visible black knob at the bottom-left of the cup and a
thread-thin wall on the left.

The set already has the answer, and it is the same answer the `square` and the `heart`
use: **cut the loop open** with `cut_closed` + `perpendicular_to_prev` + `cut_at: "start"`.
The opening lands on the corner where the stroke enters and leaves, and the pencil reads
as having been lifted there. Same recipe, same look as the rest of the set.

### Why the steam is two wavy lines and not three dashes

Feather's steam is three straight 3-unit dashes. A 3-unit stroke with the base cone
(`0.32 → 1.18`) is a **teardrop**, so all three rendered as drops of water. Two thin
wavy lines (`w 0.20 → 0.38`) read as steam and do not fill in.

### Why the handle is trimmed

The handle's thick end is a round cap of radius `w_end / 2 = 0.59 u`. Ending it exactly on
the cup's wall (x = 18) pushed that cap **into the cup's interior** — a black blob on the
right side of the cup. Ending it at x = 18.6 puts the cap's left edge exactly on the wall,
so it merges with the wall's own ink instead of sitting on top of it.

### Two engine bugs the coffee exposed

The coffee was the icon that broke, and it broke for reasons that had nothing to do with
the coffee. All three are fixed in the skill.

**1. `build_icon_multi` did not compensate the sample density for the scale.**
`strict_per_unit` is *samples per unit of length*. `build_icon` divides it by the fit
factor `k` before re-stroking the scaled geometry, so the sample count is the same at
every canvas size. `build_icon_multi` did not — so a multi-stroke icon got **k times as
many samples** at 1024 than at 256. The curvature limiter works *per sample* (a halo
measured in samples, a fixed iteration budget), so the same shape relaxed differently at
different resolutions: the cup passed at 24 and at 256 and broke at 1024, with the
limiter hitting its 400-iteration ceiling and leaving a hairpin.

**2. `build_icon_multi` did not scale the cut gaps either.**
`cut_gap` and `cut_right_angle_gap` are measured in the source's units, so they have to
grow with the geometry — `build_icon` multiplies them by `k`. Left unscaled, the opening
shrank by `k` and the "cut" degenerated into a nick: the engine's own advice reported
the opening as **0.03 × w_end** and asked for 0.10. That warning was the tell — the
advice was right and the builder was wrong. With the fix the corner opens properly, and
the cup reads exactly like the base set's `square`.

**3. A perfect semicircle could collapse into a straight line.**
The handle's arc is `a 4 4 0 0 1 0 8` — a chord of exactly `2r`, a semicircle. After the
fit scales and rounds the coordinates to two decimals, `lam` (the W3C radius factor) came
out as `1.0000000000000002` instead of `1.0` — **one ULP** over. That triggers the W3C
radius scaling, and the numerator of the centre formula then evaluates to `-2.4e-7`
instead of `0`, because the two products round differently. The parser read that as "this
arc is impossible" and returned the **chord**: the handle came out as a vertical line,
and a quarter of the drawing silently disappeared.

The fix is in `source_path.py`: after the radius scaling, that numerator is mathematically
zero (the scaled radii span the chord exactly), so a residue that is negligible against
`rx²ry²` is treated as zero. A genuinely impossible arc still returns the chord.

All three fixes leave the **base set byte-identical** (13/13) — the base set is built with
`build_icon`, the single-stroke path, which already had the first and the second.

### It is stable, not lucky

`cut_gap` {1.4, 1.6, 1.8} × `curvature_safety` {1.15, 1.25, 1.4} × `wobble_phase`
{0.5, 0.7, 0.9} — **27 combinations, all pass**, and the inked bounding box moves by at
most **0.5 px out of 860** (0.06 %). The shape does not depend on where the samples land.

## Known validator artifacts

**27 of 31 pass.** The four that do not are all the same thing:

- **`rectangle-rounded`**, **`square`**, **`search`** and **`mail`** — `non-canonical
  structure`, because they are pre-baked outlines rather than pipeline output. Explained in
  [the rectangle, used verbatim](#the-rectangle-used-verbatim). Not a visual defect: the
  drawing is the one that was supplied.

The `heart` used to be on this list and is not any more. The flag was `width DECREASES`, at
the **top cleft** between the lobes, and it was an artifact of two bugs that cancelled out:
the outer and inner offset chains desynchronised by one sample at the cusp, and the check
paired them **by index** instead of by station. Both are fixed — the chains are now aligned
before measuring, the tolerance is relative instead of 0.02 px, and the cleft is rounded in the
source so the desync never happens. See [the heart](#the-heart).

The `rectangle-golden` artifact that used to be in this list (`min curvature R/(w/2) ≈ 0.96`
at a 90° corner fillet) is gone with the icon — the corrected rectangle is a different
construction, and `square`, the same shape at a different aspect ratio, passes at every
size.

The `github` was on this list too, and is not any more. It read `min curvature R/(w/2) = 0.35`
— the folds described in [the github](#the-github). The corners are now rounded in the
source, so the offset has nothing to fold.

## Not in this set

Nothing that was asked for is missing any more. The set is complete: the 9 requested
icons (`search`, `arrow-left`, `arrow-right`, `arrow-down`, `arrow-up-right`,
`copy-link`, `github`, `linkedin`, `mail`) plus 22 more that came with them, were
derived from the base set, or came from Feather.

**Left out on purpose**, out of the 8 Feather sources:

- `linkedin` — Feather's version **fails**: its dot is a `<circle>`, which fills in
  at this weight. Ours is a short stroke instead. See
  [the linkedin dot](#the-linkedin-dot).
- `link` — redundant next to `copy-link`, which already *is* a link plus a badge.
- `link-2` — it reads as two brackets, not as a link.

## Verifying

```bash
cd ~/Documents/mmagdiel/Icons/pencil-icons-blog/blog
python3 - <<'EOF'
import sys, glob; sys.path.insert(0, "$HOME/.minimax/skills/pencil-icon-style/scripts")
from verify_icon import check
for f in sorted(glob.glob("svg/*.svg")):
    print(f, "PASS" if check(f, size=1024) == 0 else "FAIL")
EOF
```

`verify_icon.check()` defaults to `size=256`; these masters are 1024, so pass `size=1024` or
the viewBox check fails for the wrong reason.

## Rebuilding

Three steps — the cleaned sources first, then the prebuilt assets, then the build:

```bash
cd ~/Documents/mmagdiel/Icons/pencil-icons-blog
python3 clean_svg.py               # sources/*.svg -> *-corregido.svg (limpios)

python3 assemble_prebuilt.py       # -> assets/*.svg + assets/source-24.json

python3 ~/.minimax/skills/pencil-icon-style/scripts/build_icon_set.py \
  --spec blog-spec.json --out ./blog

python3 _scratch/refresh_blog.py      # -> blog/source-d.json + blog/contact-sheet.png
```

`build_icon_set.py` writes neither `source-d.json` nor `contact-sheet.png` — they are
regenerated afterwards.

**Use `/opt/homebrew/bin/python3`.** The system `python3` is 3.8 and has no PIL, which the
refresh step needs.

The `d` of the five Feather icons was extracted with `feather_to_d.py`, not typed:

```bash
python3 feather_to_d.py sources/feather-code.svg     # prints one d per element
```

The elements come out one per line; in `blog-spec.json` they are joined with a space,
which is a valid multi-subpath `d`.

### The rotated family

The six rotated icons are not hand-written: their `d` comes from rotating an existing
source path around the canvas centre (12, 12).

```bash
python3 _scratch/rot_icon.py     # prints the 6 entries to paste into blog-spec.json
```

The rotation is applied to the **source**, and the pipeline re-strokes it — so the taper
travels with the shape. In SVG coordinates `y` points down, so the standard rotation
matrix with `y` down turns the shape **clockwise** on screen; `rot_icon.py` takes the
angle in visual degrees and gets this right for you.
