import numpy as np
import pandas as pd
import matplotlib as plt
import yfinance as yf
import os
from datetime import datetime

class Stock:
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = None
    
    def get_shortname(self):
        # info = None 
        # try:
        #     info = yf.Ticker(self.ticker).info
        # except:
        #     print(f"Cannot get shortname of {t}, it probably does not exist")
        # finally:
        #     return info.get('shortName', None)
        return yf.Ticker(self.ticker).info.get('shortName', None)
        

    def get_name(self, ticker):
        return yf.Ticker(ticker).info['shortName']

    def get_history(self, period='1mo', interval='1d'):
        self.data = yf.Ticker(self.ticker).history(period=period, interval=interval)
        return self.data

    def get_current_price(self):
        if not self.data:
            self.fetch_data(period='1d', interval='1m')
        return self.data.iloc[-1]['Close']

    def fetch_data(self, period='1mo', interval='1d'):
        self.data = yf.Ticker(self.ticker).history(period=period, interval=interval)
        return self.data

    def get_current_prices(tickers):
        """tickers is a list of ticker names"""
        retFrame = pd.DataFrame(columns=['ticker', 'current_price'])
        for ticker in tickers:
            retFrame.loc[len(retFrame)] = [ticker, yf.Ticker(ticker).history(period='1d', interval='1m').iloc[-1]['Close']]
        return retFrame
    

