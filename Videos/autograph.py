
from manim import *
import sympy as sp
import inspect
import numpy as np

class AutoGraph(VGroup):
    def __init__(self, *args, autoratio=-1, y_limit=True, **kwargs):
        """
        when autoratio!=1 or if you don't do it yourself some functionality may break
        autoratio feature is really bad right now
        Initialise with autoratio to make the ratio of x_length to y_length equate to autoratio
        If you use autoratio, don't provide y_range value
        autoratio lacks customisability. if you want that, just do it yourself

        y_limit: If True (default), clip the function to the axes' y_range.
        """
        axes_defaults = dict(
            x_range=[-5, 5, 1],
            y_range=[-5, 5, 1],
            x_length=4.5,
            y_length=4.5,
            tips=False,
            axis_config={"include_numbers": False},
        )
        axes_defaults.update(kwargs)
        if autoratio > 0:
            # make the "stretch" ratio autoratio. so that 1 x unit corresponds to 1/autoratio y unit
            aspect_ratio = axes_defaults["x_length"] / axes_defaults["y_length"]
            x_range = axes_defaults["x_range"]
            xrange = abs(x_range[1] - x_range[0])
            # now calculate yrange based on aspect_ratio and autoratio
            yrange = xrange / (autoratio * aspect_ratio) # this way, if autoratio=1, then 1 x unit = 1 y unit on the screen
            axes_defaults["y_range"] = [-yrange / 2, yrange / 2, x_range[2]]

        super().__init__()
        self.axes = Axes(*args, **axes_defaults)
        self.add(self.axes)

        self.y_limit = y_limit
        self.graph = None

    @staticmethod
    def _arity(func):
        return len(inspect.signature(func).parameters)

    def _build(self, func, **plot_kwargs):
        n = self._arity(func)

        if n == 1:
            # standard f(x)
            if self.y_limit:
                y_min, y_max = self.axes.y_range[:2]
                x_min, x_max = self.axes.x_range[:2]
                segments = self._find_segments(func, (x_min, x_max), y_min, y_max)

                pieces = VGroup()
                for x_start, x_end in segments:
                    if x_end - x_start < 1e-6:
                        continue
                    pieces.add(self.axes.plot(func, x_range=[x_start, x_end], **plot_kwargs))
                return pieces
            return self.axes.plot(func, **plot_kwargs)

        elif n == 2:
            # Implicit f(x, y) = 0 curve.
            x_range = plot_kwargs.pop("x_range", self.axes.x_range[:2])
            y_range = plot_kwargs.pop("y_range", self.axes.y_range[:2])

            if self.y_limit:
                ay_min, ay_max = self.axes.y_range[:2]
                y_range = [max(y_range[0], ay_min), min(y_range[1], ay_max)]

            curve = ImplicitFunction(func, x_range=x_range, y_range=y_range, **plot_kwargs)
            curve.apply_function(lambda p: self.axes.c2p(*p[:2]))
            return curve

        else:
            raise ValueError(
                f"AutoGraph supports 1-arg functions (y=f(x)) or 2-arg "
                f"implicit functions (f(x,y)=0), got a function with {n} args."
            )

    def plot(self, func, run_time=0.5, **plot_kwargs):
        """
        Plot `func` on the axes.

        First call  -> returns a Create()
        Later calls -> returns a Transform()
        
        Any extra kwargs are forwarded to axes.plot() (explicit) or
        ImplicitFunction() (implicit) — e.g. color=RED, stroke_width=6.

        Returns an Animation() obj, so play it yourself
        """
        if run_time is None or run_time <= 0:
            raise ValueError(
                f"AutoGraph.plot() requires run_time > 0, got {run_time!r}."
            )

        new_graph = self._build(func, **plot_kwargs)

        if self.graph is None: # first time
            self.graph = new_graph
            self.add(self.graph)
            return Create(self.graph, run_time=run_time)

        return Transform(self.graph, new_graph, run_time=run_time)
        
    def _find_segments(self, func, x_range, y_min, y_max, samples=400):
        """Return (x_start, x_end) intervals where func(x) stays within [y_min, y_max]."""
        xs = np.linspace(x_range[0], x_range[1], samples)

        def in_range(x):
            try:
                v = func(x)
            except Exception:
                return False
            return v is not None and np.isfinite(v) and y_min <= v <= y_max

        def refine(x_lo, x_hi, lo_in):
            for _ in range(30):  # bisect to pin the crossing precisely
                x_mid = (x_lo + x_hi) / 2
                if in_range(x_mid) == lo_in:
                    x_lo = x_mid
                else:
                    x_hi = x_mid
            return (x_lo + x_hi) / 2

        segments, seg_start = [], (xs[0] if in_range(xs[0]) else None)
        prev_x, prev_in = xs[0], in_range(xs[0])

        for x in xs[1:]:
            cur_in = in_range(x)
            if cur_in != prev_in:
                crossing = refine(prev_x, x, prev_in)
                if prev_in:
                    segments.append((seg_start, crossing))
                    seg_start = None
                else:
                    seg_start = crossing
            prev_x, prev_in = x, cur_in

        if seg_start is not None:
            segments.append((seg_start, xs[-1]))
        return segments


