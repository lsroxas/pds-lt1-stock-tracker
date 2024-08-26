from __future__ import annotations

try: 
    import httpx
except ImportError: 
    raise ImportError("Please install httpx with 'pip install httpx' ")

try:
    import textual
except ImportError:
    raise ImportError("Please install textual with 'pip install textual' ")

try:
    import textual_pandas
except ImportError:
    raise ImportError("Please install textual with 'pip install textual_pandas' ")

try:
    import pandas
except ImportError:
    raise ImportError("Please install pandas with 'pip install pandas' ")

try:
    import numpy
except ImportError:
    raise ImportError("Please install numpy with 'pip install numpy' ")

from textual import on, work
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.containers import HorizontalScroll, VerticalScroll, ScrollableContainer
from textual.widgets import Header, Footer, Button, Static, DataTable, Label, Input, Markdown
from textual.screen import Screen
from textual_pandas.widgets import DataFrameTable
from datetime import time, datetime


import StockTracker as st

class LastUpdateInfo(Static):
    """Shows last update time of stock information"""
    last_update_time = reactive(0)
    def watch_last_update_time(self):
        # time = self.last_update_time 
        self.update(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %z')}")

class PositionActions(Static):
    """Buttons for Stock Watchlist"""
    def compose(self):
        yield Button("Buy", variant="success", id="button_Buy")
        yield Button("Sell", variant="error", id="button_Sell")
        yield Button("Refresh", variant="default", id="button_Refresh")
        yield Button("Quit", variant="default", id="button_Quit")

    @on(Button.Pressed, "#button_Refresh")
    def update_refresh_time(self):
        time_display = self.app.query_one("#display_UpdateTime")
        time_display.last_update_time = datetime.now()
    
    @on(Button.Pressed, "#button_Quit")
    def quit_application(self):
        app.exit()



class PortfolioTable(DataFrameTable):
    """Container for Actual Stock Portfolio"""

    def compose(self):
        yield DataFrameTable()

    def on_mount(self) -> None:
        table = self.query_one(DataFrameTable)
        portfolio_df =portfolio.get_portfolio()
        portfolio_df.columns = ['Ticker', 'Current Price', 'Average Price', '# of Shares', 'Market Value', 'Gain/Loss', '% Change', '% of Portfolio']
        table.add_df(portfolio_df)

        self.format_results()
    
    def format_results(self) -> None: 
        table = self.query_one(DataFrameTable)
        table.header_height = 1


class PotfolioSummary(Static):
    """Widget to display Portfolio Summary."""
    
    def compose(self):
        # yield Markdown(self.PORTFOLIO_VALUE_MESSAGE + "\\n" + self.PORTFOLIO_DAY_CHANGE_MESSAGE + "\n" + self.PORTFOLIO_GAINLOSS_MESSAGE, classes="Summary")
        value_message = f"""
        Cash Available: ${portfolio.balance}\n
        Total Portoflio Trade Value: {portfolio.portfolio_market_value:.2f}\n
        Day Change: {portfolio.portfolio_gainloss:.2f}\n
        Gain/Loss : {portfolio.portfolio_pct_change*100:.2f}%"""
        yield Label(value_message, classes="summary")

class Column_Wide(VerticalScroll):
    DEFAULT_CSS = """
    Column_Wide {
        height: 1fr;
        width: 3fr;
        margin: 0 2;
    }
    """
    def compose(self) -> ComposeResult:
        yield PortfolioTable()
        yield LastUpdateInfo(id="display_UpdateTime")
        yield PotfolioSummary()
        


class Column_Narrow(VerticalScroll):
    DEFAULT_CSS = """
    Column_Narrow {
        height: 1fr;
        width: 1fr;
        margin: 0 2;
    }
    """
    def compose(self) -> ComposeResult:
        yield PositionActions()

class StockTrackerApp(Screen):
    # CSS_PATH = "style.tcss"
    OWNER = "LT1"

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"), ("q", "quit_application", "Quit")]
    
    def compose(self) -> ComposeResult:
        """Widgets for the app"""
        yield Header()
        yield Footer()
        with HorizontalScroll():
            yield Column_Wide()
            yield Column_Narrow()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        app.dark = not app.dark

    def action_quit_application(self) -> None: 
        """Quit application"""
        app.exit()

    def on_mount(self):
        self.title = "Stock Tracker"
        self.sub_title = f"{self.OWNER}'s Portfolio"



class StockTrackerLayoutApp(App):
    def on_ready(self) -> None:
        self.push_screen(StockTrackerApp())

if __name__ == "__main__":
    portfolio = st.Portfolio()
    app = StockTrackerLayoutApp()
    app.run()
