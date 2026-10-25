#!/usr/bin/env python3
"""Extract path data from a Feather-style SVG (path / polyline / line /
rect / circle) into a single `d` string per subpath group.

Feather ships every icon as a 24x24 stroke drawing built from several
elements. The stroke engine takes a `d`, so the elements have to be
flattened first. Doing it by hand is where transcription errors creep
in (a mis-typed arc flag turns into a spike), so it is done here.
"""
from __future__ import annotations

import os
import re
import xml.etree.ElementTree as ET

NS = "{http://www.w3.org/2000/svg}"


def _f(v: str) -> str:
    s = f"{float(v):.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def _polyline(points: str) -> str:
    nums = [p for p in re.split(r"[\s,]+", points.strip()) if p]
    pts = list(zip(nums[0::2], nums[1::2]))
    return "M" + " L".join(f"{_f(x)} {_f(y)}" for x, y in pts)


def _line(el) -> str:
    return (f"M{_f(el.get('x1'))} {_f(el.get('y1'))} "
            f"L{_f(el.get('x2'))} {_f(el.get('y2'))}")


def _rect(el) -> str:
    x, y = float(el.get("x")), float(el.get("y"))
    w, h = float(el.get("width")), float(el.get("height"))
    return (f"M{_f(x)} {_f(y)} H{_f(x + w)} V{_f(y + h)} H{_f(x)} Z")


def _circle(el) -> str:
    cx, cy, r = (float(el.get(k)) for k in ("cx", "cy", "r"))
    return (f"M{_f(cx - r)} {_f(cy)} "
            f"A{_f(r)} {_f(r)} 0 1 0 {_f(cx + r)} {_f(cy)} "
            f"A{_f(r)} {_f(r)} 0 1 0 {_f(cx - r)} {_f(cy)} Z")


def extract(svg_path: str) -> list[str]:
    """Return one `d` string per drawn element, in document order."""
    root = ET.parse(svg_path).getroot()
    out: list[str] = []
    for el in root.iter():
        tag = el.tag.replace(NS, "")
        if tag == "path":
            out.append(el.get("d"))
        elif tag == "polyline":
            out.append(_polyline(el.get("points")))
        elif tag == "line":
            out.append(_line(el))
        elif tag == "rect":
            out.append(_rect(el))
        elif tag == "circle":
            out.append(_circle(el))
    return out


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        print(f"--- {os.path.basename(p)}")
        for d in extract(p):
            print(f"    {d}")
