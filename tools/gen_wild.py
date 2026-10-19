#!/usr/bin/env python3
"""Generates the 'wild' scenes into scenes/: galaxy, sierpinski, equalizer, cradle, whack, tunnel (pure X3D 4.0, no scripts).
usage: python3 tools/gen_wild.py"""
import colorsys, math, os, random
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scenes")
TAU = 2 * math.pi

def head(title, profile="Interchange"):
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<X3D profile="{profile}" version="4.0" xmlns:xsd="http://www.w3.org/2001/XMLSchema-instance" '
            f'xsd:noNamespaceSchemaLocation="https://www.web3d.org/specifications/x3d-4.0.xsd">\n<head><meta name="title" content="{title}"/></head>\n<Scene>\n')
TAIL = "</Scene>\n</X3D>\n"
def save(name, s): open(os.path.join(OUT, name + ".x3d"), "w").write(s + TAIL)
def hsv(h, s=1, v=1): return " ".join(f"{c:.3f}" for c in colorsys.hsv_to_rgb(h % 1, s, v))
def f(x): return f"{x:.3f}".rstrip("0").rstrip(".") if "." in f"{x:.3f}" else f"{x:.3f}"
def spin(name, cyc, axis="0 1 0", target=None, loop=True, n=8, sign=1):
    ks = [i / n for i in range(n + 1)]
    kv = " ".join(f"{axis} {sign * k * TAU:.5f}" for k in ks)
    target = target or name + "_X"
    return (f'<TimeSensor DEF="{name}_T" cycleInterval="{cyc}" loop="{str(loop).lower()}"/>\n'
            f'<OrientationInterpolator DEF="{name}_I" key="{" ".join(f(k) for k in ks)}" keyValue="{kv}"/>\n'
            f'<ROUTE fromNode="{name}_T" fromField="fraction_changed" toNode="{name}_I" toField="set_fraction"/>\n'
            f'<ROUTE fromNode="{name}_I" fromField="value_changed" toNode="{target}" toField="set_rotation"/>\n')

# ---------------------------------------------------------------- galaxy
def galaxy():
    random.seed(37)
    layers = {"Core": (0, 2.6, 1500, 9), "Mid": (2.6, 6.2, 2200, 15), "Rim": (6.2, 11, 2300, 26)}
    s = head("Spiral Galaxy") + '<NavigationInfo type=\'"EXAMINE" "ANY"\' headlight="false"/>\n<Background skyColor="0 0 0.02"/>\n'
    s += '<Viewpoint position="0 9 15" orientation="1 0 0 -0.52" description="Above the disc"/>\n'
    # far stars
    pts, cols = [], []
    for _ in range(700):
        v = [random.gauss(0, 1) for _ in range(3)]; n = math.sqrt(sum(x * x for x in v)) or 1; r = random.uniform(45, 70)
        pts.append(" ".join(f"{x / n * r:.1f}" for x in v)); g = random.uniform(.35, 1); cols.append(f"{g:.2f} {g:.2f} {g:.2f}")
    s += f'<Shape><PointSet><Color color="{" ".join(cols)}"/><Coordinate point="{" ".join(pts)}"/></PointSet></Shape>\n'
    # tilt the whole disc a bit
    s += '<Transform rotation="1 0 0 0.25"><Transform rotation="0 0 1 -0.12">\n'
    for nm, (r0, r1, cnt, cyc) in layers.items():
        pts, cols = [], []
        for _ in range(cnt):
            r = r0 + (r1 - r0) * random.random() ** 0.8
            arm = random.randint(0, 1)
            th = arm * math.pi + r * 0.62 + random.gauss(0, 0.32 + 0.03 * r)
            y = random.gauss(0, 0.12 + 0.35 * math.exp(-r / 2.2))
            pts.append(f"{r * math.cos(th):.2f} {y:.2f} {r * math.sin(th):.2f}")
            k = min(1, r / 11)
            if r < 2.6: c = (1, 0.85 - 0.2 * random.random(), 0.5 + 0.3 * random.random())
            else:
                c = colorsys.hsv_to_rgb(0.62 + 0.2 * random.random() * k - 0.05 * (1 - k), 0.35 + 0.5 * k, 0.65 + 0.35 * random.random())
            cols.append(f"{c[0]:.2f} {c[1]:.2f} {c[2]:.2f}")
        s += f'<Transform DEF="{nm}_X"><Shape><PointSet><Color color="{" ".join(cols)}"/><Coordinate point="{" ".join(pts)}"/></PointSet></Shape></Transform>\n'
    s += '</Transform></Transform>\n'
    for nm, (_, _, _, cyc) in layers.items():
        s += spin(nm, cyc, sign=-1)
    save("galaxy", s)

