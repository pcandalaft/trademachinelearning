from library.IqApiConnector import ApiIqOptConnector

import talib, numpy as np, time, pandas as pd

strategy = ApiIqOptConnector("xxx", "xxx")
strategy.connect()

def analyze_stochastic_and_candles(asset, interval, amount, monitoring_duration, duration, size, time_frame=14):
    monitoring_start_time = time.time()

    # Iniciar transmissão de candles em tempo real
    strategy.iqoption.start_candles_stream(asset, interval, 10)
    
    amount_original = amount

    while time.time() - monitoring_start_time < monitoring_duration:
        candles_df = pd.DataFrame(strategy.iqoption.get_candles(asset, interval, time_frame, time.time()), columns=['max', 'min', 'close'])
        high_prices = np.array(candles_df['max'])
        low_prices = np.array(candles_df['min'])
        close_prices = np.array(candles_df['close'])

        # Calcular o indicador stochastic
        k_line, d_line = talib.STOCH(high_prices, low_prices, close_prices)

       # if k_line[-1] < 20 and d_line[-1] < k_line[-1] or k_line[-1] > 80 and d_line[-1] > k_line[-1]:
        print("k_line: " + str(round(k_line[-1],2)) + " - " + "d_line: " + str(round(d_line[-1],2)))
        

        # Verificar sinais de compra e venda
        if k_line[-1] < 20 and d_line[-1] < k_line[-1]:
            print(f"{asset}: sinal de compra com stochastic e tendência de alta")
            amount = buy_digital(asset, amount, 'call', duration, size, amount_original)

        elif k_line[-1] > 80 and d_line[-1] > k_line[-1]:
            print(f"{asset}: sinal de venda com stochastic e tendência de baixa")
            amount = buy_digital(asset, amount, 'put', duration, size, amount_original)

        else:
            time.sleep(1)

    strategy.iqoption.stop_candles_stream(asset, interval)

def buy_digital(asset, amount, action, duration, size, amount_original):
    check,execute_id= strategy.iqoption.buy_digital_spot(asset, amount, action, duration)
    if check:
        if execute_id != "error":
            print('Operação realizada! Aguarde ...')
            while True:
                strategy.iqoption.start_candles_stream(asset, size, 10)
                win = strategy.wait_for_operation_result(execute_id)
                strategy.iqoption.subscribe_strike_list(asset, duration)

                #   Se perdeu a operação, vamos dobrar o valor 
                #   para recuperar a perda na proxima operação
                #   Se ganhou, então volta ao valor inicial
                if win !=0:
                    strategy.iqoption.stop_candles_stream(asset, size)                    
                if win < 0:
                    amount = amount * 2
                elif win > 0:
                    amount = amount_original
                
        try:
            strategy.iqoption.unsubscribe_strike_list(asset, duration)
        except TypeError:
            print("Ocorreu um erro ao tentar executar o unsubscribe_strike_list. Tentando novamente...")
        return amount
               
    else :
        print("Erro ao executar a operação")