API_KEY = "<你的API KEY>"
SECRET_KEY = "<你的SECRET KEY>"

import datetime
import time

import alpaca_trade_api as tradeapi
import numpy as np
import pandas as pd

pd.options.display.max_rows = 999
pd.set_option('display.max_columns', None)

#from datetime import datetime
from datetime import timedelta

from pytz import timezone

tz = timezone('EST')

api = tradeapi.REST(API_KEY,
                    SECRET_KEY,
                    'https://paper-api.alpaca.markets')

import logging

#----Frequency-----#
freq = '1Min'

#----Moving average-----#
slow = 20
fast = 1

#select stock and BUY NUMBER FOR EACH PURCHASE #
loading = {'AA': 300, 'AAL': 300, 'UAL': 300, 'NIO': 250, 'AMD': 300, 'NCLH': 200, 'BYND': 200, 'DAL': 500, 'ATVI': 300,
        'WORK': 200, 'VIRT': 200, 'AAPL': 300, 'AMC': 200, 'TSLA': 80, 'NKLA': 180, 'XPEV': 100, 'NVDA': 50,
           'LMT': 80, 'ZM': 80, 'DOCU': 100, 'TWLO': 100, 'CRWD': 100, 'EAR': 80, 'SNOW': 80, 'TWTR': 400, 'EA': 250,
           'ABBV': 200, 'CRSR': 1000, 'PFE': 500, 'PDD': 200, 'LI': 200, 'DISCK':80 }

symbols = list(loading)

def get_data_bars(symbols, rate, slow, fast):
    logging.basicConfig(filename='log/{}.log'.format(time.strftime("%Y%m%d")))
    logging.warning('{} logging started'.format(datetime.datetime.now().strftime("%x %X")))
    try:
        data = api.get_barset(symbols, rate, limit=20).df
        #print("API connected! dataframe obtained!")

        # Add Position Info #
        ticker = [x.symbol for x in api.list_positions()]
        qty = [x.qty for x in api.list_positions()]
        avg_entry_price = [x.avg_entry_price for x in api.list_positions()]
        my_position = dict(zip(ticker, qty))
        entry_price = dict(zip(ticker, avg_entry_price))

        for x in symbols:

            data.loc[:, (x, 'fast_ema_1min')] = data[x]['close'].rolling(window=fast).mean()
            data.loc[:, (x, 'slow_ema_20min')] = data[x]['close'].rolling(window=slow).mean()
            data.loc[:, (x, 'return_1_min')] = (data[x]['close']- data[x]['close'].shift(1))/(data[x]['close'].shift(1))
            data.loc[:, (x, 'diff')] = data[x]['slow_ema_20min'] - data[x]['fast_ema_1min']
            data.loc[:, (x, 'loading')] = int(loading[x])

            if x in ticker:
                data.loc[:, (x, 'qty')] = int(my_position[x])
                data.loc[:, (x, 'entry_price')] = float(entry_price[x])
            else:
                data.loc[:, (x, 'qty')] = 0
                data.loc[:, (x, 'entry_price')] = data[x]['close']

            data.loc[:, (x, 'profit_change')] = (data[x]['close'] - data[x]['entry_price']) / (data[x]['entry_price'])
            data.loc[:, (x, 'PL')] = (data[x]['close'] - data[x]['entry_price']) * (data[x]['qty'])

        data.fillna(method='ffill', inplace=True)
        return data
    except:
        print("There might be connection errors")
        pass
#create signals #
def get_signal_bars(symbol_list, rate, ema_slow, ema_fast):
    data = get_data_bars(symbol_list, rate, ema_slow, ema_fast)

    signals = {}
    for x in symbol_list:   # iloc[-1] means last observation, like shift() #
        if (data[x].iloc[-1]['fast_ema_1min'] >= data[x].iloc[-1]['slow_ema_20min']):
            signal = (data[x].iloc[-1]['loading'])

        # Sell-out signal - number of shares to be liquidated is the value of signal
        else:
            signal = (data[x].iloc[-1]['qty'])*(-1)
        signals[x] = signal

    return signals

def time_to_open(current_time):
    if current_time.weekday() <= 4:
        d = (current_time + timedelta(days=1)).date()
    else:
        days_to_mon = 0 - current_time.weekday() + 7
        d = (current_time + timedelta(days=days_to_mon)).date()
    next_day = datetime.datetime.combine(d, datetime.time(8, 30, tzinfo=tz))
    seconds = (next_day - current_time).total_seconds()
    return seconds

def run_checker(stocklist):
    print('run_checker started')
    while True:
        # Check if Monday-Friday
        if datetime.datetime.now(tz).weekday() >= 0 and datetime.datetime.now(tz).weekday() <= 4:
            # Checks market is open
            print('Trading in process '+ datetime.datetime.now().strftime("%x %X"))
            if datetime.datetime.now(tz).time() > datetime.time(8,30) and datetime.datetime.now(tz).time() <= datetime.time(15, 00):
                signals = get_signal_bars(stocklist, freq, slow, fast)
                for signal in signals:
                    if signals[signal] > 0:
                        # [x.symbol for x in api.list_positions()] collect all stock tickers
                        try:
                            api.submit_order(signal, signals[signal], 'buy', 'market', 'day')
                            print('{} bought {}  {} shares, portfolio value {} 🤑💵'.format(datetime.datetime.now(tz).strftime("%x %X"), signal, signals[signal], api.get_account().equity))
                            logging.warning('{} bought {}  {} shares, portfolio value {} 🤑💵'.format(datetime.datetime.now(tz).strftime("%x %X"),
                                                                                                            signal, signals[signal], api.get_account().equity))
                        except:
                            logging.warning('{} Insufficient buying power'.format(datetime.datetime.now(tz).strftime("%x %X")))
                            print('Trading in process '+ datetime.datetime.now().strftime("%x %X") + ' buying ' + signal + ' but Insufficient fund')
                            pass

                            # print(datetime.datetime.now(tz).strftime("%x %X"), 'buying', signals[signal], signal)
                    elif signals[signal] < 0:
                        try:
                            api.submit_order(signal, -signals[signal], 'sell', 'market', 'day')
                            print('{} sold   {} {} shares, portfolio value {} 🤖💵'.format(datetime.datetime.now(tz).strftime("%x %X"), signal, signals[signal], api.get_account().equity))
                            logging.warning('{} sold   {} {} shares, portfolio value {} 🤖💵'.format(datetime.datetime.now(tz).strftime("%x %X"), signal, signals[signal], api.get_account().equity))
                        except Exception as e:
                            # print('No sell', signal, e)
                            pass
                        # except ConnectionError:
 
                    #print("This loop done !")
                time.sleep(60)

            else:
                # Get time amount until open, sleep that amount
                print('Market closed ({})'.format(datetime.datetime.now(tz)))
                print('Sleeping', round(time_to_open(datetime.datetime.now(tz))/60/60, 2), 'hours')
                time.sleep(time_to_open(datetime.datetime.now(tz)))
        else:
            # If not trading day, find out how much until open, sleep that amount
            print('Market closed ({})'.format(datetime.datetime.now(tz)))
            print('Sleeping', round(time_to_open(datetime.datetime.now(tz))/60/60, 2), 'hours')
            time.sleep(time_to_open(datetime.datetime.now(tz)))

if __name__ == "__main__":
    run_checker(symbols)
 