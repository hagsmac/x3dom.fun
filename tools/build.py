#!/usr/bin/env python3
"""Validate scenes/*.x3d with x3d_mcp (validate_x3d, validate_semantic), wrap them with x3dom_page -> pages/*.x3dom.html,
write pages/*.xite.html and index.html.   usage: ~/Projects/x3d/x3d_mcp/.venv/bin/python tools/build.py"""
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from demos import DEMOS
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
REPO = os.path.expanduser("~/Projects/x3d/x3d_mcp")
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
XITE = "https://cdn.jsdelivr.net/npm/x_ite@16.4.3/dist"
txt = lambda r: "".join(getattr(c, "text", "") for c in r.content)
def parse(t):
    try: return json.loads(t)
    except Exception: return {"raw": t}
NAV = '<div style="position:fixed;top:8px;left:8px;z-index:9;font:13px sans-serif;background:#000a;padding:4px 10px;border-radius:12px"><a style="color:#8cf" href="../index.html">&larr; all demos</a> &middot; {t} &middot; <a style="color:#8cf" href="{o}">{ol}</a></div>'
async def main():
    p = StdioServerParameters(command=REPO + "/.venv/bin/python", args=["-m", "src.server"], cwd=REPO)
    summary = {}
    async with stdio_client(p) as (r, w), ClientSession(r, w) as s:
        await s.initialize()
        for n, title, desc, feats, hint in DEMOS:
            c = open(f"{HERE}/scenes/{n}.x3d").read(); out = {"file": n + ".x3d"}
            for tool, a in (("validate_x3d", {"content": c, "encoding": "xml"}), ("validate_semantic", {"content": c})):
                out[tool] = parse(txt(await s.call_tool(tool, a)))
            json.dump(out, open(f"{HERE}/validation/{n}.validate.json", "w"), indent=1)
            ok = out["validate_x3d"].get("valid") is True and ("All Clear" in json.dumps(out["validate_semantic"]) or "Found 0 error(s), 0 warning(s)" in json.dumps(out["validate_semantic"]))
            summary[n] = ok
            print(n, "OK" if ok else "FAIL", json.dumps(out["validate_x3d"])[:200], "|" if ok else json.dumps(out["validate_semantic"])[:400])
            html = txt(await s.call_tool("x3dom_page", {"content": c, "title": title + " (X3DOM)", "width": "100%", "height": "80vh"}))
            html = html.replace("<body>", "<body>\n" + NAV.format(t="X3DOM", o=f"{n}.xite.html", ol="open in X_ITE"), 1)
            open(f"{HERE}/pages/{n}.x3dom.html", "w").write(html)
            open(f"{HERE}/pages/{n}.xite.html", "w").write(f'''<!doctype html><meta charset="utf-8"><title>{title} (X_ITE)</title>
<link rel="stylesheet" href="{XITE}/x_ite.css">
<style>html,body{{margin:0;background:#111;color:#ccc;font:14px sans-serif}}x3d-canvas{{width:100%;height:80vh;display:block}}p{{padding:0 14px}}</style>
<script src="{XITE}/x_ite.min.js"></script>
{NAV.format(t="X_ITE", o=f"{n}.x3dom.html", ol="open in X3DOM")}
<x3d-canvas id="c" src="../scenes/{n}.x3d" contextMenu="false" splashScreen="false"></x3d-canvas>
<p><b>{title}</b>: {desc} <i>({hint})</i></p>
''')
    cards = "".join(f'<a class="c" href="pages/{n}.xite.html"><img loading="lazy" src="shots/{n}-t2.png" alt=""><h3>{t}</h3><p>{d}</p><small>{ft} &middot; <b>{h}</b></small>'
                    f'<span><a href="pages/{n}.xite.html">X_ITE</a> &middot; <a href="pages/{n}.x3dom.html">X3DOM</a> &middot; <a href="scenes/{n}.x3d">.x3d</a></span></a>' for n, t, d, ft, h in DEMOS)
    open(f"{HERE}/index.html", "w").write(f'''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>x3dom.fun</title>
<style>body{{margin:0;background:#0c0c18;color:#ddd;font:16px/1.45 system-ui,sans-serif}}header{{padding:32px 24px 8px;text-align:center}}h1{{margin:0;font-size:2.4em;letter-spacing:.03em;background:linear-gradient(90deg,#f66,#fc4,#6f9,#6cf,#c6f);-webkit-background-clip:text;color:transparent}}
.g{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:18px;padding:20px 24px 40px;max-width:1200px;margin:auto}}.c{{display:block;background:#161628;border-radius:12px;padding:12px;color:inherit;text-decoration:none;border:1px solid #2a2a48}}.c:hover{{border-color:#8cf}}
.c img{{width:100%;border-radius:8px;aspect-ratio:11/5.76;object-fit:cover;background:#000}}h3{{margin:8px 0 2px}}.c p{{margin:2px 0 8px;font-size:14px;color:#aab}}small{{color:#889}}span{{display:block;margin-top:8px}}span a{{color:#8cf}}footer{{text-align:center;color:#778;padding:0 0 30px;font-size:13px}}</style>
<header><h1>x3dom.fun</h1><p>Small, scripts-free X3D 4.0 toys. Each one runs in <b>X_ITE</b> and in <b>X3DOM</b>.</p></header><div class="g">{cards}</div>
<footer>Scenes validated with the x3d_mcp server &middot; X3DOM 1.8.2 and X_ITE 16.4.3 load from CDNs</footer>''')
    json.dump(summary, open(f"{HERE}/validation/summary.json", "w"), indent=1)
asyncio.run(main())