class Spotlight(ImageMobject):
    def __init__(
        self,
        center=ORIGIN + 0.6 * DOWN,
        radius=7,
        color=None,
        resolution=512,
        max_opacity=0.5,
        falloff=2,
        **kwargs,
    ):
        # Evaluate default color inside the body to avoid using a mutable
        # value created at import time which can lead to rendering issues
        # (flashing) in some environments.
        if color is None:
            color = ManimColor('#16445A')

        r, g, b = [int(c * 255) for c in color_to_rgb(color)]

        y, x = np.ogrid[-1:1:resolution * 1j, -1:1:resolution * 1j]
        dist = np.clip(np.sqrt(x**2 + y**2), 0, 1)
        alpha = (1 - dist) ** falloff * max_opacity

        img = np.zeros((resolution, resolution, 4), dtype=np.uint8)
        img[..., 0] = r
        img[..., 1] = g
        img[..., 2] = b
        img[..., 3] = (alpha * 255).astype(np.uint8)

        super().__init__(img, **kwargs)
        self.height = radius * 2
        self.move_to(center)
        self.set_z_index(-100)

    def align_points_with_larger(self, larger_mobject):
        # ImageMobject can't do true point-alignment for Transform —
        # no-op instead of raising, so it can still live inside a
        # Transform'd group without crashing.
        pass

def Sub(self, run_time=0.5):
    everything = Group(*[m for m in self.mobjects if not type(m) == Mobject and not isinstance(m, Spotlight)])

    pfp = MathTex(r"y", font_size=160)
    pfp.set_color(RED) # FC6255
    
    handle = Text("@MathRendered", font_size=48)
    handle.set_color_by_gradient(BLUE, RED)

    additional = Text("FREE code in bio", font_size=24)
    additional.set_color_by_gradient(interpolate_color(BLUE, WHITE, 0.3), interpolate_color(PURPLE, WHITE, 0.5))
    additional.next_to(handle, DOWN, buff=0.2)

    self.ad = VGroup(pfp, handle, additional)
    self.ad.arrange(DOWN, buff=0.6)
    self.ad.move_to(ORIGIN)

    self.ad -= additional
    
    self.play(
        Transform(everything, self.ad, run_time=run_time),
        Write(additional, run_time=run_time/1.5),
    )



