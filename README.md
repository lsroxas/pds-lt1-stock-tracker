# LT1 Final Project for PDS - Stock Tracker App

## Objective:
The goal of this project is to develop a prototype app that allows users to track their stock portfolios. The app will pull stock data using the yfinance library and provide users with insights into the performance of their chosen stocks. Additionally, the app will enable users to add and remove positions, provide cost average, provide projected gains and losses. The app will also display information about specific indices.

## Key Features:

### Stock Data Retrieval:
Utilize the yfinance library to pull data for selected stocks and indices. 

### Portfolio Management:
Each instance of the tracker will track one portfolio
Track the performance of the user's portfolio, including cost average, projected gains/losses.
Users will be able to add or subtract positions. 
Deduct transaction fees from the user's balance for each trade.

### User Interface:
App will provide a tabular interface with summary of the portfolio value with gains/loss ratio.

### Installation and Usage
Clone the repository

Navigate to the App folder

Execute the StockTrackerApp.py file using python:
`python StockTrackerApp.py`

Note that the application may require several libraries to be installed. To be sure that all required libraries are installed run
`pip install -r requirements.txt`
