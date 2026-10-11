
from engine import *
import yfinance as yf
import threading

class Stock:

    def __init__(self, ticker: str):
        self.ticker = ticker
        self.data = None
        self.period = ""
        self.interval = ""
        self.date = None
        self.date_ist = None
        self.open = None
        self.high = None
        self.low = None
        self.close = None
        self.fetching = False
        self.has_data = False

    def set_history(self, period: str, interval: str):
        self.period = period
        self.interval = interval

    def fetch_data(self):
        def worker():
            try:
                self.data = yf.Ticker(self.ticker).history(period=self.period, interval=self.interval)
                self.date = [timestamp.timestamp() for timestamp in self.data.index]
                self.open = self.data["Open"].astype(float).tolist()    
                self.high = self.data["High"].astype(float).tolist()
                self.low = self.data["Low"].astype(float).tolist()    
                self.close = self.data["Close"].astype(float).tolist()
                IST_OFFSET = 5 * 3600 + 30 * 60
                self.date_ist = [t + IST_OFFSET for t in self.date]
                self.has_data = True
            finally:
                self.fetching = False

        if not self.fetching:
            self.fetching = True
            threading.Thread(target=worker, args=(), daemon=True).start()
            