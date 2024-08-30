from __future__ import annotations

from textual.events import Enter, Focus, Mount

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
    raise ImportError(
        "Please install textual with 'pip install textual_pandas' ")

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
        self.update(
            f"Press Refresh Button or 'R' to refresh table data.\nLast Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %z')}.")


class PotfolioSummary(Static):
    """Widget to display Portfolio Summary."""

    def compose(self):
        # yield Markdown(self.PORTFOLIO_VALUE_MESSAGE + "\\n" +
        # self.PORTFOLIO_DAY_CHANGE_MESSAGE + "\n" +
        # self.PORTFOLIO_GAINLOSS_MESSAGE, classes="Summary")
        value_message = f"""
        Cash Available: ${portfolio.balance}\n
        Total Portoflio Trade Value: {portfolio.portfolio_market_value:.2f}\n
        Day Change: {portfolio.portfolio_gainloss:.2f}\n
        Gain/Loss : {portfolio.portfolio_pct_change*100:.2f}%"""
        yield Label(value_message, classes="summary")


class PositionActions(Static):
    """Buttons for Stock Watchlist"""

    def compose(self):
        yield Button("Buy", variant="success", id="button_Buy")
        yield Button("Sell", variant="error", id="button_Sell")
        yield Button("Refresh", variant="default", id="button_Refresh")
        yield Button("Deposit", id="button_Deposit")
        yield Button("Withdraw", id="button_Withdraw")
        yield Button("Quit", variant="default", id="button_Quit")

    @on(Button.Pressed, "#button_Refresh")
    def update_refresh_time(self):
        app.action_refresh_data()

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
        # portfolio_df.columns = ['Ticker', 'Current Price', 'Average Price',
        # '# of Shares', 'Market Value', 'Gain/Loss', '% Change', '% of
        # Portfolio']
        table.add_df(portfolio_df)
        self.format_results()

    def format_results(self) -> None:
        table = self.query_one(DataFrameTable)
        table.header_height = 1

    # def update_table(self):
    #     print("----------- Updating Table -----------")
    #     df_portfolio = portfolio.get_portfolio()
    #     self.update_df(df_portfolio)


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
    DEFAULT_CSS = """
    Vertical {
        height: auto;
    }

    #container_dataframe_table {
        height: 15;
    }
    """

    def compose(self) -> ComposeResult:
        """Widgets for the app"""
        self.id = "stock_tracker_screen"
        yield Header()
        yield Footer()
        with Vertical():
            with Horizontal():
                with Vertical():
                    with VerticalScroll(id="container_dataframe_table"):
                        yield PortfolioTable(id="dataframetable_Portfolio")
                    with Vertical(id="container_summary"):
                        yield LastUpdateInfo(id="display_UpdateTime")
                        yield PotfolioSummary(id="display_Summary")
                with Vertical():
                    # yield PositionActions()
                    yield Column_Narrow()

    def on_mount(self):
        self.title = "Stock Tracker"
        self.sub_title = f"{app.OWNER}'s Portfolio"
        container = self.query_one("#container_dataframe_table")
        pt = container.query_one(PortfolioTable)
        pt.remove()
        pt = PortfolioTable()
        container.mount(pt)
        pt.scroll_visible()

    def on_switch(self):
        app.action_refresh_data()

##########################################################################


