SPEED = 2 / 3

from manim import *
import numpy as np

from time import perf_counter as time

# START BOILER CONF

TITLE = "Pythagorean Theorem"

# END BOILER CONF


BG_COLOUR = "#0d0d14"

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 60  # for dev, use 60 for production

config.frame_height = 16
config.frame_width = config.frame_height * config.pixel_width / config.pixel_height

# palette — legs / hyp colors stay consistent across triangle, labels, squares
A_COLOR = "#4fb2ff"   # leg a
B_COLOR = "#6ee7a0"   # leg b
C_COLOR = "#ff6b6b"   # hypotenuse c
TRI_FILL = "#ffd166"
WHITE_ISH = "#f5f5f5"

try:
    dbgf = open("/tmp/manim_dbg", "w")
except:
    pass

def colorfunc(c):
    return interpolate_color(ManimColor(c), WHITE, 0.7)

LABELFONTSIZE = 128

class Boilerplate(Scene):
    def construct(self):
        # takes 6.33
        # 7.33
        global SPEED
        SPEED = SPEED * 7.33 / 6.33
        self.camera.background_color = BG_COLOUR

        # 3-4-5 triangle, clean integers so the squares tile perfectly
        self.a, self.b, self.c = 3, 4, 5
        self.s = self.a + self.b  # big square side length

        times = {                    }

        verystart = time()
        self.verystart = verystart
        self.title()
        end = time()
        times["title"] = end - verystart
        tri = self.intro_triangle()
        end = time()
        times["intro_triangle"] = end - verystart
        self.build_config_a(tri)
        end = time()
        times["build_config_a"] = end - verystart
        self.morph_to_config_b()
        end = time()
        times["morph_to_config_b"] = end - verystart
        self.show_equation()
        end = time()
        times["show_equation"] = end - verystart
        self.wait(1 * SPEED)
        self.end()
        end = time()
        times["end"] = end - verystart
        import rich
        rich.print_json(data=times, indent=2, highlight=True)

    # ---------------------------------------------------------------- title
    def title(self):
        self.spawn_eq()
        title = Text(TITLE, font_size=72, color=WHITE, weight=BOLD)
        title.set_color_by_gradient(BLUE, GREEN, YELLOW, RED)
        title.set(width=min(title.width, config.frame_width - 1))
        title.to_edge(UP, buff=1.6)
        self.add(self.eq)
        self.play(Write(title), run_time=1.2 * SPEED)
        self.title_mobject = title

    # ------------------------------------------------------------- helpers
    def pt(self, x, y):
        """Square-local coords (origin at square's bottom-left) -> scene
        coords, centered on the square and nudged down under the title."""
        s = self.s
        return np.array([x - s / 2, y - s / 2, 0.0]) + np.array([0.0, 1.5, 0.0])

    def poly(self, pts, **kwargs):
        return Polygon(*[self.pt(*p) for p in pts], **kwargs)

    def edge_label_pos(self, mobject, i1, i2, offset=0.22):
        vertices = np.array(mobject.get_vertices())
        p1 = vertices[i1]
        p2 = vertices[i2]
        mid = (p1 + p2) / 2
        edge_vec = p2 - p1
        normal = np.array([-edge_vec[1], edge_vec[0], 0.0])
        norm = np.linalg.norm(normal)
        if norm > 0:
            normal = normal / norm

        centroid = np.mean(vertices, axis=0)
        if np.dot(normal, centroid - mid) > 0:
            normal = -normal

        return mid + normal * offset

    def triangle_label_group(self, triangle, offset=0.2, include_c=True):
        label_a = MathTex("a", color=A_COLOR, font_size=46)
        label_b = MathTex("b", color=B_COLOR, font_size=46)
        label_a.move_to(self.edge_label_pos(triangle, 0, 1, offset=offset))
        label_b.move_to(self.edge_label_pos(triangle, 0, 2, offset=offset))

        labels = VGroup(label_a, label_b)
        if include_c:
            label_c = MathTex("c", color=C_COLOR, font_size=46)
            label_c.move_to(self.edge_label_pos(triangle, 1, 2, offset=offset))
            labels.add(label_c)

        labels.set_z(0.9)
        return labels

    # ------------------------------------------------------ intro triangle
    def intro_triangle(self):
        a, b, c = self.a, self.b, self.c

        # a big, standalone right triangle below the title to build intuition first
        big_scale = 1.35
        p0 = np.array([-a, -b, 0]) * big_scale / 2 + UP * 2.2
        pA = p0 + RIGHT * a * big_scale
        pB = p0 + UP * b * big_scale

        tri = Polygon(p0, pA, pB, color=WHITE_ISH, fill_color=TRI_FILL,
                       fill_opacity=0.85, stroke_width=4)

        label_a = MathTex("a", color=A_COLOR, font_size=64).next_to(
            (p0 + pA) / 2, DOWN, buff=0.2)
        label_b = MathTex("b", color=B_COLOR, font_size=64).next_to(
            (p0 + pB) / 2, LEFT, buff=0.2)
        label_c = MathTex("c", color=C_COLOR, font_size=64).move_to(
            (pA + pB) / 2 + np.array([0.55, 0.35, 0]))

        """
        self.eq = MathTex("a^2", "+", "b^2", "=", "c^2", font_size=88)
        self.eq[0].set_color(A_COLOR)
        self.eq[2].set_color(B_COLOR)
        self.eq[4].set_color(C_COLOR)
        self.eq.center()
        """


        qeq = MathTex("a^2", "+", "b^2", "=", "c^2", color=WHITE, font_size=64)
        qeq[0].set_color(A_COLOR)
        qeq[2].set_color(B_COLOR)
        qeq[4].set_color(C_COLOR)
        qquestion = Text("But why? ", color=WHITE, font_size=48)
        qquestion.set_color_by_gradient(interpolate_color(ManimColor(A_COLOR), WHITE, 0.3), interpolate_color(ManimColor(B_COLOR), WHITE, 0.3))

        qquestion.next_to(qeq, DOWN, buff=0.8)

        VGroup(qeq, qquestion).arrange(DOWN, buff=0.3).next_to(tri, DOWN, buff=1.8)


        self.play(
            AnimationGroup(
                ReplacementTransform(self.eq, qeq),
                AnimationGroup(
                    Create(tri),
                    Write(label_a), Write(label_b), Write(label_c),
                ),
                lag_ratio=0.2,
            ),
            run_time=0.8 * SPEED
        )
        self.wait(0.5 * SPEED)
        self.play(
            Write(qquestion),
            run_time=0.6 * SPEED,
        )
        self.wait(1 * SPEED)

        self.play(
            LaggedStart(
                *[Unwrite(qquestion), Unwrite(qeq)],
                lag_ratio=0.3,
            ),
            run_time=0.6 * SPEED,
        )

        self.tri_group = VGroup(tri, label_a, label_b, label_c)
        return tri  # the raw triangle mobject, reused below

    # ------------------------------------------------------- config A build
    def build_config_a(self, tri):
        global SPEED
        a, b = self.a, self.b

        # target: TA1, sitting flush in the corner of the big square
        ta1 = self.poly([(0, 0), (a, 0), (0, b)])
        ta1.set_stroke(WHITE_ISH, width=3)
        ta1.set_fill(TRI_FILL, opacity=0.85)

        # morph the triangle itself while keeping the original intro labels visible
        self.play(
            FadeOut(self.tri_group[1:], run_time=0.5 * SPEED),
            Transform(tri, ta1, run_time=1.0 * SPEED),
        )

        center = self.pt(self.s / 2, self.s / 2)

        # spin up 3 more copies by rotating the first 90/180/270 about the
        # square's center — same triangle, just spun into place
        copies = VGroup()
        for k in (1, 2, 3):
            cp = tri.copy()
            cp.rotate(k * PI / 2, about_point=center)
            copies.add(cp)

        self.play(
            LaggedStart(*[Create(cp) for cp in copies], lag_ratio=0.25),
            run_time=1.3 * SPEED,
        )
        self.wait(0.2 * SPEED)

        self.triangles = VGroup(tri, *copies)  # TA1..TA4, in this order
        self.triangles.set_z(1.2)

        self.triangle_label_groups = VGroup()
        for triangle in self.triangles:
            self.triangle_label_groups.add(self.triangle_label_group(triangle, offset=0.2, include_c=True))
        self.play(FadeIn(self.triangle_label_groups), run_time=0.4 * SPEED)

        # outer square outline, for context
        outer = self.poly([(0, 0), (self.s, 0), (self.s, self.s), (0, self.s)])
        outer.set_stroke(WHITE_ISH, width=2, opacity=0.5)
        outer.set_z(0.6)
        self.play(Create(outer), run_time=0.5 * SPEED)
        self.outer_square = outer

        # the tilted inner square left uncovered by the pinwheel: area c^2
        c_poly = self.poly([(a, 0), (self.s, a), (b, self.s), (0, b)])
        c_poly.set_stroke(C_COLOR, width=4)
        c_poly.set_fill(C_COLOR, opacity=0.55)
        c_poly.set_z(0.2)

        c_label = MathTex("c^2", color=colorfunc(C_COLOR), font_size=LABELFONTSIZE)
        c_label.move_to(center)

        c_sq = VGroup(c_poly, c_label)
        c_poly.set_z_index(0)
        c_poly.set_z(0.2)
        c_label.set_z_index(10)
        c_label.set_z(0.3)

        c_target = c_label.get_center()
        c_edge_a = self.triangle_label_groups[0][2]
        c_edge_b = self.triangle_label_groups[1][2]

        self.play(
            c_edge_a.animate.move_to(c_target),
            c_edge_b.animate.move_to(c_target),
            run_time=0.8 * SPEED,
        )
        c_label.set_opacity(1)
        self.play(
            FadeIn(c_poly),
            FadeIn(c_label.set_opacity(1)),
            FadeOut(c_edge_a),
            FadeOut(c_edge_b),
            FadeOut(self.triangle_label_groups),
            run_time=0.5 * SPEED,
        )
        c_label.set_opacity(1)
        self.remove(self.triangle_label_groups.set_opacity(0))
