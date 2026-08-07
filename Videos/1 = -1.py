
from manim import *
import numpy as np


TITLE = "Proof that -1 = 1"



BG_COLOUR = "#0d0d14"

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 15

config.frame_height = 16
config.frame_width = config.frame_height * config.pixel_width / config.pixel_height


class Video(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOUR

        self.title()
        self.proof()
        self.final_eq_emph()

        self.final_show()

        self.end()

    def title(self):
        title = Text(TITLE, font_size=72, color=WHITE, weight=BOLD)
        title.set_color_by_gradient(BLUE, GREEN, YELLOW, RED)

        title.set(width=min(title.width, config.frame_width - 1))

        title.to_edge(UP, buff=0.8)
        self.play(Write(title), run_time=1.2)

        self.title_mobject = title

    def proof(self):
        lines = [
            r"i = \sqrt{-1}",
            r"i^2 = (\sqrt{-1})^2",
            r"i^2 = \sqrt{-1} \cdot \sqrt{-1}",
            r"i^2 = \sqrt{(-1) \cdot (-1)}",
            r"i^2 = \sqrt{1}",
            r"i^2 = 1",
            r"-1 = 1",
        ]

        equations = [
            MathTex(line, font_size=56, color=WHITE) for line in lines
        ]
        for eq in equations:
            eq.set(width=min(eq.width, config.frame_width - 1.5))

        group = VGroup(*equations).arrange(DOWN, buff=0.55)
        group.move_to(ORIGIN + DOWN * 0.3)

        for eq in equations:
            self.play(Write(eq), run_time=0.8)
            self.wait(0.7)

        self.proof_group = group
        self.final_equation = equations[-1]

    def final_eq_emph(self):
        self.box = SurroundingRectangle(self.final_equation, color=RED, buff=0.3)
        self.play(Create(self.box), run_time=0.6)

        self.play(
            self.final_equation.animate.set_color(RED),
            Flash(self.final_equation, color=RED, flash_radius=1.0),
            run_time=0.8,
        )

        self.wait(1)

    def final_show(self):
        self.play(
            self.proof_group.animate.set_opacity(0.0),
            self.final_equation.animate.move_to(ORIGIN + UP * 0.2).set_color(WHITE),
            self.box.animate.set_opacity(0.0),
            run_time=1.0,
        )
        self.text = Text("Can you spot the error?", font_size=18, color=WHITE).set_opacity(0.8)
        self.text.set(width=min(self.text.width, config.frame_width - 1.5))
        self.text.next_to(self.final_equation, DOWN, buff=1.6)
        self.play(
            self.final_equation.animate.scale(1.5),
            run_time=0.5,
        )
        self.outline_rect = SurroundingRectangle(self.final_equation, color=WHITE, buff=0.6, )
        self.outline_rect.point_from_proportion(0.1)
        self.play(
            Create(self.outline_rect),
            Write(self.text),
            run_time=0.5,
        )
 
        
        self.wait(1.0)

    def end(self):
        self.play(
            Uncreate(self.proof_group),
            Uncreate(self.final_equation),
            Uncreate(self.final_equation),
            Uncreate(self.box),
            Uncreate(self.title_mobject),
            Uncreate(self.outline_rect),
            run_time=0.5,
        )
        self.play(
            Uncreate(self.text),
            run_time=0.2,
        )
    
