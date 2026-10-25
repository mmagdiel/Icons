#!/usr/bin/env python3
"""Utilidades SVG compartidas por el assembler y el limpiador.

Vive aparte para que `clean_svg.py` y `assemble_prebuilt.py` no se importen
entre si (y para que importar uno no ejecute el otro).
"""
import math
import re

# ---------------------------------------------------------------------------
# parser de path (absoluto y relativo)
# ---------------------------------------------------------------------------
def parse_path(d):
    tok = re.findall(r"[MmLlHhVvCcSsQqTtAaZz]|-?\d*\.?\d+(?:e-?\d+)?", d)
    i = 0
    cur = (0.0, 0.0)
    start = (0.0, 0.0)
    cmd = None
    out = []

    def take(n):
        nonlocal i
        v = []
        for _ in range(n):
            v.append(float(tok[i]))
            i += 1
        return v

    def abs_xy(x, y, rel):
        return (x + cur[0], y + cur[1]) if rel else (x, y)

    # Numero de parametros por juego, por comando. Un comando puede traer
    # VARIOS juegos seguidos sin repetir la letra ("c x1 y1 x2 y2 x y  x1 y1
    # x2 y2 x y" son dos cubicas): el SVG repite el comando implicitamente.
    # Sin esto, el segundo juego se desarma y la forma sale corrupta.
    NPAR = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7}

    while i < len(tok):
        t = tok[i]
        if re.match(r"[A-Za-z]", t):
            cmd = t
            i += 1
            if cmd in "Zz":
                cur = start
                out.append(("Z", []))
                continue
        rel = cmd.islower()
        c = cmd.upper()
        # --- un juego de parametros ---
        if c == "M":
            x, y = take(2)
            cur = abs_xy(x, y, rel)
            start = cur
            out.append(("M", [cur]))
            cmd = "l" if rel else "L"
        elif c == "L":
            x, y = take(2)
            cur = abs_xy(x, y, rel)
            out.append(("L", [cur]))
        elif c == "H":
            x = take(1)[0]
            cur = (x + cur[0], cur[1]) if rel else (x, cur[1])
            out.append(("L", [cur]))
        elif c == "V":
            y = take(1)[0]
            cur = (cur[0], y + cur[1]) if rel else (cur[0], y)
            out.append(("L", [cur]))
        elif c == "C":
            x1, y1, x2, y2, x, y = take(6)
            p1 = abs_xy(x1, y1, rel)
            p2 = abs_xy(x2, y2, rel)
            p3 = abs_xy(x, y, rel)
            out.append(("C", [p1, p2, p3]))
            cur = p3
        elif c == "S":
            x2, y2, x, y = take(4)
            p2 = abs_xy(x2, y2, rel)
            p3 = abs_xy(x, y, rel)
            out.append(("S", [p2, p3]))
            cur = p3
        elif c == "Q":
            x1, y1, x, y = take(4)
            p1 = abs_xy(x1, y1, rel)
            p2 = abs_xy(x, y, rel)
            out.append(("Q", [p1, p2]))
            cur = p2
        elif c == "T":
            x, y = take(2)
            p = abs_xy(x, y, rel)
            out.append(("T", [p]))
            cur = p
        elif c == "A":
            rx, ry, rot, laf, sw, x, y = take(7)
            p = abs_xy(x, y, rel)
            out.append(("A", [(rx, ry, rot, laf, sw, p[0], p[1])]))
            cur = p
        else:
            raise SystemExit(f"comando no soportado: {cmd}")
        # --- repeticion implicita: si sigue un numero, el comando se repite ---
        if i < len(tok) and not re.match(r"[A-Za-z]", tok[i]) and c != "M":
            continue
        if i < len(tok) and not re.match(r"[A-Za-z]", tok[i]) and c == "M":
            # tras un M, las repeticiones son lineas (no moveto)
            cmd = "l" if rel else "L"
            c = "L"
            continue
    return out


def path_points(cmds):
    """Los arcos guardan 7 valores; su punto real es el ultimo par."""
    pts = []
    for _, ps in cmds:
        for q in ps:
            pts.append((q[5], q[6]) if len(q) == 7 else q)
    return pts


