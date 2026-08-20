import inspect
import math
import numpy as np
import sympy as sp
from manim import *
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from autograph import AutoGraph, _build_layout, video, Spotlight

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_height = 16.0
config.frame_width = 9.0

config.frame_rate = 60  # for dev, use 60 for production

# CONF

TITLE = "Function Dance"

x = sp.Symbol("x")
y = sp.Symbol("y")
J = sp.Symbol("J")
mu, sigma = sp.symbols('mu sigma', real=True, positive=True)
C = 0.2

def maclaurin_label(n, is_sin=True):
    terms = []
    for k in range(n):
        power = 2 * k + 1 if is_sin else 2 * k
        sign = "-" if k % 2 else "+"

        if power == 0:
            term = "1"
        elif power == 1:
            term = "x"
        else:
            term = f"\\frac{{x^{{{power}}}}}{{{power}!}}"

        if k == 0:
            terms.append(f"-{term}" if sign == "-" else term)
        else:
            terms.append(f"{sign} {term}")

    return " ".join(terms)

COLOR1 = PINK
COLOR2 = BLUE
COLOR3 = PURPLE
COLOR4 = RED
COLOR5 = ORANGE
COLOR6 = GREEN
COLOR7 = TEAL
COLOR8 = PINK

DRUNTIME = 0.3
DWAITAFTER = 0.2

SQUARECONSTANT = 0.3

STEPS = [
    # x^2 -> x^7
    *[
        {
            "sp": SQUARECONSTANT*x**i if i > 1 else SQUARECONSTANT*3*x,
            "label": f"x^{{{i}}}", # make sure x^{10} doesn't render as x^{1}0
            "color": interpolate_color(COLOR1, COLOR2, t),
            "run_time": DRUNTIME,
            "wait_after": DWAITAFTER,
        }
        for i, t in zip(range(1, 11), np.linspace(0, 1, 10)) # +1 for the upbeat
    ],

    # x^2 + y^2 = 9 -> x^7 + y^7 = 9
    *[
        {
            "sp": x**i + y**i - 9,
            "label": f"x^{{{i}}} + y^{{{i}}} = 9",
            "color": interpolate_color(COLOR2, COLOR3, t),
            "run_time": DRUNTIME,
            "wait_after": DWAITAFTER,
        }
        for i, t in zip(range(2, 6), np.linspace(0, 1, 4))
    ],

    # sin(), cos()
    *[
        {
            "sp": sp.sin(x) if i % 2 == 0 else sp.cos(x),
            "label": "\\sin(x)" if i % 2 == 0 else "\\cos(x)",
            "color": interpolate_color(COLOR3, COLOR4, t),
            "run_time": DRUNTIME,
            "wait_after": DWAITAFTER,
        }
        for i, t in zip(range(2), np.linspace(0, 1, 2))
    ],

    # gaussian (bell curve)
    {
        "function": lambda x: 5*((1 / math.sqrt(2 * math.pi)) * math.exp(-x**2 / 2)),
        "label": r"\frac{1}{\sigma \sqrt{2\pi}} e^{-\frac{x^2}{2}}",
        "color": COLOR4,
        "run_time": 0.15,
        "wait_after": 0.1,
    },

    # -sin(), -cos()
    *[
        {
            "sp": -sp.sin(x) if i % 2 == 0 else -sp.cos(x),
            "label": "-\\sin(x)" if i % 2 == 0 else "-\\cos(x)",
            "color": interpolate_color(COLOR3, COLOR4, t),
            "run_time": DRUNTIME,
            "wait_after": DWAITAFTER,
        }
        for i, t in zip(range(2), np.linspace(0, 1, 2))
    ],

# Maclaurin series for sin(x), 2 through 5 terms
*[
    {
        "sp": sum(((-1) ** k) * x ** (2 * k + 1) / sp.factorial(2 * k + 1) for k in range(n)),
        "label": maclaurin_label(n, is_sin=True),
        "color": interpolate_color(COLOR4, COLOR5, t),
        "run_time": DRUNTIME,
        "wait_after": DWAITAFTER,
    }
    for n, t in zip(range(2, 6), np.linspace(0, 1, 4))
],

# Maclaurin series for cos(x), 2 through 5 terms
*[
    {
        "sp": sum(((-1) ** k) * x ** (2 * k) / sp.factorial(2 * k) for k in range(n)),
        "label": maclaurin_label(n, is_sin=False),
        "color": interpolate_color(COLOR5, COLOR6, t),
        "run_time": DRUNTIME,
        "wait_after": DWAITAFTER,
    }
    for n, t in zip(range(2, 6), np.linspace(0, 1, 4))
],

    {
        "label": r"e^{-\ln(x)}",
        "function": lambda x: math.exp(-math.log(x)),
        "color": COLOR7,
        "run_time": DRUNTIME,
        "wait_after": DWAITAFTER,
    },
    # -e^{-ln(x)}, -e^{-ln(-x)}, e^{-ln(-x)}
    {
        "label": r"-e^{-\ln(x)}",
        "function": lambda x: -math.exp(-math.log(x)),
        "color": COLOR8,
        "run_time": DRUNTIME,
        "wait_after": DWAITAFTER,
    },
    {
        "label": r"-e^{-\ln(-x)}",
        "function": lambda x: -math.exp(-math.log(-x)),
        "color": COLOR1,
        "run_time": DRUNTIME,
        "wait_after": DWAITAFTER,
    },
    {
        "label": r"e^{-\ln(-x)}",
        "function": lambda x: math.exp(-math.log(-x)),
        "color": COLOR2,
        "run_time": DRUNTIME,
        "wait_after": DWAITAFTER,
    },

    # x^2, ±√x, -x^2, ±√(-x)
    {
        "sp": x**2,
        "label": r"y = x^2",
        "color": COLOR3,
        "run_time": DRUNTIME,
        "wait_after": DWAITAFTER,
    },
    {
        "function": lambda x, y: x-y**2, # x = y^2
        "label": r"y^2 = x",
        "color": COLOR4,
        "run_time": DRUNTIME,
        "wait_after": DWAITAFTER,
    },
    {
        "sp": -x**2,
        "label": r"y = -x^2",
        "color": COLOR5,
        "run_time": DRUNTIME,
        "wait_after": DWAITAFTER,
    },
    {
        "function": lambda x, y: x+y**2, # x = -y^2
        "label": r"y^2 = -x",
        "color": COLOR6,
        "run_time": DRUNTIME,
        "wait_after": DWAITAFTER,
    },
    


    # x^7 -> x^2
    *[
        {
            "sp": SQUARECONSTANT*x**i,
            "label": f"x^{{{i}}}", # make sure x^{10} doesn't render as x^{1}0
            "color": interpolate_color(COLOR6, COLOR1, t),
            "run_time": DRUNTIME,
            "wait_after": DWAITAFTER,
        }
        for i, t in zip(range(7, 1, -1), np.linspace(0, 1, 6)) # -2 for the ad, -1 for the upbeat
    ],
]
# runwaittimes = {
#     0: [3, 4.5],
#     1: [3, 2],
#     2: 2.5,
#     3: 5,
#     4: [3, 4.5],
#     5: [3, 2],
#     6: 2.5,
#     7: 2.5,
#     8: 2.5,
#     25: [3, 4.5],
#     26: [3, 2],
#     27: 2.5,
#     28: 5,
#     29: [3, 4.5],
#     30: [3, 2],
#     31: 2.5,
#     32: 2.5,
#     33: 2.5,
# }
STEPSlen = len(STEPS)
print(f"STEPSlen = {STEPSlen}")
SPECIALFIX = [4, 1]
runwaittimes = {
    6: 2.5,
    7: 2.5,
    16: [2, 3], # bell curve
    17: 2.5,
    18: 2.5,
    27: 5, # e^{-\ln(x)}
    STEPSlen-3: 2.5,
    STEPSlen-2: 2.5,
}

