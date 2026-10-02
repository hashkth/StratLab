
from entities import *

class StartMenu(State):

    # StartMenu

    def __init__(self):
        super().__init__("StartMenu")

    def enter(self):
        Core.imgui_io.font_global_scale = 2
        Camera.set_perspective("2d")

    def exit(self):
        pass

    def events(self):
        pass

    def process(self):
        pass
    
    def render(self):
        pass

    def render_ui(self):
        imgui.set_next_window_pos(imgui.Vec2(Core.qw, Core.qh))
        imgui.set_next_window_size(imgui.Vec2(Core.hw, Core.hh))
        imgui.begin("StartMenu", flags=imgui.WindowFlags.NoDecoration)
        w, h = imgui.get_available_region()
        fsize = imgui.get_font_size()
        imgui.set_cursor_pos(imgui.Vec2(w/4, h/2 - fsize/2))
        imgui.set_cursor_pos(imgui.Vec2(w/4, h/2 - fsize/2))
        if imgui.button("Enter", imgui.Vec2(w/2)):
            Core.activate_state("Backtester")
        imgui.end()

Core.add_state(StartMenu)