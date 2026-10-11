
from .Stock import *


class Plotter:

    def __init__(self):
        implot.push_style_color(implot.Col.AxisBg, imgui.Vec4(0.1, 0.1, 0.1, 1.0))
        implot.push_style_color(implot.Col.AxisBgHovered, imgui.Vec4(0.15, 0.15, 0.15, 1.0))
        implot.push_style_color(implot.Col.AxisBgActive, imgui.Vec4(0.2, 0.2, 0.2, 1.0))
        implot.push_style_color(implot.Col.FrameBg, imgui.Vec4(0.1, 0.1, 0.1, 1.0))
        style = implot.get_style()
        style.plot_padding = imgui.Vec2(0, 0)
        style.plot_border_size = 1.0

        self.stock = None

        self.show_candles = True

        # Y-limits: updated using current X-range for use in next iteration
        self.y_min_next, self.y_max_next = 0, 1

        # Plot style specifications
        self.open_spec = implot.Spec()
        self.open_spec.line_weight = 2
        self.open_spec.line_color = imgui.Vec4(0.2, 0.4, 0.8, 1.0)
        self.high_spec = implot.Spec()
        self.high_spec.line_weight = 2
        self.high_spec.line_color = imgui.Vec4(0.1, 0.7, 0.3, 1.0)
        self.low_spec = implot.Spec()
        self.low_spec.line_weight = 2
        self.low_spec.line_color = imgui.Vec4(0.8, 0.2, 0.2, 1.0)
        self.close_spec = implot.Spec()
        self.close_spec.line_weight = 2
        self.close_spec.line_color = imgui.Vec4(0.9, 0.9, 0.9, 1.0)
        self.invisible_spec = implot.Spec()
        self.invisible_spec.marker_size = 0.0
        self.invisible_spec.flags = implot.ItemFlags.NoLegend

    def set_stock(self, stock: Stock):
        self.stock = stock

    def draw_candlesticks_drawlist(self, candle_width_px=8.0):
        draw_list = implot.get_plot_draw_list()
        plot_size = implot.get_plot_size()

        # topleft, bottomright
        plot_min = implot.get_plot_pos()
        plot_max = imgui.Vec2(plot_min.x + plot_size.x, plot_min.y + plot_size.y)

        draw_list.push_clip_rect(plot_min, plot_max, intersect_with_current=True)

        green_col = imgui.get_color_u32(imgui.Vec4(0.1, 0.8, 0.3, 1.0))
        red_col   = imgui.get_color_u32(imgui.Vec4(0.9, 0.2, 0.2, 1.0))
        half_width = candle_width_px * 0.5

        for i in range(len(self.stock.date_ist)):
            p_high = implot.plot_to_pixels(implot.Point(self.stock.date_ist[i], self.stock.high[i]))
            p_low  = implot.plot_to_pixels(implot.Point(self.stock.date_ist[i], self.stock.low[i]))
            p_open = implot.plot_to_pixels(implot.Point(self.stock.date_ist[i], self.stock.open[i]))
            p_close= implot.plot_to_pixels(implot.Point(self.stock.date_ist[i], self.stock.close[i]))

            # Draw high-low line
            color = green_col if self.stock.close[i] >= self.stock.open[i] else red_col
            draw_list.add_line(p_high, p_low, color, 1.5)

            # Draw candle bars
            top_y = min(p_open.y, p_close.y)
            bot_y = max(p_open.y, p_close.y)
            if bot_y - top_y < 1.0:
                bot_y = top_y + 1.0
            p_min = imgui.Vec2(p_open.x - half_width, top_y)
            p_max = imgui.Vec2(p_open.x + half_width, bot_y)
            draw_list.add_rect_filled(p_min, p_max, color)
        draw_list.pop_clip_rect()

    def plot(self):
        if not self.stock or not self.stock.date_ist:
            return
        
        implot.set_next_axis_limits(implot.Axis.Y1, self.y_min_next, self.y_max_next, imgui.Cond.Always)
        if implot.begin_plot(f"{self.stock.ticker} Price", size=imgui.Vec2(-1, -1)):
            implot.setup_axis_scale(implot.Axis.X1, implot.Scale.Time)
            implot.setup_axes(
                x_flags=implot.AxisFlags.NoLabel, 
                y_flags=implot.AxisFlags.RangeFit | implot.AxisFlags.AutoFit
            )
            # Invisible scatter plots required for proper range checking when others are hidden
            implot.plot_scatter_xy("CandleBounds", self.stock.date_ist, self.stock.low, self.invisible_spec)
            implot.plot_scatter_xy("CandleBounds", self.stock.date_ist, self.stock.high, self.invisible_spec)
            
            # Line plots
            implot.hide_next_item(True, implot.Cond.Once)
            implot.plot_line_xy("Open", self.stock.date_ist, self.stock.open, self.open_spec)
            implot.hide_next_item(True, implot.Cond.Once)
            implot.plot_line_xy("High", self.stock.date_ist, self.stock.high, self.high_spec)
            implot.hide_next_item(True, implot.Cond.Once)
            implot.plot_line_xy("Low", self.stock.date_ist, self.stock.low, self.low_spec)
            implot.hide_next_item(True, implot.Cond.Once)
            implot.plot_line_xy("Close", self.stock.date_ist, self.stock.close, self.close_spec)
            
            # Candlesticks
            if self.show_candles:
                self.draw_candlesticks_drawlist()
            
            # Calculate Y-limits automatically using visible datapoints
            x_range = implot.get_plot_limits().x
            visible_lows = [self.stock.low[i] for i in range(len(self.stock.date_ist)) if x_range.min <= self.stock.date_ist[i] <= x_range.max]
            visible_highs = [self.stock.high[i] for i in range(len(self.stock.date_ist)) if x_range.min <= self.stock.date_ist[i] <= x_range.max]
            if visible_lows and visible_highs:
                v_min = min(visible_lows)
                v_max = max(visible_highs)
                v_pad = (v_max - v_min) * 0.05 if v_max != v_min else 1.0
                self.y_min_next = v_min - v_pad
                self.y_max_next = v_max + v_pad

            implot.end_plot()