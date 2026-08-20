#!/usr/bin/env -S sh -c 'manim -pql "$0" Video'
print("class Video is the video. ")
print("this is also a self-compiling binary, so if you're on linux or mac you can execute it directly")
from manim import *
import numpy as np


TITLE = "Taylor Series"
DEGREENO = 10



BG_COLOUR = "#0d0d14"

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 60

config.frame_height = 16
config.frame_width = 9


class _boilerplate(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOUR
        self.title()
        self.wait(2)
        self.end()

    def title(self):
        title = Text(TITLE, font_size=72, color=WHITE, weight=BOLD)
        title.set_color_by_gradient(BLUE, GREEN, YELLOW, RED)
        title.set(width=min(title.width, config.frame_width - 1))
        title.to_edge(UP, buff=1.6)
        self.play(Write(title), run_time=1)
        self.title_mobject = title

    def end(self):
        pass


from manim import *
import numpy as np


def taylor_sin_factory(n):
    def f(x):
        term = x
        total = term
        k = 1
        while k < n:
            k2 = k + 2
            term = -term * (x * x) / (k2 * (k2 - 1))
            total += term
            k = k2
        return total
    return f


def sin_term_latex(n):
    if n == 1:
        return "x"
    m = (n - 1) // 2
    sign = "-" if m % 2 == 1 else "+"
    return f"{sign} \\frac{{x^{{{n}}}}}{{{n}!}}"


def find_extent(f, x_max, y_max=None, steps=600):
    dx = x_max / steps
    last_good = 0.0
    for i in range(1, steps + 1):
        x = i * dx
        try:
            y = f(x)
        except OverflowError:
            return last_good
        if not np.isfinite(y):
            return last_good
        if (y_max is not None) and (abs(y) > y_max):
            return last_good
        last_good = x
    return x_max


class Video(_boilerplate):
    def construct(self):
        self.camera.background_color = BG_COLOUR
        self.title()
        self.taylor_demo()

        self.wait(0.4)
        self.reveal_general_formula()

        self.end()

    def taylor_demo(self):
        self.x_max = 3 * PI
        self.y_max = 2.2

        axes = Axes(
            x_range=[-self.x_max, self.x_max, PI],
            y_range=[-self.y_max, self.y_max, 1],
            x_length=8.4,
            y_length=9.2,
            tips=False,
            axis_config={"color": GREY_D, "stroke_width": 3},
        )
        axes.move_to(DOWN * 3.0)
        self.axes = axes
        self.play(Create(axes), run_time=0.2)

        sin_curve = axes.plot(np.sin, x_range=[-self.x_max, self.x_max], color=YELLOW, stroke_width=6)
        sin_label = MathTex(r"\sin(x)", color=YELLOW).scale(1.1)
        sin_label.next_to(self.title_mobject, DOWN, buff=0.55)
        self.play(Create(sin_curve), Write(sin_label), run_time=0.8)
        self.sin_curve = sin_curve
        self.sin_label = sin_label

        self._formula_degree = -1
        self._terms = []
        self.formula_mobj = None
        self._collapsed = False
        self._n_lead = 0
        self._last_term_index = None

        self._graph_degree = -1
        self.poly_graph = None

        for _ in range(7):
            formula_anims, next_formula = self.get_formula_animations()
            graph_anims = self.get_graph_animations()

            self.play(*formula_anims, *graph_anims, run_time=0.7)

            if next_formula is not None:
                self.add(next_formula)
                self.formula_mobj = next_formula

            self.wait(0.3)

        for _ in "12":
            formula_anims, next_formula = self.get_formula_animations()
            graph_anims = self.get_graph_animations()

            self.play(*formula_anims, *graph_anims, run_time=0.5)

            if next_formula is not None:
                self.add(next_formula)
                self.formula_mobj = next_formula










    def _fits_in_frame(self, parts):
        max_w = config.frame_width - 1
        test = MathTex(*parts, color=WHITE).scale(0.85)
        return test.width <= max_w


    def get_formula_animations(self):
        self._formula_degree += 2
        n = self._formula_degree
        self._terms.append(sin_term_latex(n))

        if self._collapsed:
            return self._collapsed_step_animations()

        candidate_parts = [r"\sin(x)", r"\approx", *self._terms]
        if self._fits_in_frame(candidate_parts):
            candidate = MathTex(*candidate_parts, color=WHITE).scale(0.85)
            new_formula = candidate
            if self.formula_mobj is None:
                new_formula.next_to(self.sin_label, DOWN, buff=0.6)
            else:
                new_formula.move_to(self.formula_mobj)

            if self.formula_mobj is None:
                anims = [
                    ReplacementTransform(self.sin_label, new_formula[0]),
                    GrowFromCenter(new_formula[1]),
                    GrowFromCenter(new_formula[2]),
                ]
            else:
                anims = [
                    ReplacementTransform(self.formula_mobj, new_formula[:-1]),
                    GrowFromCenter(new_formula[-1]),
                ]
            return anims, new_formula

        return self._enter_collapsed_mode()


    def _max_fitting_lead_count(self):
        max_w = config.frame_width - 1
        last_term = self._terms[-1]
        best_k = 0
        for k in range(0, len(self._terms) - 1 + 1):
            if k > len(self._terms) - 1:
                break
            lead_terms = self._terms[:k]
            if k == 0:
                parts = [r"\sin(x)", r"\approx", r"\cdots", last_term]
            else:
                parts = [r"\sin(x)", r"\approx", *lead_terms, r"\cdots", last_term]
            if self._fits_in_frame(parts):
                best_k = k
            else:
                break
        return best_k


    def _enter_collapsed_mode(self):
        self._collapsed = True
        self._n_lead = self._max_fitting_lead_count()

        lead_terms = self._terms[: self._n_lead]
        last_term = self._terms[-1]
        if self._n_lead == 0:
            parts = [r"\sin(x)", r"\approx", r"\cdots", last_term]
        else:
            parts = [r"\sin(x)", r"\approx", *lead_terms, r"\cdots", last_term]

        new_formula = MathTex(*parts, color=WHITE).scale(0.85)
        max_w = config.frame_width - 1
        if new_formula.width > max_w:
            new_formula.scale_to_fit_width(max_w)

        if self.formula_mobj is None:
            new_formula.next_to(self.sin_label, DOWN, buff=0.6)
        else:
            new_formula.move_to(self.formula_mobj)

        if self.formula_mobj is None:
            anims = [
                ReplacementTransform(self.sin_label, new_formula[0]),
                GrowFromCenter(new_formula[1]),
                *[GrowFromCenter(new_formula[i]) for i in range(2, len(parts) - 1)],
                GrowFromCenter(new_formula[-1]),
            ]
        else:
            anims = [
                ReplacementTransform(self.formula_mobj, new_formula[:-1]),
                GrowFromCenter(new_formula[-1]),
            ]

        return anims, new_formula


    def _collapsed_step_animations(self):
        max_w = config.frame_width - 1
        last_term = self._terms[-1]

        while self._n_lead > 0:
            lead_terms = self._terms[: self._n_lead]
            parts = [r"\sin(x)", r"\approx", *lead_terms, r"\cdots", last_term]
            if self._fits_in_frame(parts):
                break
            self._n_lead -= 1

        lead_terms = self._terms[: self._n_lead]
        if self._n_lead == 0:
            parts = [r"\sin(x)", r"\approx", r"\cdots", last_term]
        else:
            parts = [r"\sin(x)", r"\approx", *lead_terms, r"\cdots", last_term]

        new_formula = MathTex(*parts, color=WHITE).scale(0.85)
        if new_formula.width > max_w:
            new_formula.scale_to_fit_width(max_w)
        new_formula.move_to(self.formula_mobj)

        anims = [TransformMatchingTex(self.formula_mobj, new_formula)]
        return anims, new_formula

    def get_graph_animations(self):
        self._graph_degree += 2
        n = self._graph_degree

        f = taylor_sin_factory(n)
        r = find_extent(f, self.x_max, None)
        new_poly = self.axes.plot(f, x_range=[-r, r], color=RED, stroke_width=7)

        if self.poly_graph is None:
            self.poly_graph = new_poly
            anims = [Create(new_poly)]
        else:
            anims = [Transform(self.poly_graph, new_poly)]
            
        return anims

    def reveal_general_formula(self):
        self.play(
            FadeOut(VGroup(self.axes, self.sin_curve, self.poly_graph)),
            run_time=0.2,
        )
        self.play(
            self.formula_mobj.animate.move_to(UP * 0.3).scale(0.9),
            run_time=0.3,
        )

        sin_sigma = MathTex(
            r"\sin(x)", "=", r"\sum_{k=0}^{\infty}", r"(-1)^k\frac{x^{2k+1}}{(2k+1)!}",
            color=WHITE,
        ).scale(1.05)
        sin_sigma.move_to(self.formula_mobj)
        self.box = SurroundingRectangle(sin_sigma, color=WHITE, buff=MED_LARGE_BUFF)
        self.play(
            ShrinkToCenter(self.formula_mobj),
            FadeIn(sin_sigma),
            Create(self.box),
            run_time=0.5
        )
        self.formula_mobj = sin_sigma

        general = MathTex(
            r"f(x)", "=", r"\sum_{k=0}^{\infty}", r"\frac{f^{(k)}(0)}{k!}x^k",
            color=WHITE,
        ).scale(1.05)
        general.move_to(self.formula_mobj)
        genbox = SurroundingRectangle(general, color=WHITE, buff=MED_LARGE_BUFF)
        self.play(
            TransformMatchingTex(self.formula_mobj, general),
            Transform(self.box, genbox),
            Flash(self.formula_mobj, flash_radius=3, line_length=0.15),
            run_time=0.5,
        )
        self.formula_mobj = general
        self.wait(0.4)

        self.play(FadeOut(self.formula_mobj), Uncreate(self.box), 
            Uncreate(self.title_mobject),run_time=0.1)
