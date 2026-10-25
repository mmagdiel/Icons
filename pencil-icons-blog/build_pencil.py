#!/usr/bin/env python3
"""
Convert base icons -> hand-drawn graphite-pencil style (one continuous gesture).

Source set: Ionicons-outline (24x24, filled paths whose `d` is the WALL of a
~2px stroke). Feeding those `d` strings straight to the generator would stroke
the outline and produce a doubled hollow mess, so each mark is re-described
here as a hand-designed CENTERLINE in the same 24-unit space.

Why a `d` string and not a point list: `source_path` classifies segments from
L/H/V as strict (exact slope) and from C/Q/A as curves (full organic wobble).
Emitting straight runs as L and corner arcs as C is what keeps a flat edge
dead flat while the corners breathe — a dense point list would classify
everything as strict and let the full wobble land on the straight runs.

Every centerline below is ONE continuous gesture, thin on entry, thick on exit.
Rule 3 (R >= w/2) means sharp corners belong near the THIN end, where the
tolerance is highest.
"""
import math
import os
import sys

sys.path.insert(0, "/Users/magdielmarquez/.minimax/skills/pencil-icon-style/scripts")
from pencil_stroke import build_icon  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "svg")
os.makedirs(OUT, exist_ok=True)

# --- weight -----------------------------------------------------------------
# The source stroke is ~2.0 units in this 24-space, so w_end reproduces the
# original optical weight and the converted set still reads as one family.
# Rule 3 couples stroke weight to corner radius: R >= curvature_safety*w_end/2,
# and a corner consumes R/tan(phi/2) of each edge. At w_end=1.75 that is a 4.8
# unit bite out of a 14 unit triangle edge -- the apex of the arrow disappears.
# 1.25 keeps the same optical weight as the source outline at UI sizes while
# leaving the corners enough edge to survive.
W_START, W_END = 0.36, 1.25
# ~3% of the line width: enough hand feel, not enough to undulate a flat run.
WOBBLE = 0.035

COMMON = dict(
    w_start=W_START,
    w_end=W_END,
    easing="pencil",
    wobble=WOBBLE,
    wobble_straight=WOBBLE,
    wobble_waves=7.0,
    curvature_safety=1.25,
    # corners are already rounded by hand in centerline_d(); disable the
    # generator's own fillet so the two do not compound
    fillet_min_angle_deg=179.0,
    strict_per_unit=0.8,
    padding_ratio=0.08,
    fill="currentColor",
)


def num(v):
    return f"{v:.3f}".rstrip("0").rstrip(".")


def pt(p):
    return f"{num(p[0])},{num(p[1])}"


# --- centerline construction ------------------------------------------------

def _corner(prev, cur, nxt, radius):
    """Circular fillet at `cur`. Returns (cx, cy, r, a0, a1) or None."""
    v1 = (prev[0] - cur[0], prev[1] - cur[1])
    v2 = (nxt[0] - cur[0], nxt[1] - cur[1])
    l1, l2 = math.hypot(*v1), math.hypot(*v2)
    if l1 < 1e-9 or l2 < 1e-9:
        return None
    u = (v1[0] / l1, v1[1] / l1)
    v = (v2[0] / l2, v2[1] / l2)
    cosphi = max(-1.0, min(1.0, u[0] * v[0] + u[1] * v[1]))
    phi = math.acos(cosphi)
    deg = math.degrees(phi)
    if deg < 3 or deg > 178:                    # straight, or a full reversal
        return None
    half = phi / 2.0
    # tangent length from the corner is R / tan(phi/2); note this is COT, not
    # TAN -- getting that backwards throws the centre far off the mark.
    d = min(radius / math.tan(half), 0.45 * l1, 0.45 * l2)
    r_eff = d * math.tan(half)
    bis = (u[0] + v[0], u[1] + v[1])
    lb = math.hypot(*bis)
    if lb < 1e-9:
        return None
    bis = (bis[0] / lb, bis[1] / lb)
    cx = cur[0] + bis[0] * (r_eff / math.sin(half))
    cy = cur[1] + bis[1] * (r_eff / math.sin(half))
    # tangent points, not just points on the circle: the arc must actually
    # meet both edges, or the straight runs no longer line up with the design
    a0 = math.atan2((cur[1] + u[1] * d) - cy, (cur[0] + u[0] * d) - cx)
    a1 = math.atan2((cur[1] + v[1] * d) - cy, (cur[0] + v[0] * d) - cx)
    da = a1 - a0
    while da > math.pi:
        da -= 2 * math.pi
    while da < -math.pi:
        da += 2 * math.pi
    return cx, cy, r_eff, a0, a0 + da


