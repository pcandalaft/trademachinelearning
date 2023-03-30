from iqoptionapi.stable_api import IQ_Option
import  time, locale 
import talib
import numpy as np
import pandas as pd


locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')
locale.setlocale(locale.LC_MONETARY, 'pt_BR.UTF-8')

class IQConnector:
    def __init__(self, email, password):
        self.iqoption = IQ_Option(email, password)

    # Faz a conexão
    def connect(self):
        check, reason = self.iqoption.connect()
        return check

    # desconecta a API
    def disconnect(self):
        self.iqoption.api.close()

    # Verifica o Balanço
    def get_balance_type(self):
        balance_mode = self.iqoption.get_balance_mode()

        if balance_mode == "REAL":
            return "Conta Real"
        elif balance_mode == "PRACTICE":
            return "Conta Demo"
        else:
            return "Tipo de conta desconhecido"

    # Retorna todos ativos digitais abertos incluindo OTC
    def get_open_assets(self, include_otc=False):
        open_assets = []

        all_assets = self.iqoption.get_all_open_time()
        asset_types = ["digital", "binary"]

        if include_otc:
            asset_types.extend(["turbo"])

        for asset_type in asset_types:
            if asset_type in all_assets:
                for asset, data in all_assets[asset_type].items():
                    if data["open"]:
                        open_assets.append(asset)

        return open_assets

    def is_asset_open(self, asset):
        open_time = self.iqoption.get_all_open_time()
        if "binary" not in open_time:
            # Tratamento de erro: a chave 'binary' não está presente no dicionário
            return False
        assets = open_time["binary"]["actives"]
        for a in assets:
            if a["alias"] == asset:
                return a["open"]
        return False


    # Realiza operação de compra ou de venda opções digitais
    def fn_buy_or_sell(self, id, actives, duration):
        #_,id=(self.iqoption.buy_digital_spot(actives, amount, action,duration))

        if id !="error":
            print('Operação realizada! Aguarde ...')
            
            while True:
                check,win=self.iqoption.check_win_digital_v2(id)
                self.iqoption.subscribe_strike_list(actives,duration)

                if check==True:
                    self.iqoption.stop_candles_stream(actives, 60)
                    break

            if win<0:
                result = "you loss "+str(win)+"$"
            else:
                result = "you win "+str(win)+"$"
        else:
            result = "please try again"

        return result

  
    def fn_get_closed_candles(self, asset, interval, n_candles):
        candles = self.iqoption.get_candles(asset, interval, n_candles, time.time())
       
        if not candles:
            return []

        # Inclua todos os valores dos candles (open, max, min, close)
        candles_data = [(candle["open"], candle["max"], candle["min"], candle["close"]) for candle in candles]
        return candles_data

    def buy_digital_spot(self, asset, amount, action, duration):
                
       # check, buy_order_id = self.iqoption.buy_digital_spot(asset, amount, action, duration)    
        _, execute_id = self.iqoption.buy_digital_spot(asset, amount, action, duration)
        if execute_id !="error":
            print('Operação realizada! Aguarde ...')
            
            while True:
                check,win=self.iqoption.check_win_digital_v2(id)
                self.iqoption.subscribe_strike_list(asset,duration)

                if check==True:
                    self.iqoption.stop_candles_stream(asset, 60)
                    break

            if win<0:
                result = "you loss "+str(win)+"$"
            else:
                result = "you win "+str(win)+"$"
        else:
            result = "please try again"




        time.sleep(1)
        self.iqoption.subscribe_strike_list(asset, duration)
        time.sleep(1)
        result = self.wait_for_operation_result(execute_id)
        print(result)
        
        try:
            self.iqoption.unsubscribe_strike_list(asset, duration)
        except Exception as e:
            print(f"Erro ao tentar desinscrever a lista de ativos: {e}")
        return result 
        


    def wait_for_operation_result(self, execute_id):
        while True:
            order_info = self.iqoption.get_async_order(tuple(execute_id.items()))
            if order_info["position-changed"]:
                check, win = self.iqoption.check_win_digital_v2(execute_id)
                if check:
                    if win > 0:
                        result = "Você ganhou: " + str(win) + "$"
                    else:
                        result = "Você perdeu: " + str(win) + "$"
                    return result
            time.sleep(1)


    def get_market_trend(self, high_prices, low_prices, close_prices, time_period=14, rsi_threshold=50):
        rsi = talib.RSI(close_prices, timeperiod=time_period)
        latest_rsi = rsi[-1]

        if latest_rsi > rsi_threshold:
            plus_di = talib.PLUS_DI(high_prices, low_prices, close_prices, time_period)
            minus_di = talib.MINUS_DI(high_prices, low_prices, close_prices, time_period)

            if plus_di[-1] > minus_di[-1]:
                return "uptrend"
            else:
                return "downtrend"
        else:
            return "no trend"
    # Retorna as velas para um ativo em um intervalo de tempo
    def get_candles(self, asset, interval, count, endtime):
        candles = self.iqoption.get_candles(asset, int(interval), count, endtime)
        candles_df = pd.DataFrame(candles, columns=["id", "from", "at", "to", "open", "close", "min", "max", "volume"])
        candles_df.set_index("id", inplace=True)
        candles_df.index = pd.to_datetime(candles_df.index, unit="s")
        return candles_df

