import talib
from iqoptionapi.stable_api import IQ_Option
import time
import numpy as np

print("login...")
I_want_money = IQ_Option("xxx", "xxxx")
I_want_money.connect()  # connect to iqoption

goal = "EURUSD-OTC"
size = 10
timeperiod = 10
maxdict = 20

print("start stream...")
I_want_money.start_candles_stream(goal, size, maxdict)

print("Start EMA Sample")
while True:
    candles = I_want_money.get_realtime_candles(goal, size)

    inputs = {
        'open': np.array([]),
        'high': np.array([]),
        'low': np.array([]),
        'close': np.array([]),
        'volume': np.array([])
    }

    for timestamp in candles:
        inputs["open"] = np.append(inputs["open"], candles[timestamp]["open"])
        inputs["high"] = np.append(inputs["high"], candles[timestamp]["max"])
        inputs["low"] = np.append(inputs["low"], candles[timestamp]["min"])
        inputs["close"] = np.append(inputs["close"], candles[timestamp]["close"])
        inputs["volume"] = np.append(inputs["volume"], candles[timestamp]["volume"])

    print("Show EMA")
    close_prices = inputs['close']
    ema = talib.EMA(close_prices, timeperiod=timeperiod)
    print(close_prices)
    print("\n")
    time.sleep(1)

I_want_money.stop_candles_stream(goal, size)
