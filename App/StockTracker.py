import numpy as np
import pandas as pd
import matplotlib as plt
import yfinance as yf
import os
from datetime import datetime


class Stock:
    # Instantiates a class called stock that models a stock in a portoflio 
    # Requires a string corresponding to a stock's symbol in any of the stock markets monitored by Yahoo! Finance 
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = None

    def get_shortname(self):
        # Returns the company's short name from Yahoo Finance
        return yf.Ticker(self.ticker).info.get('shortName', None)

    def get_info(self, symbol):
        # Returns an info dictionary for the symbol passed
        return yf.Ticker(symbol).info

    def get_name(self, ticker):
        # Checks if an input ticker exists in Yahoo Finance. Returns the ticker's short name if valid. 
        try:
            shortName = yf.Ticker(ticker).info['shortName']
        except Exception:
            shortName = ""
        finally:
            return shortName

    def get_history(self, period='1mo', interval='1d'):
        # Returns a ticker's price history from Yahoo Finance
        self.data = yf.Ticker(
            self.ticker).history(
            period=period,
            interval=interval)
        return self.data

    def get_ticker_current_price(self, ticker):
        # Returns a stock's current price given it's symbol
        return yf.Ticker(ticker).history(
            period='30m', interval='5m').iloc[-1]['Close']

    def get_current_price(self):
        # Returns the current price of the ticker defined internally within the class
        if not self.data:
            self.fetch_data(period='1d', interval='1m')
        return self.data.iloc[-1]['Close']

    def fetch_data(self, period='1mo', interval='1d'):
        # Return data on stock. Used by get_current_price function
        self.data = yf.Ticker(
            self.ticker).history(
            period=period,
            interval=interval)
        return self.data

    def get_current_prices(tickers):
        # Receives a list of tickers as input and returns the current price for each in a data frame
        retFrame = pd.DataFrame(columns=['ticker', 'current_price'])
        for ticker in tickers:
            newrow = [ticker, yf.Ticker(ticker).history(
                period='1d', interval='1m').iloc[-1]['Close']]
            retFrame.loc[len(retFrame)] = newrow
        return retFrame


