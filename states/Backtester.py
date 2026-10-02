
from entities import *
import yfinance as yf


class Backtester(State):

    # Backtester

    def __init__(self):
        super().__init__("Backtester")

    def enter(self):
        Core.imgui_io.font_global_scale = 2
        Camera.set_perspective("2d")
        implot.push_style_color(implot.Col.AxisBg, imgui.Vec4(0.1, 0.1, 0.1, 1.0))
        implot.push_style_color(implot.Col.AxisBgHovered, imgui.Vec4(0.15, 0.15, 0.15, 1.0))
        implot.push_style_color(implot.Col.AxisBgActive, imgui.Vec4(0.2, 0.2, 0.2, 1.0))
        implot.push_style_color(implot.Col.FrameBg, imgui.Vec4(0.1, 0.1, 0.1, 1.0))
        
        self.ticker = "AAPL"

        self.time_periods = ["1d", "5d", "1mo", "6mo", "1y", "5y", "max"]
        self.time_period = 0
        self.intervals = ["1m", "2m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"]
        self.interval = 5

        self.stock_data = None
        self.xs = None
        self.close_ys, self.open_ys, self.low_ys, self.high_ys = None, None, None, None

        self.close_spec = implot.Spec()
        self.close_spec.line_weight = 2.5
        self.close_spec.line_color = imgui.Vec4(1.0, 0.0, 0.0, 1.0)
        self.open_spec = implot.Spec()
        self.open_spec.line_weight = 2.5
        self.open_spec.line_color = imgui.Vec4(0.0, 1.0, 0.0, 1.0)

        self.y_min_next, self.y_max_next = 0, 1
        
        self.show_candles = True
        self.simulating = False
        self.auto_tick = False
        self.auto_tick_rate = 10

    def exit(self):
        pass

    def events(self):
        pass

    def process(self):
        pass
    
    def render(self):
        pass

    @staticmethod
    def draw_candlesticks_drawlist(xs, opens, closes, lows, highs, candle_width_px=8.0):
        draw_list = implot.get_plot_draw_list()
        
        plot_min = implot.get_plot_pos() # topleft
        plot_size = implot.get_plot_size()
        plot_max = imgui.Vec2(plot_min.x + plot_size.x, plot_min.y + plot_size.y) # bottomright

        draw_list.push_clip_rect(plot_min, plot_max, intersect_with_current=True)

        green_col = imgui.get_color_u32(imgui.Vec4(0.1, 0.8, 0.3, 1.0))
        red_col   = imgui.get_color_u32(imgui.Vec4(0.9, 0.2, 0.2, 1.0))
        half_width = candle_width_px * 0.5

        for i in range(len(xs)):
            p_high = implot.plot_to_pixels(implot.Point(xs[i], highs[i]))
            p_low  = implot.plot_to_pixels(implot.Point(xs[i], lows[i]))
            p_open = implot.plot_to_pixels(implot.Point(xs[i], opens[i]))
            p_close= implot.plot_to_pixels(implot.Point(xs[i], closes[i]))

            color = green_col if closes[i] >= opens[i] else red_col
            draw_list.add_line(p_high, p_low, color, 1.5)

            top_y = min(p_open.y, p_close.y)
            bot_y = max(p_open.y, p_close.y)
            if bot_y - top_y < 1.0:
                bot_y = top_y + 1.0
            p_min = imgui.Vec2(p_open.x - half_width, top_y)
            p_max = imgui.Vec2(p_open.x + half_width, bot_y)
            draw_list.add_rect_filled(p_min, p_max, color)
        draw_list.pop_clip_rect()

    def render_ui(self):
        imgui.set_next_window_pos(imgui.Vec2(0, 0))
        imgui.set_next_window_size(imgui.Vec2(Core.qw, Core.h))
        imgui.begin("Settings", flags=imgui.WindowFlags.NoCollapse | imgui.WindowFlags.NoResize)
        w, h = imgui.get_available_region()
        imgui.begin_group()
        imgui.text("Data")
        imgui.separator()
        
        if imgui.tree_node("Online"):
            imgui.text("Ticker      "); imgui.same_line()
            imgui.set_next_item_width(w / 3)
            _, self.ticker = imgui.input_text("##Ticker", self.ticker)
            
            imgui.text("Time Period "); imgui.same_line()
            imgui.set_next_item_width(w / 3)
            _, self.time_period = imgui.combo("##TP", self.time_period, self.time_periods)
            
            imgui.text("Interval    "); imgui.same_line()
            imgui.set_next_item_width(w / 3)
            _, self.interval = imgui.combo("##INT", self.interval, self.intervals)
            
            if imgui.button("Download"):
                ticker = yf.Ticker(self.ticker)
                self.stock_data = ticker.history(period=self.time_periods[self.time_period], interval=self.intervals[self.interval])
                self.xs = [timestamp.timestamp() for timestamp in self.stock_data.index]
                self.close_ys = self.stock_data["Close"].astype(float).tolist()    
                self.open_ys = self.stock_data["Open"].astype(float).tolist()    
                self.low_ys = self.stock_data["Low"].astype(float).tolist()    
                self.high_ys = self.stock_data["High"].astype(float).tolist()    
            imgui.tree_pop()

        if imgui.tree_node("Offline"):
            imgui.text_colored(imgui.Vec4(0.0, 1.0, 0.0, 1.0), "In-Development")
            imgui.tree_pop()    
        imgui.end_group()

        imgui.text("")

        imgui.begin_group()
        imgui.text("Indicators")
        imgui.separator()
        _, self.show_candles = imgui.checkbox("Candles", self.show_candles)
        imgui.end_group()

        imgui.text("")

        imgui.begin_group()
        imgui.text("Simulation")
        imgui.separator()
        
        _, self.simulating = imgui.checkbox("Simulate", self.simulating)
        _, self.auto_tick = imgui.checkbox("Auto-Tick", self.auto_tick)
        _, self.auto_tick_rate = imgui.slider_int("##AutoTick", self.auto_tick_rate, 1, 60)
        
        if imgui.button("Step Down"):
            pass
        imgui.same_line()
        if imgui.button("Step Up"):
            pass
        if imgui.button("Reset"):
            pass

        imgui.end_group()
        imgui.end()

        imgui.set_next_window_pos(imgui.Vec2(Core.qw, Core.qh * 3))
        imgui.set_next_window_size(imgui.Vec2(Core.qw * 3, Core.qh))
        imgui.begin("Information", flags=imgui.WindowFlags.NoCollapse | imgui.WindowFlags.NoResize)
        imgui.end()

        imgui.set_next_window_pos(imgui.Vec2(Core.qw, 0))
        imgui.set_next_window_size(imgui.Vec2(Core.qw * 3, Core.qh * 3))
        imgui.begin("Chart", flags=imgui.WindowFlags.NoCollapse | imgui.WindowFlags.NoResize)
        style = implot.get_style()
        style.plot_padding = imgui.Vec2(0, 0)
        style.plot_border_size = 1.0
        if self.xs:
            implot.set_next_axis_limits(implot.Axis.Y1, self.y_min_next, self.y_max_next, imgui.Cond.Always)
            if implot.begin_plot(f"{self.ticker} Price", size=imgui.Vec2(-1, -1)):
                implot.setup_axis_scale(implot.Axis.X1, implot.Scale.Time)
                implot.setup_axes(x_flags=implot.AxisFlags.NoLabel, 
                                  y_flags=implot.AxisFlags.RangeFit | implot.AxisFlags.AutoFit)

                implot.plot_line_xy("Open", self.xs, self.open_ys, self.open_spec)
                implot.plot_line_xy("Close", self.xs, self.close_ys, self.close_spec)
                
                if self.show_candles:
                    self.draw_candlesticks_drawlist(self.xs, self.open_ys, self.close_ys, self.low_ys, self.high_ys)
                
                x_range = implot.get_plot_limits().x

                visible_lows = [self.low_ys[i] for i in range(len(self.xs)) if x_range.min <= self.xs[i] <= x_range.max]
                visible_highs = [self.high_ys[i] for i in range(len(self.xs)) if x_range.min <= self.xs[i] <= x_range.max]
                if visible_lows and visible_highs:
                    v_min = min(visible_lows)
                    v_max = max(visible_highs)
                    v_pad = (v_max - v_min) * 0.05 if v_max != v_min else 1.0
                    self.y_min_next = v_min - v_pad
                    self.y_max_next = v_max + v_pad
                implot.end_plot()
        imgui.end()


Core.add_state(Backtester)