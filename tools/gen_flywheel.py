#!/usr/bin/env python3
"""Generates scenes/flywheel.x3d: 'The Copilot Flywheel' (pure X3D 4.0, no scripts).
Six stages on a ring (PROMPT -> COPILOT -> x3d_mcp -> VALIDATE -> RENDER -> PROVENANCE); a pulse laps the ring and each stage flares as it passes;
an outer ring of 28 hash-chain blocks is 'written' by a sweeping head; a gyroscope of rings and a star shell add depth.
usage: python3 tools/gen_flywheel.py"""
import colorsys, math, os, random
TAU = 2 * math.pi
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scenes", "flywheel.x3d")
def hsv(h, s=1, v=1): return " ".join(f"{c:.3f}" for c in colorsys.hsv_to_rgb(h % 1, s, v))
def n(x): return f"{x:.4f}".rstrip("0").rstrip(".")
def keys(N): return " ".join(n(i / N) for i in range(N + 1))
def bump(c, w, N=60, lo=0.0, hi=1.0):
    out = []
    for i in range(N + 1):
        t = i / N; d = min(abs(t - c), 1 - abs(t - c)); out.append(lo + (hi - lo) * math.exp(-(d / w) ** 2))
    return out
def spin(name, cyc, axis, target, sign=1, N=8):
    return (f'<TimeSensor DEF="{name}_T" cycleInterval="{cyc}" loop="true"/>\n<OrientationInterpolator DEF="{name}_I" key="{keys(N)}" keyValue="{" ".join(f"{axis} {sign * i / N * TAU:.5f}" for i in range(N + 1))}"/>\n'
            f'<ROUTE fromNode="{name}_T" fromField="fraction_changed" toNode="{name}_I" toField="set_fraction"/>\n<ROUTE fromNode="{name}_I" fromField="value_changed" toNode="{target}" toField="set_rotation"/>\n')
def glow(col, tr=0): return f'<Appearance><Material diffuseColor="0 0 0" emissiveColor="{col}" transparency="{tr}"/></Appearance>'
def torus(R, r, col, tr=0, seg=72, m=8):
    """torus as a plain IndexedFaceSet (X3DOM draws it; its Extrusion did not render the ring)"""
    pts = [f"{(R + r * math.cos(TAU * j / m)) * math.cos(TAU * i / seg):.3f} {r * math.sin(TAU * j / m):.3f} {(R + r * math.cos(TAU * j / m)) * math.sin(TAU * i / seg):.3f}" for i in range(seg) for j in range(m)]
    idx = " ".join(f"{i * m + j} {((i + 1) % seg) * m + j} {((i + 1) % seg) * m + (j + 1) % m} {i * m + (j + 1) % m} -1" for i in range(seg) for j in range(m))
    return f'<Shape>{glow(col, tr)}<IndexedFaceSet coordIndex="{idx}" solid="false"><Coordinate point="{" ".join(pts)}"/></IndexedFaceSet></Shape>'

STAGES = [("PROMPT", 0.93), ("COPILOT", 0.07), ("x3d_mcp", 0.14), ("VALIDATE", 0.40), ("RENDER", 0.53), ("PROVENANCE", 0.74)]
R, HR, NB, CYC = 5.0, 8.4, 28, 12
random.seed(5)
s = '<?xml version="1.0" encoding="UTF-8"?>\n<X3D profile="Immersive" version="4.0" xmlns:xsd="http://www.w3.org/2001/XMLSchema-instance" xsd:noNamespaceSchemaLocation="https://www.web3d.org/specifications/x3d-4.0.xsd">\n'
s += '<head><meta name="title" content="The Copilot Flywheel"/><meta name="description" content="Six stages, one pulse, a hash chain. Pure X3D 4.0."/></head>\n<Scene>\n'
s += '<NavigationInfo type=\'"EXAMINE" "ANY"\' headlight="false"/>\n<Background skyColor="0 0 0.03 0.06 0.02 0.17 0.01 0 0.05" skyAngle="1.1 1.7" groundColor="0.01 0 0.04 0.05 0.02 0.14" groundAngle="1.45"/>\n'
s += '<Viewpoint position="0 6.5 15" orientation="1 0 0 -0.38" fieldOfView="1.0" description="Overview"/>\n<DirectionalLight direction="-0.3 -0.8 -0.5" intensity="0.7"/>\n'
# stars
pts, cols = [], []
for _ in range(1600):
    v = [random.gauss(0, 1) for _ in range(3)]; d = math.sqrt(sum(x * x for x in v)) or 1; r = random.uniform(30, 55)
    pts.append(" ".join(f"{x / d * r:.1f}" for x in v)); c = colorsys.hsv_to_rgb(random.choice([0.6, 0.65, 0.9, 0.12]), random.uniform(0, .5), random.uniform(.4, 1)); cols.append(" ".join(f"{x:.2f}" for x in c))
