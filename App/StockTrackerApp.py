from textual import on
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.containers import Horizontal, VerticalScroll, ScrollableContainer
from textual.widgets import Header, Footer, Button, Static, DataTable

ROWS = [
        ("Symbol", "Market Price", "Avg Price", "Total Shares", "Market Value", "Gain/Loss", "%Chg"),
        ("AAPL", 83.41, 82.10, 1000, 10000, -55.75, -5.5),
        ("TSLA", 83.41, 82.10, 1000, 10000, -55.75, -5.5),
        ("AMZN", 83.41, 82.10, 1000, 10000, -55.75, -5.5)
    ]

class LastUpdateInfo(Static):
    """Shows last update time of stock information"""
    def compose(self):
        ...

class StockWatch(Static):
    """Buttons for Stock Watchlist"""
    def compose(self):
        yield Button("AAPL", variant="success")
        yield Button("GOOGL", variant="error", classes="hidden")
        yield Button("AMAZN", variant="success")
        yield Button("TSLA", variant="error")

    @on(Button.Pressed)
    def a_method(self):
        self.app.exit()

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
        yield Header()
        yield Footer()
        yield DataTable()

        stockList = ['BUY', 'TSLA', 'AMZN']

        # for stock in stockList:
        #     stock_message = f"""{stock}\n89.75 <up>"""
        #     yield Button(stock_message, variant="primary")

        yield StockWatch()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*ROWS[0])
        table.add_rows(ROWS[1:])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # print("Button Pressed")
        self.exit(str(event.button))

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_quit_application(self) -> None: 
        """Quit application"""
        self.exit() 

if __name__ == "__main__":
    app = StockTrackerApp()
    app.run()