def centerline_d(points, radius, closed_gap=1.15, close=False):
    """Polyline + explicit corner radii -> a path 'd' with L runs and C arcs.

    `close=True` emits a closed ring (`Z`) instead of opening it here, so the
    generator's own `cut_closed` performs the opening. Prefer that for
    rectangles and squares: `cut_strategy="perpendicular_to_prev"` retracts
    each cut end back along its OWN segment, which keeps a rectilinear shape
    axis-aligned, whereas a hand seam placed at the midpoint of an edge leaves
    a visible lump there.
    """
    pts = [tuple(p) for p in points]
    closed = (len(pts) > 3 and abs(pts[0][0] - pts[-1][0]) < 1e-9
              and abs(pts[0][1] - pts[-1][1]) < 1e-9)
    ring = pts[:-1] if closed else pts
    m = len(ring)

    arcs = []           # (vertex_index, P0, P1, P2, P3)
    for i in range(m):
        if not closed and (i == 0 or i == m - 1):
            continue
        prev = ring[(i - 1) % m]
        cur = ring[i]
        nxt = ring[(i + 1) % m]
        c = _corner(prev, cur, nxt, radius)
        if c is None:
            continue
        cx, cy, r, a0, a1 = c
        da = a1 - a0
        # cubic approximation of a circular arc: k = 4/3 * tan(da/4) * r
        # the * r matters: without it every arc comes out flattened and the
        # corner gets shaved off the mark
        k = (4.0 / 3.0) * math.tan(da / 4.0) * r
        P0 = (cx + r * math.cos(a0), cy + r * math.sin(a0))
        P3 = (cx + r * math.cos(a1), cy + r * math.sin(a1))
        # unit tangent at each end, pointing along the sweep
        t0 = (-math.sin(a0), math.cos(a0))
        if da < 0:
            t0 = (-t0[0], -t0[1])
        t1 = (-math.sin(a1), math.cos(a1))
        if da < 0:
            t1 = (-t1[0], -t1[1])
        P1 = (P0[0] + k * t0[0], P0[1] + k * t0[1])
        P2 = (P3[0] - k * t1[0], P3[1] - k * t1[1])
        arcs.append((i, P0, P1, P2, P3))

    if not arcs:
        return "M " + " L ".join(pt(p) for p in pts)

    order = sorted(arcs, key=lambda a: a[0])
    out = []
    first_in = order[0][1]
    last_out = order[-1][4]

    if closed:
        if close:
            # emit the whole ring shut and let cut_closed perform the opening
            out.append("M " + pt(first_in))
        else:
            # A closed ring traversed from vertex 0 leaves the edge that LEADS
            # INTO vertex 0 undrawn: you start on it and finish on it, but
            # never cross the middle. Put the seam at the midpoint of that
            # straight run so both halves get drawn -- and leave a gap there
            # rather than overlapping. Overlapping puts the thick tail on top
            # of the thin head and reads as a lump at this weight.
            seam = ((last_out[0] + first_in[0]) / 2.0,
                    (last_out[1] + first_in[1]) / 2.0)
            dv = (first_in[0] - last_out[0], first_in[1] - last_out[1])
            dl = math.hypot(*dv) or 1.0
            gap_end = (seam[0] - dv[0] / dl * closed_gap / 2.0,
                       seam[1] - dv[1] / dl * closed_gap / 2.0)
            out.append("M " + pt(seam))
            if abs(first_in[0] - seam[0]) > 1e-6 or abs(first_in[1] - seam[1]) > 1e-6:
                out.append("L " + pt(first_in))
    else:
        # the first edge, from ring[0] to the first arc's tangent-in, was
        # silently dropped before -- that is the shaft of the arrow
        head = ring[0]
        out.append("M " + pt(head))
        if abs(first_in[0] - head[0]) > 1e-6 or abs(first_in[1] - head[1]) > 1e-6:
            out.append("L " + pt(first_in))

    for k, (i, P0, P1, P2, P3) in enumerate(order):
        out.append(f"C {pt(P1)} {pt(P2)} {pt(P3)}")
        if k + 1 < len(order):
            nxt_start = order[k + 1][1]
            if abs(nxt_start[0] - P3[0]) > 1e-6 or abs(nxt_start[1] - P3[1]) > 1e-6:
                out.append("L " + pt(nxt_start))

    if closed:
        if close:
            if abs(first_in[0] - last_out[0]) > 1e-6 or abs(first_in[1] - last_out[1]) > 1e-6:
                out.append("L " + pt(first_in))
            out.append("Z")
        else:
            out.append("L " + pt(gap_end))
    else:
        tail = ring[-1]
        if abs(tail[0] - last_out[0]) > 1e-6 or abs(tail[1] - last_out[1]) > 1e-6:
            out.append("L " + pt(tail))
    return " ".join(out)


def search_d():
    """Magnifier: one loop around the lens, then out the handle.

    The lens is emitted as A commands so the parser treats it as a curve and
    gives it the full organic wobble. Thin entry at the top of the lens; the
    thick tail lands on the lens/handle joint, which is exactly where a hand
    puts pressure when sketching a magnifier.
    """
    cx, cy, r = 10.55, 10.50, 7.05

    def P(deg):
        a = math.radians(deg)
        return cx + r * math.cos(a), cy + r * math.sin(a)

    jx, jy = P(45)
    d = [f"M {pt(P(-90))}"]
    for a0, a1, large in ((-90, 0, 0), (0, 90, 0), (90, 180, 0), (180, 45, 1)):
        d.append(f"A {num(r)},{num(r)} 0 {large} 1 {pt(P(a1))}")
    d.append(f"L 20.70,20.60")
    return " ".join(d)