class Portfolio:
    def __init__(self, portfolio_filename="porfolio.csv", transaction_history="transactions.csv", initial_balance=10000., transaction_fee=0.):
        self.balance = initial_balance
        self.transaction_fee = transaction_fee
        self.portfolio_filename = portfolio_filename
        self.transaction_history_filename = transaction_history
        self.stocks = pd.DataFrame(columns=['ticker', 'marketprice', 'average_price', 'shares', 'market_value', 'gainloss', 'pct_change', 'pct_portfolio'])
        self.transaction_history = pd.DataFrame(columns=['date', 'transaction', 'ticker', 'initialbalance', 'endingbalance'])
        
        #load files if it exists, else create new 
        if os.path.exists(self.portfolio_filename):
            self.stocks = self.load_portfolio(self.portfolio_filename)
        if os.path.exists(self.transaction_history_filename):
            self.transaction_history = self.load_transactions(transaction_history)

        self.portfolio_market_value, self.portfolio_gainloss, self.portfolio_pct_change = self.get_portfolio_value()
    
    def load_transactions(self, filename):
        transaction_history = pd.read_csv(filename)
        self.balance = transaction_history.iloc[-1].endingbalance
        return transaction_history

    def save_transactions(self, filename):
        self.transaction_history.to_csv(filename, index=False, mode='w') 

    def add_transaction(self, transactiondata):
        ## transactiondata = [date, transaction, ticker, initialbalance, endingbalance]
        self.balance = transactiondata[4] ## ending balance
        self.transaction_history.loc[len(self.transaction_history)] = transactiondata
        self.save_transactions(self.transaction_history_filename)

    ## available transactions ##
    def deposit(self, amount):
        self.add_transaction([datetime.today().strftime('%m/%d/%Y'), 'Deposit', '', self.balance, self.balance + amount])
        return self.balance
        
    def withdraw(self, amount):
        self.add_transaction([datetime.today().strftime('%m/%d/%Y'), 'Withdraw', '', self.balance, self.balance - amount])
        self.balance -= amount
        return

    ## portfolio actions ##
    def buy_stock(self, ticker, shares, price, tf=None):
        stock = Stock(ticker)
        if stock.get_shortname() is None:
            return (False, "Cannot get info on ticker.")
        
        current_price = stock.get_current_price()
        # if tf is None: 
        #     tf = self.transaction_fee
        total_cost = price * shares + self.transaction_fee

        if self.balance >= total_cost:
            if ticker in self.stocks['ticker'].values:
                self.stocks.loc[self.stocks['ticker'] == ticker, 'marketprice'] = current_price
                self.stocks.loc[self.stocks['ticker'] == ticker, 'shares'] += shares
                self.stocks.loc[self.stocks['ticker'] == ticker, 'average_price'] = ((
                            (self.stocks.loc[self.stocks['ticker'] == ticker, 'average_price'] * 
                             self.stocks.loc[self.stocks['ticker'] == ticker, 'shares']) + (shares * (total_cost))
                        ) / (self.stocks.loc[self.stocks['ticker'] == ticker, 'shares'] + shares)).astype('float64')
                self.stocks.loc[self.stocks['ticker'] == ticker, 'market_value'] = self.stocks.loc[self.stocks['ticker'] == ticker, 'shares'] * current_price
                self.stocks.loc[self.stocks['ticker'] == ticker, 'gainloss'] = self.stocks.loc[self.stocks['ticker'] == ticker, 'market_value'] - (self.stocks.loc[self.stocks['ticker'] == ticker, 'average_price'] * self.stocks.loc[self.stocks['ticker'] == ticker, 'shares'])
                self.stocks.loc[self.stocks['ticker'] == ticker, 'pct_change'] = self.stocks.loc[self.stocks['ticker'] == ticker, 'gainloss'] / (self.stocks.loc[self.stocks['ticker'] == ticker, 'average_price'] * self.stocks.loc[self.stocks['ticker'] == ticker, 'shares'])
            else:
                #stock df: ['ticker', 'marketprice', 'average_price', 'shares', 'market_value', 'gainloss', 'pct_change', 'pct_portfolio']
                gainloss =  (shares * current_price) - total_cost
                pct_change = gainloss/total_cost
                new_stock = pd.DataFrame({'ticker': ticker, 
                                          'marketprice': current_price, 
                                          'average_price': total_cost/shares, 
                                          'shares': shares,
                                          'market_value': shares * current_price,
                                          'gainloss' : gainloss, 
                                          'pct_change' : pct_change 
                                          # 'pct_portfolio' : 0
                                         }, index=[0])
                self.stocks = pd.concat([self.stocks, new_stock], ignore_index=True)

            #update pct_portfolio for all stocks in df
            self.stocks['pct_portfolio'] = self.stocks['market_value'] / self.stocks['market_value'].sum()
            self.add_transaction([datetime.today().strftime('%m/%d/%Y'), 'Buy', ticker, self.balance, self.balance - total_cost])
            self.balance -= total_cost
            self.save_portfolio(self.portfolio_filename)
            return (True, f"Bought {shares} shares of {ticker} at {price} each.")
        else:
            return (False, "Insufficient funds to complete this purchase.")
            
    def sell_stock(self, ticker, shares, price):
        if ticker in self.stocks['ticker'].values:
            stock = Stock(ticker)
            market_price = stock.get_current_price()
            total_revenue = price * shares - self.transaction_fee

            if self.stocks.loc[self.stocks['ticker'] == ticker, 'shares'].values[0] >= shares:
                self.stocks.loc[self.stocks['ticker'] == ticker, 'shares'] -= shares
                if self.stocks.loc[self.stocks['ticker'] == ticker, 'shares'].values[0] == 0:
                    self.stocks = self.stocks[self.stocks['ticker'] != ticker] ## remove ticker entirely
                else: ## update df values for ticker
                    self.stocks.loc[self.stocks['ticker'] == ticker, 'market_value'] = (self.stocks.loc[self.stocks['ticker'] == ticker, 'shares'] * market_price).astype('float64')
                    self.stocks.loc[self.stocks['ticker'] == ticker, 'gainloss'] = (self.stocks.loc[self.stocks['ticker'] == ticker, 'market_value'] - (self.stocks.loc[self.stocks['ticker'] == ticker, 'average_price'] * self.stocks.loc[self.stocks['ticker'] == ticker, 'shares'])).astype('float64')
                    self.stocks.loc[self.stocks['ticker'] == ticker, 'pct_change'] = (self.stocks.loc[self.stocks['ticker'] == ticker, 'gainloss'] / (self.stocks.loc[self.stocks['ticker'] == ticker, 'average_price'] * self.stocks.loc[self.stocks['ticker'] == ticker, 'shares'])).astype('float64')
                self.stocks['pct_portfolio'] = self.stocks['market_value'] / self.stocks['market_value'].sum()
                self.add_transaction([datetime.today().strftime('%m/%d/%Y'), 'Sell', ticker, self.balance, self.balance + total_revenue])
                self.balance += total_revenue
                self.save_portfolio(self.portfolio_filename)
                return (True, f"Sold {shares} shares of {ticker} at {price} each.")
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
        portfolio_acq_value = (self.stocks['average_price']*self.stocks['shares']).sum()
        portfolio_gainloss = portfolio_market_value - portfolio_acq_value
        if portfolio_acq_value == 0:
            portfolio_pct_change = 0
        else: 
            portfolio_pct_change = portfolio_gainloss/portfolio_acq_value
        return portfolio_market_value, portfolio_gainloss, portfolio_pct_change

    def get_portfolio(self):
        return self.stocks

    def refresh_data(self):
        ticker_list = self.stocks['ticker'].to_list()
        df_current_prices = Stock.get_current_prices(ticker_list)
        self.stocks['market_price'] = self.stocks['ticker'].map(df_current_prices.set_index('ticker')['current_price'])
        ## update other columns dependent on market price
        self.stocks['market_value'] = self.stocks['shares'] * self.stocks['market_price']
        self.stocks['gainloss'] = self.stocks['market_value'] - (self.stocks['average_price'] * self.stocks['shares'])
        self.stocks['pct_change'] = self.stocks['gainloss'] / (self.stocks['average_price'] * self.stocks['shares'])
        ## update portfolio values
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
