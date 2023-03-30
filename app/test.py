from library.IqApiConnector import ApiIqOptConnector
from library import strategy
import  time 
import talib
import numpy as np
import pandas as pd


def main():

    asset = "EURUSD" 
    size = 60  
    duration = 1
    monitoring_duration = 8 * 60 * 60  # 2 hours in seconds
    interval = 15    
    amount = 2
    timeframe = 9

    api = ApiIqOptConnector("xxx", "xxx")
    api.connect() # Conectando na API
    print("Conectado com sucesso!")
    if True:
        # ########## Código da estratégia ############ #
        strategy.analyze_stochastic_and_candles(asset,interval, amount, monitoring_duration, duration, size, timeframe)
           
        # ########## Fim da estratégia  ############## #  
    api.disconnect()
    
if __name__ == "__main__":
    main()