def emit(cmds, k=1.0, tx=0.0, ty=0.0):
    parts = []
    for c, ps in cmds:
        if c == "Z":
            parts.append("Z")
            continue
        if c == "M":
            x, y = ps[0]
            parts.append(f"M {x*k+tx:.2f} {y*k+ty:.2f}")
        elif c == "L":
            x, y = ps[0]
            parts.append(f"L {x*k+tx:.2f} {y*k+ty:.2f}")
        elif c == "A":
            rx, ry, rot, laf, sw, x, y = ps[0]
            parts.append(f"A {rx*k:.2f} {ry*k:.2f} {rot:.1f} {laf:.0f} {sw:.0f} "
                         f"{x*k+tx:.2f} {y*k+ty:.2f}")
        else:
            nums = []
            for x, y in ps:
                nums.append(f"{x*k+tx:.2f}")
                nums.append(f"{y*k+ty:.2f}")
            parts.append(f"{c} " + " ".join(nums))
    return " ".join(parts)


def mirror_y(cmds, axis):
    """Espejo vertical: (x, y) -> (x, 2*axis - y).

    Los arcos `A` invierten el `sweep`: el espejo reverses la orientacion del
    contorno, asi que un arco con sweep=0 pasa a ser sweep=1 (y al reves).
    """
    out = []
    for c, ps in cmds:
        if c == "Z":
            out.append(("Z", []))
            continue
        if c == "A":
            rx, ry, rot, laf, sw, x, y = ps[0]
            out.append(("A", [(rx, ry, rot, laf, 1 - sw, x, 2 * axis - y)]))
        else:
            out.append((c, [(x, 2 * axis - y) for x, y in ps]))
    return out


def reverse_subpath(cmds):
    """Invierte el sentido de un contorno cerrado (M / L* / A / L* / A / Z).

    POR QUE: un espejo (espejo vertical o rotacion de 180) reverses la
    orientacion del contorno. Con la regla de relleno `non-zero`, dos
    contornos con orientaciones OPUESTAS se cancelan en la zona de solape
    (winding +1 y -1 suman 0) y esa zona queda BLANCA. En el sobre eso
    abria una mordida justo donde la solapa se junta con el borde.

    Invertir el path devuelve la orientacion original sin tocar la forma.
    Los arcos ademas cambian su `sweep`, porque invertir el sentido de un
    arco tambien invierte su barrido.
    """
    nodes = []      # (punto, arco de entrada desde el nodo anterior o None)
    arcs = []       # arcos en el orden en que aparecen
    for c, ps in cmds:
        if c == "M":
            nodes.append([ps[0], None])
        elif c == "L":
            nodes.append([ps[0], None])
        elif c == "A":
            rx, ry, rot, laf, sw, x, y = ps[0]
            arcs.append((rx, ry, rot, laf, sw))
            nodes.append([(x, y), len(arcs) - 1])
    if len(nodes) < 3:
        return cmds
    n = len(nodes)

    def arc_of(i):
        """El arco de la arista que va de nodes[i] a nodes[i+1] (mod n)."""
        return nodes[(i + 1) % n][1]

    rev = list(reversed(range(n)))
    out = [("M", [nodes[rev[0]][0]])]
    for t in range(1, n):
        i = rev[t]
        j = rev[t - 1]
        a = arc_of(j)
        p = nodes[i][0]
        if a is not None:
            rx, ry, rot, laf, sw = arcs[a]
            out.append(("A", [(rx, ry, rot, laf, 1 - sw, p[0], p[1])]))
        else:
            out.append(("L", [p]))
    out.append(("Z", []))
    return out


def translate(cmds, dx, dy):
    out = []
    for c, ps in cmds:
        if c == "Z":
            out.append(("Z", []))
            continue
        if c == "A":
            rx, ry, rot, laf, sw, x, y = ps[0]
            out.append(("A", [(rx, ry, rot, laf, sw, x + dx, y + dy)]))
        else:
            out.append((c, [(x + dx, y + dy) for x, y in ps]))
    return out


