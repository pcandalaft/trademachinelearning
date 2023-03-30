from iqoptionapi.stable_api import IQ_Option
import  time, locale 
import talib
import numpy as np
import pandas as pd


locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')
locale.setlocale(locale.LC_MONETARY, 'pt_BR.UTF-8')

class IQOptionConnector:
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

    def is_asset_open(self, asset, asset_type="digital"):
        open_time = self.iqoption.get_all_open_time()
        asset_data = open_time.get(asset_type, {}).get(asset, {})
        return asset_data.get("open", False)

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

    def analyze_candles(self, amount, asset, interval, monitoring_duration, historic_candles_count=100):
        # Carregar candles históricos
        historic_candles = self.fn_get_closed_candles(asset, interval, historic_candles_count)

        # Separar os valores de abertura, máximo, mínimo e fechamento em arrays numpy
        open_prices, high_prices, low_prices, close_prices = map(np.array, zip(*historic_candles))

        # Iniciar a monitoração
        monitoring_start_time = time.time()
        last_candle_id = None
        # Verificar a tendência do mercado
        market_trend = self.get_market_trend(np.array(high_prices), np.array(low_prices), np.array(close_prices))

        # Iniciar transmissão de candles em tempo real
        self.iqoption.start_candles_stream(asset, interval, 1)

        

        # Funções problemáticas da TA-Lib que esperam um número incorreto de argumentos
       # problematic_functions = ["CDLBREAKAWAY","CDLBELTHOLD","CDLADVANCEBLOCK","CDLABANDONEDBABY","CDL3STARSINSOUTH","CDL3OUTSIDE","CDL3LINESTRIKE","CDL2CROWS", "CDL3BLACKCROWS", "CDL3WHITESOLDIERS", "CDL3INSIDE"]
        problematic_functions = []
        while time.time() - monitoring_start_time < monitoring_duration:
            # ...
            # Restante do código do loop while
            # ...
            patterns = talib.get_function_groups()["Pattern Recognition"]
           
            for pattern in patterns:
                if pattern in problematic_functions:
                    continue  # Ignorar funções problemáticas
                pattern_function = getattr(talib, pattern)
                pattern_result = pattern_function(open_prices, high_prices, low_prices, close_prices)

                # Verificar se há sinal de compra ou venda
                if pattern_result[-1] > 0 and market_trend == "uptrend":                            
                    print(f"{pattern}: Compra")
                    time.sleep(1)  # Adicione esta linha
                    _, execute_id = self.iqoption.buy_digital_spot(asset, amount, 'call', 1)
                    self.iqoption.subscribe_strike_list(asset, interval)
                    result = self.wait_for_operation_result(execute_id)
                    print(result)
                    try:
                        self.iqoption.unsubscribe_strike_list(asset, interval)
                    except Exception as e:
                        print(f"Erro ao tentar desinscrever a lista de ativos: {e}")
                elif pattern_result[-1] < 0 and market_trend == "downtrend":
                    print(f"{pattern}: Venda")
                    time.sleep(1)  # Adicione esta linha
                    _, execute_id = self.iqoption.buy_digital_spot(asset, amount, 'put', 1)
                    self.iqoption.subscribe_strike_list(asset, interval)
                    result = self.wait_for_operation_result(execute_id)
                    print(result)
                    try:
                        self.iqoption.unsubscribe_strike_list(asset, interval)
                    except Exception as e:
                        print(f"Erro ao tentar desinscrever a lista de ativos: {e}")                    
                        # else:
                        #     print(f"{pattern}: Sem padrões identificados")

                    # Remover os últimos preços de abertura, máximo, mínimo e fechamento para analisar o próximo candle
                    open_prices = np.delete(open_prices, -1)
                    high_prices = np.delete(high_prices, -1)
                    low_prices = np.delete(low_prices, -1)
                    close_prices = np.delete(close_prices, -1)

            # Adicionar uma pausa entre as iterações para reduzir o uso da CPU
            time.sleep(1)

        # Parar a transmissão de candles em tempo real
        self.iqoption.stop_candles_stream(asset, interval)


    def fn_get_closed_candles(self, asset, interval, n_candles):
        candles = self.iqoption.get_candles(asset, interval, n_candles, time.time())
        print("verificando o historico...")
        if not candles:
            return []

        # Inclua todos os valores dos candles (open, max, min, close)
        candles_data = [(candle["open"], candle["max"], candle["min"], candle["close"]) for candle in candles]
        return candles_data

    def buy_digital_spot(self, asset, amount, action, duration):
        expiration_time = int(time.time()) + duration * 60
        
        check, buy_order_id = self.iqoption.buy_digital_spot(asset, amount, action, expiration_time)
        print(buy_order_id)
        if check:
            print(f"Compra realizada com o ID: {buy_order_id}")
            time.sleep(1)
            check, win = self.iqoption.check_win_digital_v2(buy_order_id)
            if check:
                return round(win, 2)
        #else:
       #     print("Operação não realizada.")

    def wait_for_operation_result(self, execute_id):
        while True:
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

