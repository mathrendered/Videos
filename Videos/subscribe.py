from manim import *

def Sub(self, run_time=0.5):
    everything = Group(*self.mobjects)

    pfp = MathTex(r"y", font_size=160)
    pfp.set_color(RED) # FC6255
    
    handle = Text("@MathRendered", font_size=48)
    handle.set_color_by_gradient(BLUE, RED)
    
    self.ad = VGroup(pfp, handle)
    self.ad.arrange(DOWN, buff=0.6)
    self.ad.move_to(ORIGIN)
    
    self.play(
        Transform(everything, self.ad),
        run_time=run_time
    )