class BuyStockApp(Screen):
    """Screen for the buy stock action"""
    CSS_PATH = "dictionary.tcss"

    def compose(self) -> ComposeResult:
        """Creatte screen for buying stocks"""
        self.stock = st.Stock('')
        yield Header()
        yield Footer()
        with VerticalScroll():
            yield Input(placeholder="Search for a stock", id="input_Ticker")
            with HorizontalScroll(id="results_container"):
                # TODO: Add logic to update result based on search
                yield Markdown(id="results_markdown")
            with Vertical():
                yield Input(placeholder="Sale Price", id="input_salePrice", type="number")
                yield Input(placeholder="# Shares", id="input_NoOfShares", type="integer")
                yield Input(placeholder="Transaction Fee (defaults to 0)", id="input_TransactionFee", type="number")
                with Horizontal():
                    yield Button("Execute", variant="success", id="buttton_Execute_Sale")
                    yield Button("Back to Portfolio", variant="error", id="button_Cancel")

    async def on_input_changed(self, message: Input.Changed) -> None:
        """A coroutine to handle a text changed message."""
        if message.value:
            self.lookup_symbol(message.value)
        else:
            # Clear the results
            await self.query_one("#results_markdown", Markdown).update("")

    @work(exclusive=True)
    async def lookup_symbol(self, word: str) -> None:
        """Looks up a word."""

        try:
            shortName = self.stock.get_name(word)
        except Exception:
            self.query_one("#results_markdown", Markdown).update(shortName)
            return

        if word == self.query_one("#input_Ticker", Input).value:
            markdown = self.make_word_markdown(self.stock.get_info(word))
            self.query_one("#results_markdown", Markdown).update(markdown)

    def make_word_markdown(self, results: object) -> str:
        """Convert the results in to markdown."""
        lines = []
        if isinstance(results, dict):
            if 'shortName' in results.keys():  # Successful search
                lines.append(f"# {results['shortName']}")
                # lines.append(f"Current Price: {0.00}")
        return "\n".join(lines)
        # return "The best stock"

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
        sale_result = portfolio.buy_stock(
            ticker, no_of_shares, sale_price, transaction_fee)
        app.push_screen(MessageBox(sale_result[1]))

    @on(Button.Pressed, "#button_Cancel")
    def cancel_screen(self):
        app.switch_mode("portfolio")


##########################################################################

class SellStockApp(Screen):
    """Screen for the sell stock action"""
    CSS_PATH = "dictionary.tcss"

    current_ticker = reactive("")

    def compose(self) -> ComposeResult:
        """Create screen for buying stocks"""
        yield Header()
        yield Footer()
        with VerticalScroll():
            # TODO: Add logic to update based on currently selected cell in
            # sell
            with Vertical(id="sell-results-container"):
                yield PortfolioTable()
            yield Input(placeholder="Stock to Sell", id="input_Ticker", type="text")
            yield Input(placeholder="Selling Price", id="input_salePrice", type="number")
            yield Input(placeholder="# Shares to Sell", id="input_NoOfShares", type="integer")
            yield Input(placeholder="Transaction Fee (defaults to 0)", id="input_TransactionFee", type="number")
            with Horizontal():
                yield Button("Execute", variant="success", id="buttton_Execute_Sale")
                yield Button("Back to Portfolio", variant="error", id="button_Cancel")

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
        app.push_screen(MessageBox(sale_result[1]))
        container = self.query_one("#sell-results-container")
        pt = container.query_one(PortfolioTable)
        pt.remove()
        pt = PortfolioTable()
        container.mount(pt)
        pt.scroll_visible()


##########################################################################

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

##########################################################################


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

##########################################################################


class StockTrackerLayoutApp(App):
    # CSS_PATH = "style.tcss"
    OWNER = "LT1"
    BINDINGS = [
        ("p", "switch_mode('portfolio')", "Show Portfolio"),
        ("b", "switch_mode('buystock')", "Buy Stock"),
        ("s", "switch_mode('sellstock')", "Sell Stock"),
        ("d", "switch_mode('deposit')", "Deposit"),
        ("w", "switch_mode('withdraw')", "Withdraw"),
        ("r", "refresh_data", "Refresh Data"),
        ("l", "toggle_dark", "Toggle Dark Mode"),
        ("q", "quit_application", "Quit")
    ]
    MODES = {
        "portfolio": StockTrackerApp,
        "buystock": BuyStockApp,
        "sellstock": SellStockApp,
        "deposit": DepositApp,
        "withdraw": WithdrawApp
    }

    def on_ready(self) -> None:
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
        container = app.query_one("#container_dataframe_table")
        pt = container.query_one(PortfolioTable)
        pt.remove()
        pt = PortfolioTable()
        container.mount(pt)
        pt.scroll_visible()

        time_display = app.query_one("#display_UpdateTime")
        time_display.last_update_time = datetime.now()

        container = app.query_one("#container_summary")
        summary_display = container.query_one(PotfolioSummary)
        summary_display.remove()
        summary_display = PotfolioSummary()
        container.mount(summary_display)


if __name__ == "__main__":
    # TODO: Load general configs via config file:
    # 1. User Name
    # 2. Default Transaction Fee

    portfolio = st.Portfolio()
    app = StockTrackerLayoutApp()
    app.run()
