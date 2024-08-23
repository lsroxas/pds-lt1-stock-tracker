from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np

class Stock:

    def __init__(self, code: str):
        self.symbol = code
        self.stock = yf.Ticker(code)

    def get_current_price(self):
        self.last_update = datetime.now()
        return self.stock.info.get('currentPrice')



# class StockTracker:

# class Portfolio:
#     def __init__():


if __name__ == "__main__": 
    # app = StockTrackerApp()
    # app.mainloop()
    new_stock = Stock(code='AAPL')
    print(new_stock.get_current_price())
