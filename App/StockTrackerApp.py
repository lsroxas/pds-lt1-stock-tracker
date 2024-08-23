from textual import on
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.containers import Horizontal, VerticalScroll, ScrollableContainer
from textual.widgets import Header, Footer, Button, Static, DataTable, Label
from datetime import time, datetime

ROWS = [
        ("Symbol", "Market Price", "Avg Price", "Total Shares", "Market Value", "Gain/Loss", "%Chg"),
        ("AAPL", 83.41, 82.10, 1000, 10000, -55.75, -5.5),
        ("TSLA", 83.41, 82.10, 1000, 10000, -55.75, -5.5),
        ("AMZN", 83.41, 82.10, 1000, 10000, -55.75, -5.5)
    ]

class LastUpdateInfo(Static):
    """Shows last update time of stock information"""
    last_update_time = reactive(0)
    def watch_last_update_time(self):
        # time = self.last_update_time 
        self.update(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %z')}")

    @on(Button.Pressed)
    def a_method(self):
        # self.app.exit()
        time_display = app.query_one(LastUpdateInfo)
        time_display.last_update_time = datetime.now()

class PositionActions(Static):
    """Buttons for Stock Watchlist"""
    def compose(self):
        yield Button("Buy", variant="success")
        yield Button("Sell", variant="error")
        yield Button("Refresh", variant="default")

    @on(Button.Pressed)
    def update_refresh_time(self):
        # self.app.exit()
        time_display = app.query_one(LastUpdateInfo)
        time_display.last_update_time = datetime.now()


class PortfolioTable(Static):
    """Container for Actual Stock Portfolio"""

    def compose(self):
        yield DataTable(id="Portfolio")
    
    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*ROWS[0])
        table.add_rows(ROWS[1:])


class PotfolioSummary(Static):
    """Widget to display Portfolio Summary."""
    VALUE = 1000
    DAYCHANGE = 50
    GAINLOSS = 5
    PORTFOLIO_VALUE_MESSAGE = f"""
    Total Portoflio Trade Value: {VALUE}\n
    Day Change: {DAYCHANGE}\n
    Gain/Loss : {GAINLOSS}"""
    
    def compose(self):
        # yield Markdown(self.PORTFOLIO_VALUE_MESSAGE + "\\n" + self.PORTFOLIO_DAY_CHANGE_MESSAGE + "\n" + self.PORTFOLIO_GAINLOSS_MESSAGE, classes="Summary")
        yield Label(self.PORTFOLIO_VALUE_MESSAGE, classes="Summary")

class StockTrackerApp(App):

    CSS_PATH = "style.tcss"

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"), ("q", "quit_application", "Quit")]
    
    # ROWS = [
    #     ("Symbol", "Market Price", "Avg Price", "Total Shares", "Market Value", "Gain/Loss", "%Chg"),
    #     ("AAPL", 83.41, 82.10, 1000, 10000, -55.75, -5.5),
    #     ("TSLA", 83.41, 82.10, 1000, 10000, -55.75, -5.5),
    #     ("AMZN", 83.41, 82.10, 1000, 10000, -55.75, -5.5)
    # ]
    
    def compose(self) -> ComposeResult:
        """Widgets for the app"""
        yield Header("Stock Portfolio Tracker")
        yield Footer()
        yield PortfolioTable()
        yield PotfolioSummary()

        yield PositionActions()
        yield LastUpdateInfo(f"Last Updated {datetime.now().strftime('%Y-%m-%d %H:%M:%S %z')}")

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_quit_application(self) -> None: 
        """Quit application"""
        self.exit()

if __name__ == "__main__":
    app = StockTrackerApp()
    app.run()