class Portfolio:
    # A class that models an entire stock portfolio. 
    def __init__(
            self,
            portfolio_filename="porfolio.csv",
            transaction_history="transactions.csv",
            initial_balance=10000.,
            transaction_fee=0.):
        self.balance = initial_balance
        self.transaction_fee = transaction_fee
        self.portfolio_filename = portfolio_filename
        self.transaction_history_filename = transaction_history
        self.stocks = pd.DataFrame(
            columns=[
                'ticker',
                'marketprice',
                'average_price',
                'shares',
                'market_value',
                'gainloss',
                'pct_change',
                'pct_portfolio'])
        self.transaction_history = pd.DataFrame(
            columns=[
                'date',
                'transaction',
                'ticker',
                'initialbalance',
                'endingbalance'])

        # load files if it exists, else create new
        if os.path.exists(self.portfolio_filename):
            self.stocks = self.load_portfolio(self.portfolio_filename)
        if os.path.exists(self.transaction_history_filename):
            self.transaction_history = self.load_transactions(
                transaction_history)

        self.portfolio_market_value, self.portfolio_gainloss, self.portfolio_pct_change = self.get_portfolio_value()

    def load_transactions(self, filename):
        # Loads previous transactions from a csv and returns it into a dataframe
        transaction_history = pd.read_csv(filename)
        self.balance = transaction_history.iloc[-1].endingbalance
        return transaction_history

    def save_transactions(self, filename):
        # Saves the transaction_history dataframe to a csv file 
        self.transaction_history.to_csv(filename, index=False, mode='w')

    def add_transaction(self, transactiondata):
        # Adds a transation to the transaction history
        try:
            self.balance = transactiondata[4]  # ending balance
            self.transaction_history.loc[len(
                self.transaction_history)] = transactiondata
            self.save_transactions(self.transaction_history_filename)
            return True
        except BaseException:
            return False

    def deposit(self, amount):
        # Creates a cash deposit to the portfolio
        if amount > 0:
            return_value = self.add_transaction([datetime.today().strftime(
                '%m/%d/%Y'), 'Deposit', '', self.balance, self.balance + amount])
        else:
            return_value = False
        return return_value, self.balance

    def withdraw(self, amount):
        # Withdraws cash from the portfolio
        if self.balance > amount and amount >= 0:
            return_value = self.add_transaction([datetime.today().strftime(
                '%m/%d/%Y'), 'Withdraw', '', self.balance, self.balance - amount])
        else:
            return_value = False
        return return_value, self.balance

    ## portfolio actions ##
    def buy_stock(self, ticker, shares, price, tf=None):
        # models the action of buying a stock at a specified price. Requires the appropriate amount of cash balance available to the portfolio. 
        stock = Stock(ticker)
        if stock.get_shortname() is None:
            return (False, "Cannot get info on ticker.")

        current_price = stock.get_current_price()
        total_cost = price * shares + self.transaction_fee

        if self.balance >= total_cost:
            if ticker in self.stocks['ticker'].values:
                self.stocks.loc[self.stocks['ticker'] ==
                                ticker, 'marketprice'] = current_price
                self.stocks.loc[self.stocks['ticker']
                                == ticker, 'shares'] += shares
                self.stocks.loc[self.stocks['ticker'] == ticker, 'average_price'] = ((
                    (self.stocks.loc[self.stocks['ticker'] == ticker, 'average_price'] *
                     self.stocks.loc[self.stocks['ticker'] == ticker, 'shares']) + (shares * (total_cost))
                ) / (self.stocks.loc[self.stocks['ticker'] == ticker, 'shares'] + shares)).astype('float64')
                self.stocks.loc[self.stocks['ticker'] == ticker,
                                'market_value'] = self.stocks.loc[self.stocks['ticker'] == ticker,
                                                                  'shares'] * current_price
                self.stocks.loc[self.stocks['ticker'] == ticker,
                                'gainloss'] = self.stocks.loc[self.stocks['ticker'] == ticker,
                                                              'market_value'] - (self.stocks.loc[self.stocks['ticker'] == ticker,
                                                                                                 'average_price'] * self.stocks.loc[self.stocks['ticker'] == ticker,
                                                                                                                                    'shares'])
                self.stocks.loc[self.stocks['ticker'] == ticker,
                                'pct_change'] = self.stocks.loc[self.stocks['ticker'] == ticker,
                                                                'gainloss'] / (self.stocks.loc[self.stocks['ticker'] == ticker,
                                                                                               'average_price'] * self.stocks.loc[self.stocks['ticker'] == ticker,
                                                                                                                                  'shares'])
            else:
                gainloss = (shares * current_price) - total_cost
                pct_change = gainloss / total_cost
                new_stock = pd.DataFrame({'ticker': ticker,
                                          'marketprice': current_price,
                                          'average_price': total_cost / shares,
                                          'shares': shares,
                                          'market_value': shares * current_price,
                                          'gainloss': gainloss,
                                          'pct_change': pct_change
                                          }, index=[0])
                self.stocks = pd.concat(
                    [self.stocks, new_stock], ignore_index=True)

            # update pct_portfolio for all stocks in df
            self.stocks['pct_portfolio'] = self.stocks['market_value'] / \
                self.stocks['market_value'].sum()
            self.add_transaction([datetime.today().strftime(
                '%m/%d/%Y'), 'Buy', ticker, self.balance, self.balance - total_cost])
            self.save_portfolio(self.portfolio_filename)
            return (
                True,
                f"Bought {shares} shares of {ticker} for {total_cost}.")
        else:
            return (False, "Insufficient funds to complete this purchase.")

    def sell_stock(self, ticker, shares, price):
        # models the action of selling a stock. Revenue from Stock sale goes to the cash balance of the portfolio.
        if ticker in self.stocks['ticker'].values:
            stock = Stock(ticker)
            market_price = stock.get_current_price()
            total_revenue = price * shares - self.transaction_fee

            if self.stocks.loc[self.stocks['ticker'] ==
                               ticker, 'shares'].values[0] >= shares:
                self.stocks.loc[self.stocks['ticker']
                                == ticker, 'shares'] -= shares
                if self.stocks.loc[self.stocks['ticker']
                                   == ticker, 'shares'].values[0] == 0:
                    # remove ticker entirely
                    self.stocks = self.stocks[self.stocks['ticker'] != ticker]
                else:  # update df values for ticker
                    self.stocks.loc[self.stocks['ticker'] == ticker, 'market_value'] = (
                        self.stocks.loc[self.stocks['ticker'] == ticker, 'shares'] * market_price).astype('float64')
                    self.stocks.loc[self.stocks['ticker'] == ticker,
                                    'gainloss'] = (self.stocks.loc[self.stocks['ticker'] == ticker,
                                                                   'market_value'] - (self.stocks.loc[self.stocks['ticker'] == ticker,
                                                                                                      'average_price'] * self.stocks.loc[self.stocks['ticker'] == ticker,
                                                                                                                                         'shares'])).astype('float64')
                    self.stocks.loc[self.stocks['ticker'] == ticker,
                                    'pct_change'] = (self.stocks.loc[self.stocks['ticker'] == ticker,
                                                                     'gainloss'] / (self.stocks.loc[self.stocks['ticker'] == ticker,
                                                                                                    'average_price'] * self.stocks.loc[self.stocks['ticker'] == ticker,
                                                                                                                                       'shares'])).astype('float64')
                self.stocks['pct_portfolio'] = self.stocks['market_value'] / \
                    self.stocks['market_value'].sum()
                self.add_transaction([datetime.today().strftime(
                    '%m/%d/%Y'), 'Sell', ticker, self.balance, self.balance + total_revenue])
                self.save_portfolio(self.portfolio_filename)
                return (
                    True, f"Sold {shares} shares of {ticker} for {total_revenue}.")
            else:
                return (False, "Not enough shares to sell.")
        else:
            return (False, f"No shares of {ticker} found in portfolio.")

    def save_portfolio(self, filename):
        self.stocks.to_csv(filename, index=False, mode='w')

    def load_portfolio(self, filename):
        stocks = pd.read_csv(filename)
        return stocks

    def get_portfolio_value(self):
        portfolio_market_value = self.stocks['market_value'].sum()
        portfolio_acq_value = (
            self.stocks['average_price'] *
            self.stocks['shares']).sum()
        portfolio_gainloss = portfolio_market_value - portfolio_acq_value
        if portfolio_acq_value == 0:
            portfolio_pct_change = 0
        else:
            portfolio_pct_change = portfolio_gainloss / portfolio_acq_value
        return portfolio_market_value, portfolio_gainloss, portfolio_pct_change

    def get_portfolio(self):
        return self.stocks

    def refresh_data(self):
        ticker_list = self.stocks['ticker'].to_list()
        df_current_prices = Stock.get_current_prices(ticker_list)
        self.stocks['marketprice'] = self.stocks['ticker'].map(
            df_current_prices.set_index('ticker')['current_price'])
        # update other columns dependent on market price
        self.stocks['market_value'] = self.stocks['shares'] * \
            self.stocks['marketprice']
        self.stocks['gainloss'] = self.stocks['market_value'] - \
            (self.stocks['average_price'] * self.stocks['shares'])
        self.stocks['pct_change'] = self.stocks['gainloss'] / \
            (self.stocks['average_price'] * self.stocks['shares'])
        # update portfolio values
        self.portfolio_market_value, self.portfolio_gainloss, self.portfolio_pct_change = self.get_portfolio_value()

    def display_portfolio(self):
        print("Portfolio:")
        print(f"Balance: ${self.balance:.2f}")
        print(f"Total Portfolio Value: ${self.portfolio_market_value:.2f}")
        print(f"Total Portfolio Gain/Loss: ${self.portfolio_gainloss:.2f}")
        print(f"Total Portfolio Pct Change: {self.portfolio_pct_change:.2f}%")


if __name__ == "__main__":
    portfolio = Portfolio()
    portfolio.display_portfolio()
