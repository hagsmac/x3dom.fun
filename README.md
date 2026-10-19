# x3dom.fun

Ten small, script-free X3D 4.0 toys. Each runs in X_ITE and in X3DOM. Open `index.html` for the gallery.

| demo | what it is | features |
|---|---|---|
| flywheel | the showpiece: six glowing stages, a pulse that laps them, a hash chain being written | torus meshes, Billboard text, 28 ColorInterpolators |
| galaxy | 6,000-star spiral galaxy, core spins faster than rim | PointSet + Color |
| sierpinski | 256-tetrahedron fractal, tumbling, lit by a colour-cycling light | IndexedFaceSet, animated DirectionalLight |
| equalizer | 13x13 bars driven by a radial wave | 169 PositionInterpolators as scale |
| cradle | Newton's cradle | sampled pendulum OrientationInterpolators |
| whack | nine moles on timers, click to squash | TouchSensor, no scripts |
| tunnel | endless seamless ring fly-through | Fog, emissive, looping world translation |
| solar, bounce, touch | the three starter scenes | TimeSensor + interpolators, TouchSensor |

## Layout
- `scenes/*.x3d`: sources. `gen_flywheel.py` generates flywheel; `gen_wild.py` generates galaxy, sierpinski, equalizer, cradle, whack and tunnel. solar, bounce and touch were written by hand.
- `pages/*.x3dom.html`: made by the x3d_mcp `x3dom_page` tool, with a nav bar added. They load X3DOM 1.8.2 from `x3dom.org`.
- `pages/*.xite.html`: they load X_ITE 16.4.3 from `cdn.jsdelivr.net`.
- `shots/`: X_ITE screenshots, two per scene. `validation/`: validator and render-check output.
- `tools/`: `demos.py` (metadata), `gen_wild.py`, `build.py` (validate + generate pages and index), `render.js` (screenshots).

## Run locally
```
python3 -m http.server --bind 127.0.0.1 8765
```
Open http://127.0.0.1:8765/. Do not use file://, because X_ITE fetches the .x3d. The pages need internet for the CDNs.

## Verified, and what was not
Checked on 2026-10-19 on macOS:
- All 10 scenes pass `validate_x3d` (X3D 4.0 schema, 0 errors) and `validate_semantic` (0 errors, 0 warnings). galaxy has 4 infos, about shapes with no Appearance, which is intended because unlit PointSets use their Color. whack and tunnel use the Immersive profile, because they need TouchSensor and Fog level 2.
- All 10 pages rendered in X_ITE 16.4.3 (headless Chromium over 127.0.0.1). Each screenshot is non-blank, and the two timestamps differ, by 1.2% (bounce) up to about 38% (equalizer, tunnel). The click scenes (touch, whack) were also clicked once between the two shots.
- That render run answered the jsDelivr URL from a local copy of X_ITE 16.4.3.
- After deploying to https://hagsmac.github.io/x3dom.fun/ I opened X3DOM whack, galaxy and tunnel and X_ITE cradle in a browser and saw them render. X3DOM draws the galaxy's points fine, and the tunnel with fog. The other X3DOM pages, the TouchSensor click in X3DOM and the animated light in sierpinski were **not** checked.
- **X3DOM vs X_ITE, observed:** an Extrusion-built ring did not show in X3DOM but did in X_ITE, so the flywheel's rings are plain IndexedFaceSet meshes. The flywheel was opened in X3DOM from a local server and renders (pulse, labels, rings).
- A single unexplained 404 console message on the galaxy page (probably the favicon) was not chased.
