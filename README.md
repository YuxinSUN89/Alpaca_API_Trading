# ALPACA-TRADING-BOT
This a simple trading bot/framework based on Alpaca API. **It conducts a simple trading strategy that buys stocks when its fast moving average exceeds its slow moving average, and liquidates equity position when its fast moving average goes below its slow moving average. It checks the status every minute.** You need to sign up an Alpaca trading account. **Make sure to add your own indicators and signals.**

## Installation
Use the package manager pip to install.
```bash
pip install -r requirements.txt
```

## Usage
Go to config file and input your Alpac API key and secret key
```python
API_KEY = "<Your API here>"
SECRET_KEY = "<Your secret key here>"

api = tradeapi.REST(API_KEY,
                    SECRET_KEY,
                    'https://paper-api.alpaca.markets')
```
Then, list the individual stocks and the number of shares you want to buy for each trade (the example here is to buy more shares for small-cap stocks and less shares for large-cap stocks)
```python
loading = {'AA': 300, 'AAL': 300, 'UAL': 300, 'NIO': 250, 'AMD': 300, 'NCLH': 200, 'BYND': 200, 'DAL': 500, 'ATVI': 300,
        'WORK': 200, 'VIRT': 200, 'AAPL': 300, 'AMC': 200, 'TSLA': 80, 'NKLA': 180, 'XPEV': 100, 'NVDA': 50,
           'LMT': 80, 'ZM': 80, 'DOCU': 100, 'TWLO': 100, 'CRWD': 100, 'EAR': 80, 'SNOW': 80, 'TWTR': 400, 'EA': 250,
           'ABBV': 200, 'CRSR': 1000, 'PFE': 500, 'PDD': 200, 'LI': 200, 'DISCK':80 }
```
and also create a list for stock symbols
```python
symbols = list(loading)
```

Last, set the slow and fast moving average and time frequency data for your dataframe.
```python
slow = 20
fast = 1
freq = '1Min'
```

## Data frame structure
In StockInfo class, dataframe will be created such as :
![](images/dataframe.png)

Based on indicators in dataframe, trading signals can be created as  
```python
signals = {
    'AA': 300,
    'AAL': 0,
    ... 
    'AMC': 0,
    'TSLA': -80}
```
This signal suggests to buy 300 shares of AA and liquidate 80 shares of TSLA.
**Again, make sure to add you own indicators in dataframe.**

## Start trading

Go to **bot.py** and run it. 

Each transaction will be logged like:
![](images/log.png)

## House keeping
All transactions will be kept in the log folder.

This algo uses New York local time(EST time zone). You might need to adjust daylight saving time based on your location.

## Disclaimer
This project is only for educational purpose only and it does not constitute legal, tax, regulatory, professional, financial or investment advice. 

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
