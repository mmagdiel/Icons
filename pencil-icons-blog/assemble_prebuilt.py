#!/usr/bin/env python3
"""Ensambla los iconos que NO salen del pipeline de trazos.

    assets/rectangle-rounded.svg   el rectángulo corregido, verbatim
    assets/square.svg              el cuadrado corregido por el usuario, verbatim
    assets/mail.svg                el rectángulo + la solapa
    assets/source-24.json          las rutas en unidades de 24

Reglas del juego:

* Un asset externo es un ASSET, no una fuente. Se copia tal cual — su path,
  su transform, su aspecto. Re-derivarlo no lo reproduce.
* La solapa del sobre es el CHEVRON BASE ya renderizado, espejado vertical.
  No se vuelve a trazar: el motor de trazos no es simétrico bajo espejo (una
  "valley" degrada la esquina) y el espejo conserva la esquina limpia del
  chevron original.
* Los masters quedan en 1024x1024 con el ajuste del set (la tinta ocupa 84%
  del lado mayor y queda centrada), igual que los que produce la skill.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
sys.path.insert(0, os.path.expanduser("~/.minimax/skills/pencil-icon-style/scripts"))
from pencil_stroke import stroke_path  # noqa: E402
from svgkit import (  # noqa: E402
    emit, fit, mirror_y, parse_path, path_bbox, path_points,
    reverse_subpath, translate, write_master,
)

MASTER = 1024
K24 = 1024.0 / 24.0
PADDING = 0.08

# El lado mayor de la tinta de cada asset externo, en unidades de 24. Es lo
# que hace que un icono pese lo mismo que el resto del set:
#   * el rectangulo, su tamaño natural (20.175 x 12.870)
#   * el cuadrado, el del cuadrado BASE del set (14.9777)
#   * la lupa, el de la lupa del pipeline (16.950)
RECT_LONG_SIDE = 20.175
SQUARE_BASE_LONG_SIDE = 14.9777
SEARCH_LONG_SIDE = 16.950

W_START, W_END = 0.32, 1.18
FILLET_PER_W, FILLET_SAMPLES, TRIM_EXTRA = 2.0, 80, 0.40

# La solapa: el chevron base (punta ARRIBA) ya renderizado, espejado.
#
# El cono de grosor va INVERTIDO respecto de la rotacion, y eso es
# aritmetica, no gusto: el borde superior del rectangulo no es uniforme —
# va de 0.375 u a la izquierda hasta 0.751 u a la derecha. La tapa del
# extremo grueso mide 1.18 u de diametro y NO cabe en una banda de 0.73.
# El extremo grueso tiene que caer del lado ancho, y el espejo lo pone ahi
# (fino a la izquierda, grueso a la derecha) sin deformar la V.
#
# Y_FOOT se mide desde el borde exterior del rectangulo: la tapa del extremo
# grueso tiene que quedar JUSTO dentro, sin asomar.
CHEV_BASE = "M 6 15 L 12 9 L 18 15"      # punta arriba, el chevron del set base
Y_FOOT = 6.163                          # donde cae el pie de la solapa
MIRROR_AXIS = (15.0 + Y_FOOT) / 2.0     # el pie original esta en y=15

# ---------------------------------------------------------------------------
# carga de un asset externo
# ---------------------------------------------------------------------------
def load_clean(filename, long_side, center=True):
    """Lee un SVG LIMPIO y devuelve su ruta en unidades de 24.

    Los archivos corregidos (`*-corregido.svg`) ya vienen sin transform ni
    metadata de Inkscape, con el viewBox justo a la tinta (ver clean_svg.py).
    Solo falta llevar esa tinta al espacio de 24 y escalarla al lado mayor
    pedido, para que el icon pese lo mismo que el resto del set.
    """
    raw = open(os.path.join(HERE, filename), encoding="utf-8").read()
    d = re.search(r'\sd="([^"]+)"', raw, re.S).group(1)
    cmds = parse_path(d)
    bb = path_bbox(cmds)
    k = long_side / max(bb[2] - bb[0], bb[3] - bb[1])
    cmds = [(c, [] if c == "Z" else [(x * k, y * k) for x, y in ps])
            for c, ps in cmds]
    pts = path_points(cmds)
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    if center:
        dx = 12.0 - (x0 + x1) / 2
        dy = 12.0 - (y0 + y1) / 2
        cmds = [(c, [] if c == "Z" else [(x + dx, y + dy) for x, y in ps])
                for c, ps in cmds]
        pts = path_points(cmds)
        x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
        y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    print(f"{filename:26s} tinta {x1-x0:.3f} x {y1-y0:.3f} u  (x{k:.4f})")
    return cmds, pts


# ---------------------------------------------------------------------------
# 1. el rectángulo externo -> contorno en unidades de 24
# ---------------------------------------------------------------------------
rect24, RECT_PTS = load_clean("rect-corregido.svg", RECT_LONG_SIDE)

# ---------------------------------------------------------------------------
# 2. el cuadrado externo -> contorno en unidades de 24
#    (se normaliza al lado mayor del cuadrado BASE para que pese lo mismo
#    en el set)
# ---------------------------------------------------------------------------
square24, SQUARE_PTS = load_clean("square-corregido.svg", SQUARE_BASE_LONG_SIDE)

# ---------------------------------------------------------------------------
# 2b. la lupa externa -> contorno en unidades de 24
#     (el mismo criterio: el lado mayor que ocupa la lupa del pipeline)
# ---------------------------------------------------------------------------
search24, SEARCH_PTS = load_clean("search-corregido.svg", SEARCH_LONG_SIDE)

# ---------------------------------------------------------------------------
# 3. la solapa: el chevron base YA RENDERIZADO, espejado
# ---------------------------------------------------------------------------
chev_d, _chev_rep = stroke_path(CHEV_BASE, w_start=W_START, w_end=W_END,
                                 fillet_per_w=FILLET_PER_W,
                                 fillet_samples=FILLET_SAMPLES,
                                 trim_extra=TRIM_EXTRA)
flap24 = mirror_y(parse_path(chev_d), MIRROR_AXIS)
# el espejo invierte la orientacion del contorno: hay que devolverla, o el
# solape con el borde se cancela (non-zero: +1 y -1 = 0 -> blanco)
flap24 = reverse_subpath(flap24)

# El wobble del chevron base desplaza su punto final, asi que el pie NO cae
# exactamente donde dice la cuenta. Se ancla por GEOMETRIA: el tope de la
# tapa de la solapa tiene que quedar en el BORDE EXTERIOR del rectangulo, en
# el punto exacto donde cae la tapa (no en el minimo global de la tinta: el
# borde superior no es plano y el minimo esta mas a la derecha).
def top_edge_at(pts, x, tol=0.32):
    """El borde exterior (el de arriba) del rectangulo en la abscisa x.

    El contorno del rectangulo son dos cadenas (exterior e interior) mas el
    borde de abajo, y los puntos van espaciados ~0.28 u, asi que:
      1. se toma solo la mitad de arriba, para no confundir con el borde
         inferior;
      2. la ventana en x es +-0.32, mas ancha que el paso, para que siempre
         caiga algun punto.
    """
    ys_all = [p[1] for p in pts]
    mid = (min(ys_all) + max(ys_all)) / 2.0
    upper = [p for p in pts if p[1] < mid]
    ys = [p[1] for p in upper if abs(p[0] - x) <= tol]
    if not ys:
        ys = [p[1] for p in upper if p[0] <= x]
        if not ys:
            return min(ys_all)
        return max(ys)
    return min(ys)


def cap_center(cmds):
    """Centro de la tapa GRUESA (el arco de radio w_end/2)."""
    for c, ps in cmds:
        if c != "A":
            continue
        rx, ry, rot, laf, sw, x, y = ps[0]
        if abs(rx - W_END / 2.0) > 1e-6:
            continue
        i = cmds.index((c, ps))
        p0 = cmds[i - 1][1][-1]
        return ((p0[0] + x) / 2.0, (p0[1] + y) / 2.0)
    return None


_cc = cap_center(flap24)
_cap_x = _cc[0] if _cc else 18.0
_anchor = top_edge_at(RECT_PTS, _cap_x)
_fb = path_bbox(flap24)
flap24 = translate(flap24, 0.0, _anchor - _fb[1])
FLAP_PTS = path_points(flap24)
_fb = path_bbox(flap24)
print(f"solapa: espejo del chevron base (eje y={MIRROR_AXIS:.4f}); "
      f"tapa en x={_cap_x:.2f}, anclada al borde exterior local ({_anchor:.3f}); "
      f"tinta y {_fb[1]:.3f}..{_fb[3]:.3f}")


# ---------------------------------------------------------------------------
# 4. ajuste al canvas, igual que la skill
# ---------------------------------------------------------------------------

os.makedirs(ASSETS, exist_ok=True)

d, k = fit([(rect24, RECT_PTS)])
write_master(os.path.join(ASSETS, "rectangle-rounded.svg"), d)
print(f"assets/rectangle-rounded.svg   k={k:.3f}")

d, k = fit([(square24, SQUARE_PTS)])
write_master(os.path.join(ASSETS, "square.svg"), d)
print(f"assets/square.svg              k={k:.3f}")

d, k = fit([(rect24, RECT_PTS), (flap24, FLAP_PTS)])
write_master(os.path.join(ASSETS, "mail.svg"), d)
print(f"assets/mail.svg                 k={k:.3f}")

d, k = fit([(search24, SEARCH_PTS)])
write_master(os.path.join(ASSETS, "search.svg"), d)
print(f"assets/search.svg               k={k:.3f}")


# ---------------------------------------------------------------------------
# 5. las rutas en unidades de 24, para que source-d.json tenga una sola
#    unidad (los iconos del pipeline usan el espacio de 24)
# ---------------------------------------------------------------------------
src24 = {
    "rectangle-rounded": emit(rect24, 1.0, 0.0, 0.0),
    "square": emit(square24, 1.0, 0.0, 0.0),
    "mail": emit(rect24, 1.0, 0.0, 0.0) + " " + emit(flap24, 1.0, 0.0, 0.0),
    "search": emit(search24, 1.0, 0.0, 0.0),
}
with open(os.path.join(ASSETS, "source-24.json"), "w", encoding="utf-8") as fh:
    json.dump(src24, fh, indent=2, ensure_ascii=False)
    fh.write("\n")
print("assets/source-24.json ->", ", ".join(src24))