s += f'<Transform DEF="Stars_X"><Shape><PointSet><Color color="{" ".join(cols)}"/><Coordinate point="{" ".join(pts)}"/></PointSet></Shape></Transform>\n'
s += '<Transform DEF="World_X">\n'
# core + halos + gyroscope
s += '<Transform DEF="Core_X"><Shape>' + glow("0.75 0.95 1") + '<Sphere radius="0.8"/></Shape><Shape>' + glow("0.3 0.7 1", 0.8) + '<Sphere radius="1.25"/></Shape><Shape>' + glow("0.4 0.3 1", 0.93) + '<Sphere radius="1.9"/></Shape></Transform>\n'
for i, (rad, col, ax) in enumerate([(2.5, hsv(0.52), "1 0 0"), (3.1, hsv(0.78), "0 0 1"), (3.7, hsv(0.9), "1 1 0")]):
    s += f'<Transform DEF="Gyro{i}_X">{torus(rad, 0.045, col, 0.1)}</Transform>\n'
# stage ring + stages
s += torus(R, 0.05, "0.35 0.5 0.8", 0.55, 96) + "\n"
OCT = "0 0.7 0  0.7 0 0  0 0 0.7  -0.7 0 0  0 0 -0.7  0 -0.7 0"
OCI = "0 1 2 -1 0 2 3 -1 0 3 4 -1 0 4 1 -1 5 2 1 -1 5 3 2 -1 5 4 3 -1 5 1 4 -1"
for i, (nm, hue) in enumerate(STAGES):
    a = TAU * i / 6; col = hsv(hue, 0.75, 1)
    s += (f'<Transform DEF="S{i}_X" translation="{R * math.cos(a):.3f} 0 {R * math.sin(a):.3f}"><Transform DEF="S{i}_Spin"><Shape><Appearance><Material diffuseColor="{hsv(hue, .6, .5)}" emissiveColor="{hsv(hue, .8, .55)}" specularColor="1 1 1" shininess="0.8"/></Appearance>'
          f'<IndexedFaceSet coordIndex="{OCI}" solid="false"><Coordinate point="{OCT}"/></IndexedFaceSet></Shape></Transform>'
          f'<Shape><Appearance><Material DEF="S{i}_Halo" diffuseColor="0 0 0" emissiveColor="{col}" transparency="0.88"/></Appearance><Sphere radius="1.05"/></Shape>'
          f'<Transform translation="0 1.45 0"><Billboard axisOfRotation="0 0 0"><Shape>{glow(col)}<Text string=\'"{nm}"\'><FontStyle family=\'"SANS"\' justify=\'"MIDDLE" "MIDDLE"\' size="0.55"/></Text></Shape></Billboard></Transform></Transform>\n')
# pulse + comet (pivot rotates; fraction 0..1 = one lap; pulse passes stage i at i/6)
for k in range(7):
    s += f'<Transform DEF="Comet{k}_X"><Transform translation="{R} 0 0"><Shape>{glow("1 1 1" if k == 0 else hsv(0.55, 0.5, 1 - k * 0.12), k * 0.12)}<Sphere radius="{0.36 - 0.035 * k:.3f}"/></Shape></Transform></Transform>\n'
# hash chain ring
s += '<Transform DEF="Tilt_X" rotation="1 0 0 0.32"><Transform DEF="Chain_X">\n'
s += torus(HR, 0.02, "0.25 0.3 0.6", 0.4, 120) + "\n"
for j in range(NB):
    a = TAU * j / NB
    s += f'<Transform translation="{HR * math.cos(a):.3f} 0 {HR * math.sin(a):.3f}" rotation="0 1 0 {-(a + math.pi / 2):.4f}"><Shape><Appearance><Material DEF="B{j}_M" diffuseColor="0 0 0" emissiveColor="0.2 0.3 0.4"/></Appearance><Box size="0.95 0.28 0.5"/></Shape></Transform>\n'