def _build_layout(layout_func=None):
    if layout_func is None:
        layout_func = globals()["build_layout"]
    layout = layout_func()

    if isinstance(layout, dict):
        cfg = layout.copy()
    else:
        items = list(layout)
        cfg = {"autographs": [], "labels": [], "others": []}

        for it in items:
            if isinstance(it, (Text, MathTex, Tex)) or getattr(it, "is_label", False):
                if getattr(it, "is_label", False):
                    cfg["labels"].append(it)
                else:
                    firstletter = it[0][0] if isinstance(it, (MathTex, Tex)) else it[0]
                    if firstletter == " ":
                        cfg["labels"].append(it)

            if isinstance(it, AutoGraph):
                cfg["autographs"].append(it)
            else:
                cfg["others"].append(it)

    cfg.setdefault("autographs", [])
    cfg.setdefault("labels", [])
    cfg.setdefault("others", [])

    return cfg

def video(self, build_layout, STEPS, x, y):
    cfg = _build_layout(build_layout)  # normalized layout dict

    to_add = []
    to_add.extend(cfg.get("autographs", []))
    to_add.extend(cfg.get("others", []))
    to_add.extend(cfg.get("labels", []))
    self.add(*to_add)

    for step in STEPS:
        anims = []
        if "sp" in step:
            expr = step["sp"]
        else:
            expr = None

        funcs = None
        if "function" in step:
            fobj = step["function"]
            if callable(fobj):
                funcs = [fobj]
            else:
                funcs = list(fobj)
        else:
            if expr is not None:
                if expr.has(y):
                    funcs = [sp.lambdify((x, y), expr)]
                else:
                    funcs = [sp.lambdify(x, expr)]

        if not "label" in step and expr is not None:
            if expr.has(y):
                step["label"] = sp.latex(expr) + " = 0"
            else:
                step["label"] = "y = " + sp.latex(expr)

        run_time = step.get("run_time", 0.3)
        step_color = step.get("color")

        # 1. Prepare Label Targets and temporarily apply them to ensure 
        # that 'others' (like boxes) can adapt to the new size.
        label_targets = {}
        for label in cfg.get("labels", []):
            if "label" in step:
                new_label = MathTex(step["label"], font_size=60).move_to(label)
            else:
                new_label = label.copy()
            
            if hasattr(label, 'ccolor') and label.ccolor and step_color:
                new_label.set_color(step_color)
            
            if hasattr(label, 'anchor'):
                new_label.move_to(label.anchor)
            
            label_targets[label] = new_label
            label.save_state()
            label.become(new_label)

        # 2. Prepare Other Targets (they will see the labels in their target states)
        for other in cfg.get("others", []):
            target_color = other.get_color()
            if hasattr(other, 'ccolor') and other.ccolor and step_color:
                target_color = step_color
            
            if hasattr(other, 'redeclare'):
                new_other = other.redeclare()
                if hasattr(other, 'ccolor') and other.ccolor and step_color:
                    new_other.set_color(target_color)
                anims.append(Transform(other, new_other, run_time=run_time))
            elif hasattr(other, 'ccolor') and other.ccolor and step_color:
                anims.append(FadeToColor(other, target_color, run_time=run_time))

        # 3. Restore labels and add their Transform animations
        for label, new_label in label_targets.items():
            label.restore()
            anims.append(Transform(label, new_label, run_time=run_time))

        # 4. Autograph animations
        autographs = cfg.get("autographs", [])
        colors = [BLUE, YELLOW, GREEN, RED, PURPLE, ORANGE]
        if funcs is not None and len(autographs) > 0:
            for i, ag in enumerate(autographs):
                func = funcs[i] if i < len(funcs) else funcs[-1]
                color = colors[i % len(colors)]
                if hasattr(ag, 'ccolor') and ag.ccolor and step_color:
                    color = step_color

                anims.append(ag.plot(func, run_time=run_time, color=color))

        self.play(*anims, run_time=run_time)
        wait_after = step.get("wait_after", 0.2)
        if wait_after > 0:
            self.wait(wait_after)

    # Clean up dummy plain Mobject instances left over by self.wait()
    self.remove(*[m for m in self.mobjects if type(m) is Mobject])

