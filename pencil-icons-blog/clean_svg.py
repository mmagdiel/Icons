#!/usr/bin/env python3
"""Limpia un export de Inkscape: se lleva el(metadata y deja el viewBox justo.

Inkscape exporta una PAGINA (210x297), no un icono: el viewBox es el de la
hoja, la marca queda en una esquina y el archivo viene con el `namedview`,
los `defs`, los `id`, los `sodipodi:*` y un comentario de cabecera. Eso es
ruido para un asset.

Este script:
  1. lee el path y su matriz de transformacion,
  2. hornea la transformacion dentro del path (una sola subpath limpia),
  3. lo translates para que la tinta empiece en (0,0),
  4. escribe un SVG minimo con el viewBox JUSTO a la tinta y el tamano
     proporcional.

El path NO se modifica: solo se le aplica la matriz que ya traia.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from svgkit import parse_path, path_bbox  # noqa: E402

TARGET_WIDTH = 120.0


def clean(src_path, out_path, title=""):
    raw = open(src_path, encoding="utf-8").read()
    d = re.search(r'\sd="([^"]+)"', raw, re.S).group(1)
    m = re.search(r'transform="matrix\(([^)]+)\)"', raw)
    if m:
        A, B, C, D, E, F = [float(v) for v in m.group(1).split(",")]

        def xf(x, y):
            return (A * x + C * y + E, B * x + D * y + F)
    else:
        def xf(x, y):
            return (x, y)

    cmds = []
    for c, ps in parse_path(d):
        if c == "Z":
            cmds.append(("Z", []))
            continue
        cmds.append((c, [xf(x, y) for x, y in ps]))

    bb = path_bbox(cmds)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    # Se escala para que el lado mayor del viewBox sea TARGET_WIDTH: asi el
    # viewBox queda en unidades sanas (0 0 120 118) y no en milimetros de
    # pagina. La forma no cambia: es una escala uniforme.
    k = TARGET_WIDTH / max(w, h)
    dx, dy = -bb[0] * k, -bb[1] * k
    cmds = [(c, [] if c == "Z" else [(x * k + dx, y * k + dy) for x, y in ps])
            for c, ps in cmds]
    vw, vh = round(TARGET_WIDTH, 3), round(h * k, 3)

    # emitir en absoluto, una sola subpath
    parts = []
    for c, ps in cmds:
        if c == "Z":
            continue
        if c == "M":
            parts.append(f"M {ps[0][0]:.3f} {ps[0][1]:.3f}")
        elif c == "L":
            parts.append(f"L {ps[0][0]:.3f} {ps[0][1]:.3f}")
        elif c == "C":
            nums = " ".join(f"{x:.3f} {y:.3f}" for x, y in ps)
            parts.append(f"C {nums}")
        elif c == "S":
            nums = " ".join(f"{x:.3f} {y:.3f}" for x, y in ps)
            parts.append(f"S {nums}")
        elif c == "Q":
            nums = " ".join(f"{x:.3f} {y:.3f}" for x, y in ps)
            parts.append(f"Q {nums}")
        elif c == "T":
            parts.append(f"T {ps[0][0]:.3f} {ps[0][1]:.3f}")
        elif c == "A":
            rx, ry, rot, laf, sw, x, y = ps[0]
            parts.append(f"A {rx:.3f} {ry:.3f} {rot:.1f} {laf:.0f} {sw:.0f} {x:.3f} {y:.3f}")

    height = round(vh, 3)
    title_line = f"   <!-- {title} -->\n" if title else ""
    out = (
        f'<svg xmlns="http://www.w3.org/2000/svg"\n'
        f'{title_line}'
        f'   width="{TARGET_WIDTH}"\n'
        f'   height="{height}"\n'
        f'   viewBox="0 0 {vw} {vh}">\n'
        f'  <path fill="#000000" d="{" ".join(parts)}"/>\n'
        f'</svg>\n'
    )
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(out)
    print(f"{os.path.basename(out_path):26s} viewBox 0 0 {vw:g} {vh:g}   "
          f"size {TARGET_WIDTH:g} x {height:g}")
    return vw, vh


if __name__ == "__main__":
    SRC = os.path.join(HERE, "sources")
    jobs = [
        ("rect.svg", "rect-corregido.svg", "rectangulo: viewBox y transform horneados"),
        ("square.svg", "square-corregido.svg", "cuadrado: viewBox y transform horneados"),
        ("search.svg", "search-corregido.svg", "lupa: viewBox y transform horneados"),
    ]
    for src, out, title in jobs:
        s = os.path.join(SRC, src)
        if not os.path.exists(s):
            print(f"  (falta {s}, se salta)")
            continue
        clean(s, os.path.join(HERE, out), title)