s += '</Transform></Transform>\n</Transform>\n'
# ------------------------------------------------------------ animation
s += f'<TimeSensor DEF="Lap_T" cycleInterval="{CYC}" loop="true"/>\n'
for k in range(7):
    lag = k * 0.012
    kv = " ".join(f"0 1 0 {-(i / 12 - lag) * TAU:.5f}" for i in range(13))
    s += (f'<OrientationInterpolator DEF="Comet{k}_I" key="{keys(12)}" keyValue="{kv}"/>\n<ROUTE fromNode="Lap_T" fromField="fraction_changed" toNode="Comet{k}_I" toField="set_fraction"/>\n'
          f'<ROUTE fromNode="Comet{k}_I" fromField="value_changed" toNode="Comet{k}_X" toField="set_rotation"/>\n')
for i in range(6):
    c = i / 6
    sc = " ".join(f"{1 + 0.55 * v:.3f} {1 + 0.55 * v:.3f} {1 + 0.55 * v:.3f}" for v in bump(c, 0.045))
    tr = " ".join(n(0.88 - 0.62 * v) for v in bump(c, 0.045))
    s += (f'<PositionInterpolator DEF="S{i}_ScI" key="{keys(60)}" keyValue="{sc}"/>\n<ScalarInterpolator DEF="S{i}_TrI" key="{keys(60)}" keyValue="{tr}"/>\n'
          f'<ROUTE fromNode="Lap_T" fromField="fraction_changed" toNode="S{i}_ScI" toField="set_fraction"/>\n<ROUTE fromNode="S{i}_ScI" fromField="value_changed" toNode="S{i}_X" toField="set_scale"/>\n'
          f'<ROUTE fromNode="Lap_T" fromField="fraction_changed" toNode="S{i}_TrI" toField="set_fraction"/>\n<ROUTE fromNode="S{i}_TrI" fromField="value_changed" toNode="S{i}_Halo" toField="set_transparency"/>\n')
    s += spin(f"S{i}Spin", 6 + i, "0 1 0", f"S{i}_Spin", 1)
# chain writer head: sweeps once per lap
for j in range(NB):
    c = j / NB
    vals = []
    for i in range(61):
        t = i / 60; d = (t - c) % 1.0       # time since the head passed block j
        g = 0.38 + (0.78 * math.exp(-(d / 0.03) ** 2) if d < 0.5 else 0) + 0.2 * math.exp(-d / 0.25) * (1 if d < 0.9 else 0)
        base = colorsys.hsv_to_rgb(0.5 + 0.35 * c, 0.7, 1)
        vals.append(" ".join(f"{min(1, g * x):.3f}" for x in base))
    s += (f'<ColorInterpolator DEF="B{j}_I" key="{keys(60)}" keyValue="{" ".join(vals)}"/>\n<ROUTE fromNode="Lap_T" fromField="fraction_changed" toNode="B{j}_I" toField="set_fraction"/>\n'
          f'<ROUTE fromNode="B{j}_I" fromField="value_changed" toNode="B{j}_M" toField="set_emissiveColor"/>\n')
s += spin("Chain", 90, "0 1 0", "Chain_X", 1) + spin("World", 120, "0 1 0", "World_X", -1) + spin("Stars", 300, "0.2 1 0", "Stars_X", 1)
for i, cyc in enumerate((9, 13, 17)): s += spin(f"Gyro{i}", cyc, ["1 0 0", "0 0 1", "1 1 0"][i], f"Gyro{i}_X", 1 if i % 2 == 0 else -1)
s += ('<TimeSensor DEF="Core_T" cycleInterval="3" loop="true"/>\n<PositionInterpolator DEF="Core_I" key="0 0.5 1" keyValue="1 1 1 1.12 1.12 1.12 1 1 1"/>\n'
      '<ROUTE fromNode="Core_T" fromField="fraction_changed" toNode="Core_I" toField="set_fraction"/>\n<ROUTE fromNode="Core_I" fromField="value_changed" toNode="Core_X" toField="set_scale"/>\n')
s += "</Scene>\n</X3D>\n"
open(OUT, "w").write(s); print(len(s), "bytes")