for i in range(len(STEPS)):
    if not i in runwaittimes:
        continue
    if type(runwaittimes[i]) in (int, float):
        runwaittimes[i] = [runwaittimes[i]*3/5, runwaittimes[i]*2/5]
    STEPS[i]["run_time"] = runwaittimes[i][0] / 10
    STEPS[i]["wait_after"] = runwaittimes[i][1] / 10

def build_layout():
    """
    central design
    empty text/tex/mathtex = classified as label
    return all the elements for autodetect
    or return something looking like
    {
        "autographs": [AutoGraph(), AutoGraph()],
        "labels": [MathTex(), MathTex()],
        "others": [Text(), Text()],
    }
    """

    # title = Text(TITLE, font_size=72, color=WHITE, weight=BOLD)
    # title.to_edge(UP, buff=1.6)
    title = Text(TITLE, font_size=48, color=WHITE, weight=BOLD)
    title.set_color_by_gradient(BLUE, GREEN)
    title.set(width=min(title.width, config.frame_width - 1))
    title.to_edge(UP, buff=0.8)


    # Limiting height to the visible axes range (boolean toggle)
    top = AutoGraph(x_length=4.5, y_length=4.5, autoratio=1, y_limit=True)
    top.to_edge(UP, buff=1.6+0.6)
#    top.next_to(title, DOWN, buff=0.6)

    bottom = AutoGraph(x_length=4.5, y_length=4.5, autoratio=1, y_limit=True)
    bottom.to_edge(DOWN, buff=1.0)

    spotlight = Spotlight()

    label = MathTex("x", font_size=60).move_to(ORIGIN + DOWN * 0.6)
    label.anchor = ORIGIN + DOWN * 0.6
    label.is_label = True
    #box = SurroundingRectangle(label, color=WHITE, buff=0.2).move_to(ORIGIN + DOWN * 0.6)
#    boxlambda = lambda: RoundedRectangle(corner_radius=0.2, color=WHITE, stroke_width=4).surround(label, buff=1)
    # just use the plain SurroundingRectangle for now, since the RoundedRectangle is not working well with the label
    boxlambda = lambda: SurroundingRectangle(label, buff=0.2)
    box = boxlambda().move_to(ORIGIN + DOWN * 0.6).set_color(COLOR1.lighter())
    box.anchor = ORIGIN + DOWN * 0.6 # this doesn't work

    # custom property
    bottom.ccolor = True
    top.ccolor = True
    box.ccolor = True

    box.redeclare = boxlambda

    # return a simple tuple by default (title, top, bottom, spotlight, label, box)
    return title, top, bottom, spotlight, label, box

# END CONF







class Video(Scene):
    def construct(self):
        self.camera.background_color = "#0d0d14"
        video(self, build_layout, STEPS, x, y)
        self.end()

    def end(self):
        from autograph import Sub
        Sub(self, run_time=0.5)
        self.wait(0.5)
