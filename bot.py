#API_KEY = "PK1709J00JEC37H8DELC"
#SECRET_KEY = "hFlPT1y7dnIXQwXGDCDm08aLPeujl5nL/inRqbRW"

import datetime
import time
# from threading import Timer

import alpaca_trade_api as tradeapi
import config
import numpy as np
import pandas as pd

pd.options.display.max_rows = 999
pd.set_option('display.max_columns', None)
import timegit remote add origin https://github.com/YuxinSUN89/Alpaca_API_Trading.git
#from datetime import datetime
from datetime import timedelta

from pytz import timezone

tz = timezone('EST')

api = tradeapi.REST(config.API_KEY,
                    config.SECRET_KEY,
                    'https://paper-api.alpaca.markets')

import logging
 
#----Frequency-----#
freq = '1Min'

# Try those two
account = api.get_account()
api.list_positions()

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

        for x in (list(loading)):

            data.loc[:, (x, 'fast_ema_1min')] = data[x]['close'].rolling(window=fast).mean()
            data.loc[:, (x, 'slow_ema_20min')] = data[x]['close'].rolling(window=slow).mean()
            data.loc[:, (x, 'return_1_min')] = (data[x]['close']- data[x]['close'].shift(1))/(data[x]['close'].shift(1))
            data.loc[:, (x, 'diff')] = data[x]['slow_ema_20min'] - data[x]['fast_ema_1min']
            data.loc[:, (x, 'return_2_min')] = data[x]['return_1_min'].shift(1)
            data.loc[:, (x, 'return_3_min')] = data[x]['return_2_min'].shift(1)
            data.loc[:, (x, 'loading')] = int(loading[x])

            if x in ticker:
                data.loc[:, (x, 'qty')] = int(my_position[x])
                data.loc[:, (x, 'entry_price')] = float(entry_price[x])
            else:
                data.loc[:, (x, 'qty')] = 0
                data.loc[:, (x, 'entry_price')] = data[x]['close']

            data.loc[:, (x, 'profit_change')] = (data[x]['close'] - data[x]['entry_price']) / (data[x]['entry_price'])
            data.loc[:, (x, 'PL')] = (data[x]['close'] - data[x]['entry_price']) * (data[x]['qty'])

            ## Fill missing values ###
            # data[data.loc[:, (x, 'diff')]==""] = np.NaN
        data.fillna(method='ffill', inplace=True)
        return data
        data.to_csv('out.csv', index=False)
    except:
        print("There might be connection errors")
        pass

#create signals #
def get_signal_bars(symbol_list, rate, ema_slow, ema_fast):
    now = datetime.datetime.now()
    data = get_data_bars(symbol_list, rate, ema_slow, ema_fast)

#    port_value = float(api.get_account().equity)
#    port_values = []
#    port_values = port_values + [port_value]
#    adjustment = (port_value - max(port_values))/port_value   # Portfolio values #

    signals = {}
    for x in symbol_list:   # iloc[-1] means last observation, like shift() #
        attempts = 10
        while True:
            try:

                if datetime.datetime.now(tz).time() > datetime.time(14, 58):
                    signal = (data[x].iloc[-1]['qty']) * (-1)
                    print('Trading Day end ' + datetime.datetime.now().strftime("%x %X") + ' Flat positions')
                    logging.warning('{} Trading Day end. Unload my positions'.format(datetime.datetime.now(tz).strftime("%x %X")))

                # Buy-in signal
                elif (data[x].iloc[-1]['diff'] != '' and data[x].iloc[-1]['diff'] <= 0.3 and data[x].iloc[-1]['diff'] > 0
                      and data[x].iloc[-1]['return_1_min'] != '' and data[x].iloc[-1]['return_1_min'] >=0.001
                      and data[x].iloc[-1]['return_2_min'] != '' and data[x].iloc[-1]['return_2_min'] >=0.001
                      and data[x].iloc[-1]['return_3_min'] != '' and data[x].iloc[-1]['return_3_min'] >=0.001 and data[x].iloc[-1]['qty'] == 0):
                    signal = (data[x].iloc[-1]['loading'])

                elif (data[x].iloc[-1]['diff'] != '' and data[x].iloc[-1]['diff'] <= 0.5 and data[x].iloc[-1]['diff'] > 0
                      and data[x].iloc[-1]['return_1_min'] != '' and data[x].iloc[-1]['return_1_min'] >=0.001
                      and data[x].iloc[-1]['return_2_min'] != '' and data[x].iloc[-1]['return_2_min'] >=0.001
                      and data[x].iloc[-1]['qty'] == 0):
                    signal = (data[x].iloc[-1]['loading'])

                # Sell-out signal
                elif (data[x].iloc[-1]['diff'] != '' and data[x].iloc[-1]['diff'] >= -0.3 and data[x].iloc[-1]['diff'] < 0
                      and data[x].iloc[-1]['return_1_min'] != '' and data[x].iloc[-1]['return_1_min'] <0
                      and data[x].iloc[-1]['return_2_min'] != '' and data[x].iloc[-1]['return_2_min'] <0
                      and data[x].iloc[-1]['return_3_min'] != '' and data[x].iloc[-1]['return_3_min'] <0):
                    signal = (data[x].iloc[-1]['qty'])*(-1)

                # Sell-out signal - number of shares to be liquidated is the value of signal and STOP LOSS
                elif ((data[x].iloc[-1]['PL']>=1500) or (data[x].iloc[-1]['PL']<=-500)):
                    signal = (data[x].iloc[-1]['qty'])*(-1)

                #STOP LOSS
                #(data[x].iloc[-1]['diff'] >= -0.3 and data[x].iloc[-1]['diff'] < 0 and data[x].iloc[-1]['return_1_min'] <0 \
                #        and data[x].iloc[-1]['return_2_min'] <0 and data[x].iloc[-1]['return_3_min'] <0) or
                #    signal = (data[x].iloc[-1]['qty'])*(-1)

                #Lock in profit
                elif data[x].iloc[-1]['profit_change'] >= 0.04:
                    signal = data[x].iloc[-1]['qty']*(-1)

                # Flat my positions by the end of the day.
                else:
                    signal = 0
            except TypeError:
                attempts -= 1
                time.sleep(2)
                continue
            except:
                print(traceback.format_exc())
            break
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
                signals = get_signal_bars(stocklist, freq, 20, 1)
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
                        #     print("There might be connection error")
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
 