# ---------------------------------------------------------------- sierpinski
def sierpinski(level=4):
    A, B, C, D = (1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)
    mid = lambda p, q: tuple((a + b) / 2 for a, b in zip(p, q))
    def rec(v, lv):
        if lv == 0: return [v]
        out = []
        for i in range(4):
            out += rec(tuple(v[i] if j == i else mid(v[i], v[j]) for j in range(4)), lv - 1)
        return out
    tets = rec((A, B, C, D), level)
    pts, cols, idx = [], [], []
    for t in tets:
        base = len(pts)
        for p in t:
            pts.append(f"{p[0]:.4f} {p[1]:.4f} {p[2]:.4f}")
            cols.append(hsv(0.02 + 0.4 * (p[1] + 1) + 0.08 * p[0] + 0.06 * p[2], 0.75, 1))
        for tri in ((0, 1, 2), (0, 3, 1), (0, 2, 3), (1, 3, 2)):
            idx.append(" ".join(str(base + i) for i in tri) + " -1")
    s = head("Sierpinski Tetrahedron") + '<NavigationInfo type=\'"EXAMINE" "ANY"\' headlight="false"/>\n<Background skyColor="0.02 0.01 0.06"/>\n<Viewpoint position="0 0.3 5.6" description="Front"/>\n'
    s += '<DirectionalLight DEF="Glow" direction="-0.4 -0.6 -0.7" color="1 0.3 0.3" intensity="1"/>\n<DirectionalLight direction="0.6 0.5 0.4" color="0.7 0.7 0.9" intensity="1.1"/>\n'
    s += ('<Transform DEF="Tumble_X"><Transform DEF="Breath_X"><Shape><Appearance><Material specularColor="0.5 0.5 0.5" shininess="0.4"/></Appearance>'
          f'<IndexedFaceSet coordIndex="{" ".join(idx)}" creaseAngle="0"><Coordinate point="{" ".join(pts)}"/><Color color="{" ".join(cols)}"/></IndexedFaceSet></Shape></Transform></Transform>\n')
    s += spin("Tumble", 18, axis="0.3 0.9 0.3", n=12)
    s += ('<TimeSensor DEF="Breath_T" cycleInterval="4" loop="true"/>\n<PositionInterpolator DEF="Breath_I" key="0 0.5 1" keyValue="1 1 1 1.18 1.18 1.18 1 1 1"/>\n'
          '<ROUTE fromNode="Breath_T" fromField="fraction_changed" toNode="Breath_I" toField="set_fraction"/>\n<ROUTE fromNode="Breath_I" fromField="value_changed" toNode="Breath_X" toField="set_scale"/>\n')
    cs = [hsv(i / 6) for i in range(7)]
    s += (f'<TimeSensor DEF="Glow_T" cycleInterval="9" loop="true"/>\n<ColorInterpolator DEF="Glow_I" key="{" ".join(f(i / 6) for i in range(7))}" keyValue="{" ".join(cs)}"/>\n'
          '<ROUTE fromNode="Glow_T" fromField="fraction_changed" toNode="Glow_I" toField="set_fraction"/>\n<ROUTE fromNode="Glow_I" fromField="value_changed" toNode="Glow" toField="set_color"/>\n')
    save("sierpinski", s)

