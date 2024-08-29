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
from textual.containers import Container, HorizontalScroll, VerticalScroll, ScrollableContainer, Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Static, DataTable, Label, Input, Markdown
from textual.screen import Screen, ModalScreen
from textual_pandas.widgets import DataFrameTable

from datetime import time, datetime

import StockTracker as st



class MessageBox(ModalScreen):
    """Generic Message Box"""
    CSS_PATH = "modalscreen.tcss"

    def __init__(self, message):
        super().__init__()
        self.message = message

    def compose(self):
        with Container():
            yield Label(self.message)
            with Horizontal():
                yield Button.success("Ok", id="yes")

    @on(Button.Pressed)
    def exit_screen(self, event):
        button_id = event.button.id
        self.dismiss(button_id == "yes")


class LastUpdateInfo(Static):
    """Shows last update time of stock information"""
    last_update_time = reactive(0)
    def watch_last_update_time(self):
        # time = self.last_update_time 
        self.update(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %z')}")

class ResultsInfo(Static):
    """Shows last update time of stock information"""
    message = reactive("")
    def watch_message(self):
        # time = self.last_update_time 
        self.update(f"{self.message}")


class PositionActions(Static):
    """Buttons for Stock Watchlist"""
    def compose(self):
        yield Button("Buy", variant="success", id="button_Buy")
        yield Button("Sell", variant="error", id="button_Sell")
        yield Button("Refresh", variant="default", id="button_Refresh")
        yield Button("Deposit", id="button_Deposit")
        yield Button("Withraw", id="button_Withdraw")
        yield Button("Quit", variant="default", id="button_Quit")

    @on(Button.Pressed, "#button_Refresh")
    def update_refresh_time(self):
        portfolio.refresh_data()
        tables = app.query(PortfolioTable)
        for i in tables:
            i.update_table()
        time_display = self.app.query_one("#display_UpdateTime")
        time_display.last_update_time = datetime.now()
    
    @on(Button.Pressed, "#button_Quit")
    def quit_application(self):
        app.exit()

    @on(Button.Pressed, "#button_Buy")
    def action_buy_stock(self) -> None:
        app.switch_mode("buystock")

    @on(Button.Pressed, "#button_Sell")
    def action_sell_stock(self) -> None: 
        app.switch_mode("sellstock")

    @on(Button.Pressed, "#button_Deposit")
    def action_deposit(self) -> None: 
        app.switch_mode("deposit")
    
    @on(Button.Pressed, "#button_Withdraw")
    def action_withdraw(self) -> None: 
        app.switch_mode("withdraw")

class PortfolioTable(DataFrameTable):
    """Container for Actual Stock Portfolio""" 

    def compose(self):
        yield DataFrameTable(id="df_portfolio")

    def on_mount(self) -> None:
        table = self.query_one(DataFrameTable)
        portfolio_df = portfolio.get_portfolio()
        # portfolio_df.columns = ['Ticker', 'Current Price', 'Average Price', '# of Shares', 'Market Value', 'Gain/Loss', '% Change', '% of Portfolio']
        table.add_df(portfolio_df)
        self.format_results()
    
    def format_results(self) -> None: 
        table = self.query_one(DataFrameTable)
        table.header_height = 1

    def update_table(self):
        df_portfolio = portfolio.get_portfolio()
        self.update_df(df_portfolio)

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
        margin: 1 1;
    }
    """
    def compose(self) -> ComposeResult:
        yield PortfolioTable()
        yield LastUpdateInfo(id="display_UpdateTime")
        yield PotfolioSummary(id="display_Summary")
        
class Column_Narrow(VerticalScroll):
    DEFAULT_CSS = """
    Column_Narrow {
        height: 1fr;
        width: 20;
        margin: 0 0;
    }
    """
    def compose(self) -> ComposeResult:
        yield PositionActions()

class StockTrackerApp(Screen):
    """Screen for the actual stock tracker"""
    def compose(self) -> ComposeResult:
        """Widgets for the app"""
        yield Header()
        yield Footer()
        with HorizontalScroll():
            yield Column_Wide()
            yield Column_Narrow()

    def on_mount(self):

        self.title = "Stock Tracker"
        self.sub_title = f"{app.OWNER}'s Portfolio"

####################################################################################################################################

class BuyStockApp(Screen):
    """Screen for the buy stock action"""
    CSS_PATH = "dictionary.tcss"

    def compose(self) -> ComposeResult:
        """Creatte screen for buying stocks"""
        yield Header()
        yield Footer()
        yield Input(placeholder="Search for a stock", id="input_Ticker")
        with VerticalScroll(id="results-container"):
            with HorizontalScroll():
                ### TODO: Add logic to update result based on search
                yield Markdown(id="results")
            with VerticalScroll():
                yield Input(placeholder="Sale Price", id="input_salePrice", type="number")
                yield Input(placeholder="# Shares", id="input_NoOfShares", type="integer")
                yield Input(placeholder="Transaction Fee (defaults to 0)", id="input_TransactionFee", type="number")
                with Horizontal():
                    yield Button("Execute", variant="success", id="buttton_Execute_Sale")
                    yield Button("Back to Portfolio", variant="error", id="button_Cancel")
                    # yield ResultsInfo("_", id="buy_results")

    @on(Button.Pressed, "#buttton_Execute_Sale")
    def execute_sale(self):
        ticker = self.query_one("#input_Ticker").value
        sale_price = float(self.query_one("#input_salePrice").value)
        no_of_shares = int(self.query_one("#input_NoOfShares").value)
        transaction_fee = self.query_one("#input_TransactionFee").value
        if transaction_fee == "":
            transaction_fee = portfolio.transaction_fee
        else:
            transaction_fee = float(transaction_fee)
        sale_result = portfolio.buy_stock(ticker, no_of_shares, sale_price, transaction_fee)
        # results = self.query_one("#buy_results")
        # results.message = sale_result[1]
        app.push_screen(MessageBox(sale_result[1]))


    @on(Button.Pressed, "#button_Cancel")
    def cancel_screen(self):
        app.switch_mode("portfolio")


####################################################################################################################################

class SellStockApp(Screen):
    """Screen for the sell stock action"""
    CSS_PATH = "dictionary.tcss"

    current_ticker = reactive("")

    def watch_current_ticker(self):
        # time = self.last_update_time 
        # self.update(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %z')}")
        ...

    def compose(self) -> ComposeResult:
        """Create screen for buying stocks"""
        yield Header()
        yield Footer()
        with VerticalScroll(id="results-container"):
            ### TODO: Add logic to update based on currently selected cell in sell 
            yield PortfolioTable()
            yield Input(placeholder="Stock to Sell", id="input_Ticker", type="text")
            yield Input(placeholder="Selling Price", id="input_salePrice", type="number")
            yield Input(placeholder="# Shares to Sell", id="input_NoOfShares", type="integer")
            yield Input(placeholder="Transaction Fee (defaults to 0)", id="input_TransactionFee", type="number")
            with Horizontal():
                yield Button("Execute", variant="success", id="buttton_Execute_Sale")
                yield Button("Back to Portfolio", variant="error", id="button_Cancel")
                # yield ResultsInfo("_", id="sell_results")

    @on(Button.Pressed, "#button_Cancel")
    def cancel_screen(self):
        app.switch_mode("portfolio")

    @on(Button.Pressed, "#buttton_Execute_Sale")
    def execute_sale(self):
        ticker = self.query_one("#input_Ticker").value
        sale_price = float(self.query_one("#input_salePrice").value)
        no_of_shares = int(self.query_one("#input_NoOfShares").value)
        transaction_fee = self.query_one("#input_TransactionFee").value
        if transaction_fee == "":
            transaction_fee = portfolio.transaction_fee
        else:
            transaction_fee = float(transaction_fee)
        sale_price += transaction_fee
        sale_result = portfolio.sell_stock(ticker, no_of_shares, sale_price)
        # results = self.query_one("#sell_results")
        # results.message = sale_result[1]
        app.push_screen(MessageBox(sale_result[1]))


####################################################################################################################################

class DepositApp(Screen):
    """Screen for the sell stock action"""
    CSS_PATH = "dictionary.tcss"

    def compose(self) -> ComposeResult:
        """Create screen for depositing money"""
        yield Header()
        yield Footer()
        with VerticalScroll(id="results-container"):
            yield Input(placeholder="Amount to Deposit", id="input_DepositAmount", type="number")
            with Horizontal():
                yield Button("Execute", variant="success", id="buttton_Execute")
                yield Button("Back to Portfolio", variant="error", id="button_Cancel")

    @on(Button.Pressed, "#button_Cancel")
    def cancel_screen(self):
        app.switch_mode("portfolio")

    @on(Button.Pressed, "#buttton_Execute")
    def execute_Deposit(self):
        amount = float(self.query_one("#input_DepositAmount").value)
        deposit_result = portfolio.deposit(amount)
        if deposit_result[0]:
            message = f"Deposit Completed. New balance: $ {deposit_result[1]:.2f}"
        else:
            message = f"Deposit Failed. Balance: $ {deposit_result[1]:.2f}"
        app.push_screen(MessageBox(message))

####################################################################################################################################

class WithdrawApp(Screen):
    """Screen for the withdraw money action"""
    CSS_PATH = "dictionary.tcss"

    def compose(self) -> ComposeResult:
        """Creatte screen for withdrawing money"""
        yield Header()
        yield Footer()
        with VerticalScroll(id="results-container"):
            yield Input(placeholder="Amount to Withdraw", id="input_WithdrawalAmount", type="number")
            with Horizontal():
                yield Button("Execute", variant="success", id="buttton_Execute")
                yield Button("Back to Portfolio", variant="error", id="button_Cancel")
                # yield ResultsInfo("_", id="withdraw_results")

    @on(Button.Pressed, "#button_Cancel")
    def cancel_screen(self):
        # self.dismiss()
        app.switch_mode("portfolio")
    
    @on(Button.Pressed, "#buttton_Execute")
    def execute_Withdrawal(self):
        amount = float(self.query_one("#input_WithdrawalAmount").value)
        withdrawal_result = portfolio.withdraw(amount)
        if withdrawal_result[0]:
            message = f"Withdrawal Completed. New balance: $ {withdrawal_result[1]:.2f}"
        else:
            message = f"Withdrawal Failed. Balance: $ {withdrawal_result[1]:.2f}"
        app.push_screen(MessageBox(message))

class StockTrackerLayoutApp(App):
    # CSS_PATH = "style.tcss"
    OWNER = "LT1"
    BINDINGS = [
        ("p", "switch_mode('portfolio')", "Show Portfolio"),
        ("b", "switch_mode('buystock')", "Buy Stock"), 
        ("s", "switch_mode('sellstock')", "Sell Stock"), 
        ("d", "switch_mode('deposit')", "Deposit"),
        ("w", "switch_mode('withdraw')", "Withdraw"),
        ("r", "refresh_data"), 
        ("l", "toggle_dark", "Toggle Dark Mode"), 
        ("q", "quit_application", "Quit")
    ]
    MODES = {
        "portfolio" : StockTrackerApp, 
        "buystock" : BuyStockApp, 
        "sellstock" : SellStockApp,
        "deposit" : DepositApp, 
        "withdraw": WithdrawApp
    }

    active_ticker = "AAPL"

    def on_ready(self) -> None:
        # self.push_screen(StockTrackerApp())
        self.switch_mode("portfolio")

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        app.dark = not app.dark

    def action_quit_application(self) -> None: 
        """Quit application"""
        app.exit()

    def action_refresh_data(self) -> None: 
        """refresh data"""
        portfolio.refresh_data()
        tables = app.query(PortfolioTable)
        for i in tables:
            i.update_table()
        time_display = self.app.query_one("#display_UpdateTime")
        time_display.last_update_time = datetime.now()
        # app.exit()

if __name__ == "__main__":
    ### TODO: 
    ### 1. Refresh Dataframe after buy and sell 
    ### 2. Load general configs via config file:
    ###     User Name
    ###     Default Transaction Fee
    ### 
    portfolio = st.Portfolio()
    app = StockTrackerLayoutApp()
    app.run()