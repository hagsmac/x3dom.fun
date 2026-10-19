# id, title, one-line description, X3D features used, interaction hint
DEMOS = [
 ("flywheel", "The Copilot Flywheel", "Six stages, one glowing pulse, a hash chain being written: prompt, co-author, tools, validators, renderers, provenance.", "generated tori, Billboard text, 28 ColorInterpolators, PointSet starfield", "drag to orbit"),
 ("galaxy", "Spiral Galaxy", "6,000 stars in two spiral arms with differential rotation: the core spins faster than the rim.", "PointSet + Color, 3 independent pivots", "drag to orbit"),
 ("sierpinski", "Sierpinski Tetrahedron", "A 256-tetrahedron fractal that tumbles, breathes, and is lit by a colour-cycling light.", "IndexedFaceSet, per-vertex Color, animated DirectionalLight", "drag to orbit"),
 ("equalizer", "Ripple Equalizer", "A 13x13 grid of bars driven by a travelling radial wave, like a sound visualiser.", "169 PositionInterpolators (used as scale) on one TimeSensor", "drag to orbit"),
 ("cradle", "Newton's Cradle", "Five chrome balls and the classic click-clack, with a hand-sampled pendulum.", "OrientationInterpolator sampled from cos(), nested pivots", "watch"),
 ("whack", "Whack-a-Mole", "Nine moles pop up on their own clocks. Click one to squash it and flash red.", "TouchSensor -> TimeSensor -> Position/ColorInterpolator, no scripts", "click the moles"),
 ("tunnel", "Rainbow Tunnel", "An endless seamless fly-through of glowing rings, with fog and a slow roll.", "Fog, emissive materials, looping translation of the world", "watch"),
 ("solar", "Tiny Solar System", "Sun, four planets and a moon on spinning orbit pivots.", "TimeSensor + OrientationInterpolator", "drag to orbit"),
 ("bounce", "Bouncing Ball", "A ball that squashes and stretches as it hops across a lawn.", "two PositionInterpolators on one clock", "watch"),
 ("touch", "Click Me", "Three cubes. Click one and it flips and changes colour.", "TouchSensor -> TimeSensor -> Color/OrientationInterpolator", "click the cubes"),
]