# ---------------------------------------------------------------- equalizer
def equalizer(n=13, sp=0.9):
    K = 16
    keys = " ".join(f(i / K) for i in range(K + 1))
    s = head("Ripple Equalizer") + '<Background skyColor="0.04 0.04 0.1"/>\n<Viewpoint position="0 8 13" orientation="1 0 0 -0.5" description="Overview"/>\n'
    s += '<Transform DEF="City_X">\n'
    ra = []
    for i in range(n):
        for j in range(n):
            x, z = (i - n // 2) * sp, (j - n // 2) * sp
            r = math.hypot(x, z); nm = f"B{i}_{j}"
            vals = []
            for k in range(K + 1):
                t = k / K; h = 0.35 + 2.6 * (0.5 + 0.5 * math.sin(TAU * (t - r / 5.0))) * math.exp(-r / 14)
                vals.append(f"1 {h:.2f} 1")
            col = hsv(0.55 + r / 14, 0.85, 1)
            s += (f'<Transform DEF="{nm}_X" translation="{x:.2f} 0 {z:.2f}" scale="1 1 1"><Transform translation="0 0.5 0"><Shape><Appearance><Material diffuseColor="{col}" specularColor="0.4 0.4 0.4"/></Appearance>'
                  f'<Box size="0.7 1 0.7"/></Shape></Transform></Transform>\n')
            ra.append(f'<PositionInterpolator DEF="{nm}_I" key="{keys}" keyValue="{" ".join(vals)}"/>\n<ROUTE fromNode="Pulse" fromField="fraction_changed" toNode="{nm}_I" toField="set_fraction"/>\n<ROUTE fromNode="{nm}_I" fromField="value_changed" toNode="{nm}_X" toField="set_scale"/>\n')
    s += '</Transform>\n<TimeSensor DEF="Pulse" cycleInterval="3" loop="true"/>\n' + "".join(ra) + spin("City", 40, target="City_X", n=8)
    save("equalizer", s)

# ---------------------------------------------------------------- newton's cradle
def cradle():
    a = 0.75; N = 48
    s = head("Newton's Cradle") + '<Background skyColor="0.12 0.1 0.2"/>\n<Viewpoint position="0 3 11" orientation="1 0 0 -0.12" description="Front"/>\n'
    s += '<Transform translation="0 -0.2 0"><Shape><Appearance><Material diffuseColor="0.25 0.18 0.12"/></Appearance><Box size="10 0.4 5"/></Shape></Transform>\n'
    mat = '<Appearance><Material diffuseColor="0.7 0.7 0.75" specularColor="1 1 1" shininess="0.6"/></Appearance>'
    for x in (-3.4, 3.4):
        s += f'<Transform translation="{x} 2.4 0"><Shape>{mat}<Box size="0.2 4.8 0.2"/></Shape></Transform>\n'
    s += f'<Transform translation="0 4.5 0"><Shape>{mat}<Box size="7 0.2 0.2"/></Shape></Transform>\n'
    cols = [hsv(i / 5, 0.8, 1) for i in range(5)]
    for i in range(5):
        x = (i - 2) * 1.0
        s += (f'<Transform {("DEF=%sP%d_X%s " % (chr(34), i, chr(34))) if i in (0, 4) else ""}translation="{x} 4.5 0"><Transform translation="0 -1.75 0"><Shape><Appearance><Material emissiveColor="0.6 0.6 0.6"/></Appearance><Cylinder radius="0.02" height="3.5"/></Shape></Transform>'
              f'<Transform translation="0 -3.5 0"><Shape><Appearance><Material diffuseColor="{cols[i]}" specularColor="1 1 1" shininess="0.8"/></Appearance><Sphere radius="0.5"/></Shape></Transform></Transform>\n')
    s += '<TimeSensor DEF="Clock" cycleInterval="2.4" loop="true"/>\n'
    for nm, sign, fn in (("P0", -1, lambda c: max(0, c)), ("P4", 1, lambda c: max(0, -c))):
        ks = [i / N for i in range(N + 1)]
        kv = " ".join(f"0 0 1 {sign * a * fn(math.cos(TAU * k)):.4f}" for k in ks)
        s += (f'<OrientationInterpolator DEF="{nm}_I" key="{" ".join(f(k) for k in ks)}" keyValue="{kv}"/>\n<ROUTE fromNode="Clock" fromField="fraction_changed" toNode="{nm}_I" toField="set_fraction"/>\n'
              f'<ROUTE fromNode="{nm}_I" fromField="value_changed" toNode="{nm}_X" toField="set_rotation"/>\n')
    save("cradle", s)

# ---------------------------------------------------------------- whack-a-mole
def whack():
    s = head("Whack-a-Mole", "Immersive") + '<Background skyColor="0.5 0.8 1"/>\n<Viewpoint position="0 9 9" orientation="1 0 0 -0.85" description="Lawn"/>\n'
    s += '<Transform translation="0 -0.3 0"><Shape><Appearance><Material diffuseColor="0.2 0.6 0.2"/></Appearance><Box size="11 0.6 11"/></Shape></Transform>\n'
    cyc = [3.1, 3.7, 2.7, 4.1, 3.3, 2.9, 3.9, 3.5, 4.3]
    for i in range(3):
        for j in range(3):
            n = i * 3 + j; x, z = (j - 1) * 3, (i - 1) * 3; c = cyc[n]; ph = (n * 0.37) % 1
            s += f'<Transform translation="{x} 0.01 {z}"><Shape><Appearance><Material diffuseColor="0.05 0.03 0.02"/></Appearance><Cylinder radius="1.1" height="0.02"/></Shape></Transform>\n'
            s += (f'<Transform DEF="M{n}_Pop" translation="{x} -1.1 {z}"><Transform DEF="M{n}_Squash"><Shape><Appearance><Material DEF="M{n}_Mat" diffuseColor="0.55 0.33 0.18"/></Appearance><Sphere radius="0.8"/></Shape>'
                  '<Transform translation="-0.3 0.3 0.62"><Shape><Appearance><Material diffuseColor="1 1 1"/></Appearance><Sphere radius="0.2"/></Shape></Transform>'
                  '<Transform translation="0.3 0.3 0.62"><Shape><Appearance><Material diffuseColor="1 1 1"/></Appearance><Sphere radius="0.2"/></Shape></Transform>'
                  '<Transform translation="-0.3 0.3 0.8"><Shape><Appearance><Material diffuseColor="0 0 0"/></Appearance><Sphere radius="0.09"/></Shape></Transform>'
                  '<Transform translation="0.3 0.3 0.8"><Shape><Appearance><Material diffuseColor="0 0 0"/></Appearance><Sphere radius="0.09"/></Shape></Transform>'
                  '<Transform translation="0 0 0.78"><Shape><Appearance><Material diffuseColor="1 0.5 0.6"/></Appearance><Sphere radius="0.17"/></Shape></Transform>'
                  f'<TouchSensor DEF="M{n}_Touch" description="whack!"/></Transform></Transform>\n')
            # rising/falling profile, phase shifted by rotating the key list start is awkward; use a start offset via different cycle times instead
            ks = "0 0.5 0.58 0.78 0.86 1"; ys = [-1.1, -1.1, 0.25, 0.25, -1.1, -1.1]
            kv = " ".join(f"{x} {y} {z}" for y in ys)
            s += (f'<TimeSensor DEF="M{n}_PopT" cycleInterval="{c}" loop="true"/>\n<PositionInterpolator DEF="M{n}_PopI" key="{ks}" keyValue="{kv}"/>\n'
                  f'<ROUTE fromNode="M{n}_PopT" fromField="fraction_changed" toNode="M{n}_PopI" toField="set_fraction"/>\n<ROUTE fromNode="M{n}_PopI" fromField="value_changed" toNode="M{n}_Pop" toField="set_translation"/>\n')
            s += (f'<TimeSensor DEF="M{n}_BonkT" cycleInterval="0.7"/>\n<PositionInterpolator DEF="M{n}_BonkI" key="0 0.15 0.35 0.6 1" keyValue="1 1 1 1.5 0.35 1.5 0.8 1.25 0.8 1.1 0.9 1.1 1 1 1"/>\n'
                  f'<ColorInterpolator DEF="M{n}_BonkC" key="0 0.15 0.7 1" keyValue="0.55 0.33 0.18 1 0.1 0.1 1 0.4 0.4 0.55 0.33 0.18"/>\n'
                  f'<ROUTE fromNode="M{n}_Touch" fromField="touchTime" toNode="M{n}_BonkT" toField="set_startTime"/>\n'
                  f'<ROUTE fromNode="M{n}_BonkT" fromField="fraction_changed" toNode="M{n}_BonkI" toField="set_fraction"/>\n<ROUTE fromNode="M{n}_BonkI" fromField="value_changed" toNode="M{n}_Squash" toField="set_scale"/>\n'
                  f'<ROUTE fromNode="M{n}_BonkT" fromField="fraction_changed" toNode="M{n}_BonkC" toField="set_fraction"/>\n<ROUTE fromNode="M{n}_BonkC" fromField="value_changed" toNode="M{n}_Mat" toField="set_diffuseColor"/>\n')
    save("whack", s)

# ---------------------------------------------------------------- tunnel
def tunnel(rings=30, gap=3.0, period=6):
    s = head("Rainbow Tunnel", "Immersive") + '<NavigationInfo type=\'"NONE"\' headlight="false"/>\n<Background skyColor="0 0 0"/>\n<Fog color="0 0 0" visibilityRange="70" fogType="LINEAR"/>\n<Viewpoint position="0 0 0" description="Inside"/>\n'
    s += '<Transform DEF="Roll_X"><Transform DEF="Travel_X">\n'
    for i in range(rings):
        z = -gap * i; col = hsv((i % period) / period)
        s += f'<Transform translation="0 0 {z:g}" rotation="0 0 1 {(i % period) * 0.3:.3f}"><Transform rotation="1 0 0 1.5708"><Shape><Appearance><Material diffuseColor="0 0 0" emissiveColor="{col}"/></Appearance><Cylinder radius="5" height="0.3" top="false" bottom="false" solid="false"/></Shape></Transform>'
        for k in range(6):
            a = k * TAU / 6
            s += f'<Transform translation="{5 * math.cos(a):.2f} {5 * math.sin(a):.2f} 0"><Shape><Appearance><Material diffuseColor="0 0 0" emissiveColor="{hsv((i + 3) % period / period)}"/></Appearance><Box size="0.7 0.7 0.7"/></Shape></Transform>'
        s += '</Transform>\n'
    s += '</Transform></Transform>\n'
    L = gap * period
    s += (f'<TimeSensor DEF="Travel_T" cycleInterval="4" loop="true"/>\n<PositionInterpolator DEF="Travel_I" key="0 1" keyValue="0 0 0 0 0 {L:g}"/>\n'
          '<ROUTE fromNode="Travel_T" fromField="fraction_changed" toNode="Travel_I" toField="set_fraction"/>\n<ROUTE fromNode="Travel_I" fromField="value_changed" toNode="Travel_X" toField="set_translation"/>\n')
    s += spin("Roll", 24, axis="0 0 1", n=8)
    save("tunnel", s)

for fn in (galaxy, sierpinski, equalizer, cradle, whack, tunnel): fn()