#        self.play(Indicate(c_sq, color=C_COLOR, scale_factor=1.03), run_time=0.7 * SPEED)
        self.play(Indicate(c_sq, color=C_COLOR, scale_factor=1.03), run_time=0.5 * SPEED)
        SPEED = SPEED * 6.33 / 7.33
        self.wait(0.3 * SPEED) # self.wait(1.5 * SPEED)

        self.square_row_y = self.pt(0, 0)[1] - 2.2
        c_rotation = -np.arctan(a / b)
        c_center = c_poly.get_center()
        self.play(
            Rotate(c_poly, angle=c_rotation, about_point=c_center),
            c_sq.animate.scale(0.5).move_to(np.array([0.0, self.square_row_y, 0.0])),
            run_time=0.8 * SPEED,
        )
        c_label.set_opacity(1)
        self.wait(0.3 * SPEED)

        self.c_sq = c_sq
        self.c_square_group = c_sq

    # -------------------------------------------------- morph to config B
    def morph_to_config_b(self):
        a, b, s = self.a, self.b, self.s

        # same 4 triangles, new spots inside the SAME outer square
        tb_pts = [
            [(0, 0), (a, 0), (0, b)],           # TB1 — already sitting here
            [(a, 0), (a, b), (0, b)],           # TB2
            [(a, b), (s, b), (a, s)],           # TB3
            [(s, b), (s, s), (a, s)],           # TB4
        ]
        targets = VGroup(*[
            self.poly(p, color=WHITE_ISH, fill_color=TRI_FILL, fill_opacity=0.85,
                      stroke_width=3)
            for p in tb_pts
        ])

        sq_a_poly = self.poly([(0, b), (a, b), (a, s), (0, s)])
        sq_a_poly.set_stroke(A_COLOR, width=4)
        sq_a_poly.set_fill(A_COLOR, opacity=0.55)
        sq_a_poly.set_z(0.2)

        sq_b_poly = self.poly([(a, 0), (s, 0), (s, b), (a, b)])
        sq_b_poly.set_stroke(B_COLOR, width=4)
        sq_b_poly.set_fill(B_COLOR, opacity=0.55)
        sq_b_poly.set_z(0.2)

        label_a2 = MathTex("a^2", color=colorfunc(A_COLOR), font_size=LABELFONTSIZE).move_to(
            self.pt(a / 2, b + (s - b) / 2))
        label_b2 = MathTex("b^2", color=colorfunc(B_COLOR), font_size=LABELFONTSIZE).move_to(
            self.pt(a + (s - a) / 2, b / 2))

        a_sq = VGroup(sq_a_poly, label_a2)
        sq_a_poly.set_z_index(0)
        sq_a_poly.set_z(0.2)
        label_a2.set_z_index(99)
        label_a2.set_z(0.3)

        b_sq = VGroup(sq_b_poly, label_b2)
        sq_b_poly.set_z_index(0)
        sq_b_poly.set_z(0.2)
        label_b2.set_z_index(99)
        label_b2.set_z(0.3)

        a_target = label_a2.get_center()
        b_target = label_b2.get_center()

        # keep the c^2 square visible while the pieces slide into the new
        # config so we can line the three squares up later
        self.play(
            *[Transform(self.triangles[i], targets[i]) for i in range(4)],
            run_time=1.4 * SPEED,
        )

        a_label_bottom = MathTex("a", color=A_COLOR, font_size=46)
        a_label_right = MathTex("a", color=A_COLOR, font_size=46)
        b_label_left = MathTex("b", color=B_COLOR, font_size=46)
        b_label_top = MathTex("b", color=B_COLOR, font_size=46)

        slabels1 = self.triangle_label_group(self.triangles[0], include_c=False)
        slabels2 = self.triangle_label_group(self.triangles[3], include_c=False)
        slabels = VGroup(slabels1, slabels2)
        # these are static labels, they don't move

        a_label_bottom.move_to(self.edge_label_pos(self.triangles[1], 1, 2, offset=0.2))
        a_label_right.move_to(self.edge_label_pos(self.triangles[2], 0, 2, offset=0.2))
        b_label_left.move_to(self.edge_label_pos(self.triangles[1], 0, 1, offset=0.2))
        b_label_top.move_to(self.edge_label_pos(self.triangles[2], 0, 1, offset=0.2))

        config_b_labels = VGroup(a_label_bottom, a_label_right, b_label_left, b_label_top)
        config_b_labels.set_z(0.9)
        self.play(FadeIn(config_b_labels), FadeIn(slabels), run_time=0.4 * SPEED)

        self.play(
            a_label_bottom.animate.move_to(a_target),
            a_label_right.animate.move_to(a_target),
            b_label_left.animate.move_to(b_target),
            b_label_top.animate.move_to(b_target),
            run_time=0.8 * SPEED,
        )
        label_a2.set_opacity(1); label_b2.set_opacity(1)
        self.play(
            FadeIn(sq_a_poly),
            FadeIn(sq_b_poly),
            FadeIn(label_a2.set_opacity(1)),
            FadeIn(label_b2.set_opacity(1)),
            FadeOut(config_b_labels),
            FadeOut(slabels1),
            FadeOut(slabels2),
            run_time=0.6 * SPEED,
        )
        label_a2.set_opacity(1); label_b2.set_opacity(1)
        self.play(
            Indicate(a_sq, color=A_COLOR, scale_factor=1.03),
            Indicate(b_sq, color=B_COLOR, scale_factor=1.03),
            run_time=0.7 * SPEED,
        )
        self.wait(0.6 * SPEED)

        self.a_sq = a_sq
        self.b_sq = b_sq
        label_a2.set_opacity(1); label_b2.set_opacity(1)
        self.play(
            a_sq.animate.scale(0.5),
            b_sq.animate.scale(0.5),
            run_time=0.4 * SPEED,
        )
        row_group = VGroup(self.a_sq, self.b_sq, self.c_sq)
        self.play(
            row_group.animate.arrange(RIGHT, buff=0.35).set_y(self.square_row_y),
            run_time=0.8 * SPEED,
        )
        self.wait(0.3 * SPEED)

        self.play(FadeOut(self.triangles), FadeOut(self.outer_square), run_time=0.6 * SPEED)
        self.wait(0.2 * SPEED)

        self.config_b_group = VGroup(self.a_sq, self.b_sq, self.c_sq)

    def spawn_eq(self):
        self.eq = MathTex("a^2", "+", "b^2", "=", "c^2", font_size=88)
        self.eq[0].set_color(A_COLOR)
        self.eq[2].set_color(B_COLOR)
        self.eq[4].set_color(C_COLOR)
        self.eq.center()

    # ------------------------------------------------------------ equation
    def show_equation(self):
        eq = MathTex("a^2", "+", "b^2", "=", "c^2", font_size=88)
        eq[0].set_color(A_COLOR)
        eq[2].set_color(B_COLOR)
        eq[4].set_color(C_COLOR)
        eq.center()
        plus = MathTex("+", font_size=80, color=WHITE)
        equals = MathTex("=", font_size=80, color=WHITE)
        plus.next_to(self.a_sq, RIGHT, buff=-0.1)
        equals.next_to(self.b_sq, RIGHT, buff=0.1)

        self.play(Write(plus), Write(equals), run_time=0.6 * SPEED)
        self.wait(0.3 * SPEED)

        self.box = SurroundingRectangle(eq, color=WHITE, buff=MED_LARGE_BUFF)
        self.play(
            TransformMatchingShapes(
                VGroup(self.a_sq[1].copy(), plus.copy(), self.b_sq[1].copy(), equals.copy(), self.c_sq[1].copy()),
                eq,
            ),
            run_time=1.2 * SPEED,
        )
        self.play(
            Create(self.box),
            FadeOut(self.a_sq, self.b_sq, self.c_sq, plus, equals),
            run_time=0.5 * SPEED,
        )

        self.remove(self.a_sq, self.b_sq, self.c_sq, plus, equals)

        self.eq_group = VGroup(eq)

        # ts = 14.6
        # beatdrop at 15.0

    # ------------------------------------------------------------------ end
    def end(self):
        # let's keep the clean loop, in favor of it over the ad

        self.play(
            Uncreate(self.title_mobject),
            Uncreate(self.box),
            run_time=0.6 * SPEED,
        )

        # pfp = MathTex(r"y", font_size=160)
        # pfp.set_color(RED) # FC6255
        
        # handle = Text("@MathRendered", font_size=48)
        # handle.set_color_by_gradient(BLUE, GREEN, YELLOW)
        
        # content = VGroup(pfp, handle)
        # content.arrange(DOWN, buff=0.6)
        # content.move_to(ORIGIN)
        
        # b4 = VGroup(self.title_mobject, self.eq_group, self.box)

        # self.play(
        #     Transform(b4, content),
        #     # Uncreate(self.title_mobject),
        #     # FadeOut(self.eq_group),
        #     # Uncreate(self.box),
        #     # Create(content),
        #     run_time=0.6 * SPEED,
        # )
        # self.wait(0.4 * SPEED)