def path_bbox(cmds, arc_samples=72):
    """BBox EXACTO de una ruta: los arcos se muestrean, no se ignoran.

    Hace falta porque el tope de la tapa redondeada del trazo no es un punto
    de la ruta — es el extremo del arco. Si se midiera solo con los vertices
    de la ruta, la tapa "asomaria" sin que nada lo dijera.
    """
    xs, ys = [], []
    cur = None
    for c, ps in cmds:
        if c == "Z":
            cur = None
            continue
        if c == "M":
            x, y = ps[0]
            cur = (x, y)
            xs.append(x); ys.append(y)
        elif c == "L":
            x, y = ps[0]
            xs.append(x); ys.append(y)
            cur = (x, y)
        elif c == "A":
            rx, ry, rot, laf, sw, x, y = ps[0]
            if cur is None:
                cur = (x, y)
            # parametrizacion endpoint -> centro (SVG spec, F.6.5)
            phi = math.radians(rot)
            cosp, sinp = math.cos(phi), math.sin(phi)
            dx2 = (cur[0] - x) / 2.0
            dy2 = (cur[1] - y) / 2.0
            x1p = cosp * dx2 + sinp * dy2
            y1p = -sinp * dx2 + cosp * dy2
            lam = (x1p * x1p) / (rx * rx) + (y1p * y1p) / (ry * ry)
            if lam > 1:
                s = math.sqrt(lam)
                rx, ry = rx * s, ry * s
            num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
            den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
            co = math.sqrt(max(0.0, num / den)) if den else 0.0
            if laf == sw:
                co = -co
            cxp = co * rx * y1p / ry
            cyp = -co * ry * x1p / rx
            cx = cosp * cxp - sinp * cyp + (cur[0] + x) / 2.0
            cy = sinp * cxp + cosp * cyp + (cur[1] + y) / 2.0
            def ang(ux, uy, vx, vy):
                dot = ux * vx + uy * vy
                n = math.hypot(ux, uy) * math.hypot(vx, vy)
                if n == 0:
                    return 0.0
                a = math.acos(max(-1.0, min(1.0, dot / n)))
                return -a if (ux * vy - uy * vx) < 0 else a
            th1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
            dth = ang((x1p - cxp) / rx, (y1p - cyp) / ry,
                      (-x1p - cxp) / rx, (-y1p - cyp) / ry)
            if not sw and dth > 0:
                dth -= 2 * math.pi
            elif sw and dth < 0:
                dth += 2 * math.pi
            for i in range(arc_samples + 1):
                t = th1 + dth * i / arc_samples
                px = cosp * rx * math.cos(t) - sinp * ry * math.sin(t) + cx
                py = sinp * rx * math.cos(t) + cosp * ry * math.sin(t) + cy
                xs.append(px); ys.append(py)
            cur = (x, y)
        else:
            for x, y in ps:
                xs.append(x); ys.append(y)
            cur = (x, y)
    return (min(xs), min(ys), max(xs), max(ys))




# ---------------------------------------------------------------------------
# ajuste al canvas, igual que la skill
# ---------------------------------------------------------------------------
MASTER = 1024
PADDING = 0.08


def fit(items, size=MASTER):
    """Escala y centra un conjunto de rutas en el lienzo.

    La tinta ocupa el 84% del lado mayor y queda centrada: es la misma regla
    que usa la skill, para que los assets externos y los del pipeline se
    comporten igual en el set.
    """
    allpts = [p for _, pts in items for p in pts]
    x0 = min(p[0] for p in allpts)
    x1 = max(p[0] for p in allpts)
    y0 = min(p[1] for p in allpts)
    y1 = max(p[1] for p in allpts)
    live = size * (1 - 2 * PADDING)
    k = min(live / max(x1 - x0, 1e-6), live / max(y1 - y0, 1e-6))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    tx, ty = -cx * k + size / 2, -cy * k + size / 2
    return " ".join(emit(cmds, k, tx, ty) for cmds, _ in items), k


def write_master(path, d, size=MASTER):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" '
                 f'fill="none" xmlns="http://www.w3.org/2000/svg">\n'
                 f'<path d="{d}" fill="black"/>\n</svg>\n')
