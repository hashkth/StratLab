
from entities import *
import yfinance as yf
import threading

class Backtester(State):

    # Backtester

    def __init__(self):
        super().__init__("Backtester")

    def enter(self):
        Core.imgui_io.font_global_scale = 2
        Camera.set_perspective("2d")

        # YFinance Warmup
        yf.Ticker("AAPL").history(period="1d", interval="1d")

        self.ticker = "AAPL"
        self.stock_data = None
        self.stocks = {}
        self.is_searching = False

        self.time_periods = ["1d", "1wk", "1mo", "6mo", "1y", "3y", "5y"]
        self.time_period = 0
        self.intervals = [
            ["1m", "5m", "30m", "1h", "1d"],
            ["1m", "5m", "30m", "1h", "1d", "1wk"],
            ["5m", "30m", "1h", "1d", "1wk", "1mo"],
            ["1d", "1wk", "1mo"],
            ["1d", "1wk", "1mo"],
            ["1d", "1wk", "1mo"],
            ["1d", "1wk", "1mo"]
        ]
        self.interval = 0

        self.plotter = Plotter()

        self.simulating = False
        self.auto_tick = False
        self.auto_tick_rate = 10

        self.search_query = ""
        self.search_results = []
        self.selected_search_index = 0

        self.logs = []

    def exit(self):
        pass

    def events(self):
        pass

    def process(self):
        pass
    
    def render(self):
        pass

    def log(self, message: str):
        self.logs.insert(0, str(message))
        if len(self.logs) > 100: self.logs.pop()

    def render_ui(self):
        imgui.set_next_window_pos(imgui.Vec2(0, 0))
        imgui.set_next_window_size(imgui.Vec2(Core.qw, Core.h))
        imgui.begin("Settings", flags=imgui.WindowFlags.NoCollapse | imgui.WindowFlags.NoResize)
        w, h = imgui.get_available_region()
        imgui.begin_group()
        imgui.text("Data")
        imgui.separator()
        
        if imgui.tree_node("Online"):
            imgui.text("Search  ")
            imgui.same_line()
            imgui.set_next_item_width(w / 3)
            changed, self.search_query = imgui.input_text("##SearchQuery", self.search_query)
            
            def fetch_search_results(query):
                try:
                    search_obj = yf.Search(query, max_results=5)
                    self.search_results = search_obj.quotes
                except Exception:
                    self.search_results = []
                finally:
                    self.is_searching = False

            if (changed and len(self.search_query) > 2):
                if not self.is_searching:
                    self.is_searching = True
                    threading.Thread(target=fetch_search_results, args=(self.search_query,), daemon=True).start()

            if self.is_searching:
                imgui.text("Searching")
            elif self.search_results:
                result_labels = [
                    f"{item.get('symbol', '')} - {item.get('shortname', item.get('longname', 'Unknown'))}" 
                    for item in self.search_results
                ]
                
                imgui.text("Results ")
                imgui.same_line()
                imgui.set_next_item_width(w / 2)
                
                if self.selected_search_index >= len(result_labels):
                    self.selected_search_index = 0
                    
                _, self.selected_search_index = imgui.combo(
                    "##SearchResults", self.selected_search_index, result_labels
                )
                
                if imgui.button("Select"):
                    selected_item = self.search_results[self.selected_search_index]
                    self.ticker = selected_item.get('symbol', self.ticker)

            imgui.separator()
            imgui.text("Ticker:      " + self.ticker);            
            imgui.text("Time Period "); imgui.same_line()
            imgui.set_next_item_width(w / 3)
            _, self.time_period = imgui.combo("##TP", self.time_period, self.time_periods)
            
            imgui.text("Interval    "); imgui.same_line()
            imgui.set_next_item_width(w / 3)
            if self.interval > len(self.intervals[self.time_period]):
                self.interval = 0
            _, self.interval = imgui.combo("##INT", self.interval, self.intervals[self.time_period])
            
            if imgui.button("Download"):
                if self.ticker in self.stocks:
                    del self.stocks[self.ticker]
                self.stocks[self.ticker] = Stock(self.ticker)
                self.stocks[self.ticker].set_history(self.time_periods[self.time_period], self.intervals[self.time_period][self.interval])
                self.stocks[self.ticker].fetch_data()
                self.plotter.set_stock(self.stocks[self.ticker])
                self.log(f"Downloading... {self.ticker}")
            imgui.tree_pop()

        if imgui.tree_node("Offline"):
            imgui.text_colored(imgui.Vec4(0.0, 1.0, 0.0, 1.0), "In-Development")
            imgui.tree_pop()
        imgui.end_group()

        imgui.text("")

        imgui.begin_group()
        imgui.text("Indicators")
        imgui.separator()
        _, self.plotter.show_candles = imgui.checkbox("Candles", self.plotter.show_candles)
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
        imgui.set_next_window_size(imgui.Vec2(Core.qw * 2, Core.qh))
        imgui.begin("Information", flags=imgui.WindowFlags.NoCollapse | imgui.WindowFlags.NoResize)
        imgui.end()

        imgui.set_next_window_pos(imgui.Vec2(Core.qw * 3, Core.qh * 3))
        imgui.set_next_window_size(imgui.Vec2(Core.qw, Core.qh))
        imgui.begin("Log", flags=imgui.WindowFlags.NoCollapse | imgui.WindowFlags.NoResize)
        for l in self.logs:
            imgui.text(l)
        imgui.end()

        imgui.set_next_window_pos(imgui.Vec2(Core.qw, 0))
        imgui.set_next_window_size(imgui.Vec2(Core.qw * 3, Core.qh * 3))
        imgui.begin("Chart", flags=imgui.WindowFlags.NoCollapse | imgui.WindowFlags.NoResize)
        if self.stocks and self.stocks[self.ticker].has_data:
            self.plotter.plot()
        imgui.end()

Core.add_state(Backtester)