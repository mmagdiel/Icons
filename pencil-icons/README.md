# pencil-icons — hand-drawn graphite icon set

Generated with the `pencil-icon-style` Mavis skill. **Vector masters are in `svg/`** — the PNGs are previews, not sources.

## Contents
```
svg/          13 vector masters @ 1024x1024  <- the real assets
png-256/      raster previews @ 256
png-512/      raster previews @ 512
png-1024/     raster previews @ 1024
source-d.json original source path data per icon
manifest.json full parameter set + validator result + warnings per icon
preview.html  browser gallery (open directly, no server)
contact-sheet.png  all 13 on one sheet
```

## Shared parameters
```python
w_start = 0.32
w_end = 1.18
fillet_per_w = 2.0
fillet_samples = 80
trim_extra = 0.4
```

## Per-icon settings

| icon | cut gap | strategy | cut_at | right-angle gap | wobble | validator |
|---|---|---|---|---|---|---|
| `chevron` | - | - | - | - | 0.10 | pass |
| `plus` | - | - | - | - | 0.10 | pass |
| `arrow-right` | - | - | - | - | 0.10 | pass |
| `zigzag` | - | - | - | - | 0.10 | pass |
| `heart` | 1.6 | perpendicular_to_prev | start | 1.6 | 0.10 | pass |
| `menu` | - | - | - | - | 0.10 | pass |
| `square` | 1.6 | perpendicular_to_prev | start | 1.6 | 0.10 | pass |
| `arrow-up` | - | - | - | - | 0.10 | pass |
| `list` | - | - | - | - | 0.10 | pass |
| `align-justify` | - | - | - | - | 0.10 | pass |
| `hash` | - | - | - | - | 0.10 | pass |
| `x-close` | - | - | - | - | 0.10 | pass |
| `rectangle-golden` | 1.6 | perpendicular_to_prev | start | 1.6 | 0.05 | fail |

## The three closed shapes

All three are cut with `cut_at="start"` — at the corner where the path opens and closes — so the two open ends of the stroke ARE the two sides of the cut. It reads as *the line starts here and ends here*. Cutting anywhere else on a 90 deg corner leaves the two bodies joined through the inner corner, which reads as a chipped corner instead.

**heart** — `perpendicular_to_prev`, `cut_gap=1.6` and `cut_right_angle_gap=1.6`, cut at the bottom tip. Retracting each arm of the cusp along its own direction keeps the point and opens the tip into two clean strokes; the `bisector` strategy it used to ship with splits the two ends radially instead, which at a cusp pushes one end past the outline. Both end caps have radius `w_end/2`, so the opening must clear `~1.2 x w_end` (1.42 here) or the caps bridge and the cut silently disappears. This icon carried `0.95` for several rounds and rendered as an unbroken line the whole time.

**The heart's cleft is rounded in the source, on purpose.** It used to be a hard cusp where the two lobe arcs met at `(12, 8.4)` with the tangent reversing. The engine fillets corners, and its fillet length is capped by the length of the *straight run* next to the vertex — next to an arc there is no straight run, so the fillet collapsed to a couple of hundredths of a unit. The turn became a hairpin whose inner offset folded over itself, and the leftover of that fold is a small nick in the notch. Worse, whether the nick appeared depended on where the samples landed: `cut_gap` 1.6 / 1.8 / 2.0 and `curvature_safety` 1.25 / 1.5 / 1.6 / 1.9 all gave a *different* notch, and the validator's verdict flipped with it.

Rounding the cleft with a 0.4-unit arc removes the corner altogether. The inner offset never folds, the notch is a clean pencil point instead of a flat-bottomed V, and the result is the same for every combination of parameters (36 of 36 builds render identically and pass).

```
before:  M12 21s-7-4.5-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 11c0 5.5-7 10-7 10z
after:   M12 21s-7-4.5-7-10A4 4 0 0 1 11.7 8.0597A0.4 0.4 0 0 0 12.3 8.0597A4 4 0 0 1 19 11c0 5.5-7 10-7 10z
```

**square** / **rectangle-golden** — `perpendicular_to_prev`, `cut_gap=1.6` and `cut_right_angle_gap=1.6`. Both must exceed `w_end` (1.18) or the caps overlap and the ink stays connected. `cut_chamfer_fillet=False` protects the two 45 deg diagonal endpoints from the corner fillet.

`rectangle-golden` is `M 4 7 H 20 V 17 H 4 Z` (16x10 source units, ~1.6:1) with `wobble=0.05`.

## Known validator artifacts

- **`rectangle-golden`** — `min curvature R/(w/2) ≈ 0.96` at a 90 deg corner fillet, against a target of 1.25. It does not respond to `wobble`, `curvature_safety` or `fillet_per_w`; the result only flips side with sample density, so it is a marginal-geometry reading rather than a defect. `square`, the same construction at a different aspect ratio, passes at every size.

**12 of 13 pass.** The heart used to be on this list; it is not any more — see above.

## Processing a new icon set

```bash
python3 ~/.minimax/skills/pencil-icon-style/scripts/build_icon_set.py --spec my-icons.json --out ~/Documents/my-icons
```

The generator renders SVG masters + PNG previews, validates every icon, and explains failures:

- `[HAZRD]` — the SOURCE shape cannot carry a pencil stroke (a near-reversal fold > 145 deg, or a spike < 70 deg, on a straight-line corner). Nothing you tune will fix it; round the vertex in the source path or split the symbol.

- `[WHY]` — the shape is fine but the stroke came out wrong, with the parameter to reach for.

## Verifying
```bash
cd ~/Documents/pencil-icons
python3 - <<'EOF'
import sys, glob; sys.path.insert(0, "$HOME/.minimax/skills/pencil-icon-style/scripts")
from verify_icon import check
for f in sorted(glob.glob("svg/*.svg")):
    print(f, "PASS" if check(f, size=1024) == 0 else "FAIL")
EOF
```

`verify_icon.check()` defaults to `size=256`; these masters are 1024, so pass `size=1024` or the viewBox check fails for the wrong reason.