def strokes(*ds):
    """Join N independent gestures into one path.

    Each subpath tapers independently, thin at its own start and thick at its
    own end, so every stroke gets to declare its own direction. That is what
    lets an icon whose strokes mean different things -- a shaft that points at
    the corner and a head that does not -- carry the right emphasis on each.
    """
    return " ".join(d for d in ds if d)


# --- the set ----------------------------------------------------------------
# Gesture direction follows the symbol: the stroke ENDS thick where the icon
# points, and enters thin on the side it comes from. That means the apex is
# always the LAST vertex of a closed ring, not the first.
#
#   arrow-left   ◁  ring order puts the apex last -> heavy tip points left
#   arrow-right  ▷  apex last -> heavy tip points right
#   arrow-down   ▽  apex last -> heavy tip points down
#
# Winding matters: the counter-clockwise traversal of a ring makes the
# curvature limiter fire ~65 times and it visibly inflates the corners, so
# every ring here is traversed clockwise.

ICONS = [
    ("search", search_d(), {}),
    ("arrow-left",
     centerline_d([(17.45, 4.25), (17.30, 19.75), (5.35, 12.10), (17.45, 4.25)], 1.25), {}),
    ("arrow-right",
     centerline_d([(6.70, 19.70), (6.55, 4.30), (18.65, 11.90), (6.70, 19.70)], 1.25), {}),
    ("arrow-down",
     centerline_d([(4.85, 6.35), (19.15, 6.50), (12.00, 18.60), (4.85, 6.35)], 1.35), {}),
    # Two strokes, because one gesture cannot draw this symbol. The shaft runs
    # tail -> corner and lands THICK on the arrow's point; the head is the
    # original icon's corner bar, which carries the eye to that same corner.
    # Forcing both into one chevron closed the 45-degree barb into a balloon.
    # The shaft stops 1.0 short of the corner so its cap sits INSIDE the head's
    # corner join instead of bulging past it as a dot.
    ("arrow-up-right",
     strokes(centerline_d([(4.60, 19.40), (17.40, 7.55)], 0.9),
             centerline_d([(9.00, 6.55), (18.40, 6.55), (18.40, 16.20)], 0.9)),
     {}),
    # Two strokes: the envelope body and the flap (Rule 4 -- the flap is an
    # enclosed element, it is not reachable from the body in one gesture).
    #
    # On the body's cut: cut_closed + cut_strategy="perpendicular_to_prev" is
    # the rectangle recipe, and it was tried here first. It does keep the ring
    # axis-aligned, but it retracts gap/sqrt(2) back along EACH adjacent
    # segment and joins them with a diagonal -- so cutting at a right angle
    # BEVELS that corner, and a bevelled envelope corner reads as a defect.
    # The hand seam is used instead, with the gap parked on the right edge:
    # the corners stay round, and the opening is invisible because the two caps
    # still overlap at closed_gap=0.5 (visible opening is roughly
    # gap*scale - w_end, so the gap must stay under one stroke width).
    #
    # The flap is anchored INSIDE the body on purpose: ending it on the corner
    # vertex made the thick cap bulge past the top edge as a step.
    ("mail",
     strokes(centerline_d([(19.55, 18.25), (4.45, 18.20), (4.40, 6.55),
                           (19.60, 6.60), (19.55, 18.25)], 1.05, closed_gap=0.5),
             centerline_d([(5.46, 6.55), (12.05, 13.75), (17.90, 7.20)], 1.05)),
     {}),
]


def write(name, d, **over):
    kw = dict(COMMON, **over)
    svg, rep = build_icon(d, **kw)
    # make_svg() returns a whole <svg> document. Nesting it inside our own
    # <svg> puts a second viewBox inside the first, which crops and zooms the
    # mark -- lift out just the <path>.
    body = svg[svg.index("<path"):svg.rindex("</svg>")].strip()
    path = os.path.join(OUT, name + ".svg")
    with open(path, "w") as fh:
        fh.write(
            f'<svg role="img" aria-labelledby="{name}t" viewBox="0 0 256 256" '
            f'xmlns="http://www.w3.org/2000/svg">\n'
            f'<title id="{name}t">{name.replace("-", " ").title()}</title>\n'
            f'{body}\n</svg>\n'
        )
    return path, rep


if __name__ == "__main__":
    for name, d, over in ICONS:
        p, rep = write(name, d, **over)
        print(f"{name:16s} scale={rep['scale']:.2f} samples={rep.get('samples')} "
              f"relaxed={rep.get('samples_relaxed')} -> {os.path.basename(p)}")