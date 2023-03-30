from iqoptionapi.stable_api import IQ_Option
import talib, time

class ApiIqOptConnector:
    def __init__(self, email, password):
        self.iqoption = IQ_Option(email, password)

    def connect(self):
        check, reason = self.iqoption.connect()
        return check

    def disconnect(self):
        self.iqoption.api.close()

    def get_version(self):
        return IQ_Option.__version__

    def get_balance_type(self):
        balance_mode = self.iqoption.get_balance_mode()
        return "Conta Real" if balance_mode == "REAL" else "Conta Demo" if balance_mode == "PRACTICE" else "Tipo de conta desconhecido"

    def get_open_assets(self, include_otc=False):
        all_assets = self.iqoption.get_all_open_time()
        asset_types = ["digital", "binary"]
        if include_otc:
            asset_types.extend(["turbo"])

        return [asset for asset_type in asset_types if asset_type in all_assets for asset, data in all_assets[asset_type].items() if data["open"]]

    def set_session(self):
        header = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0"}
        cookie = {"Iq": "GOOD"}
        self.iqoption.set_session(header, cookie)
        return True

    def get_balance(self):
        return self.iqoption.get_balance()

    def change_balance(self, mode):
        self.iqoption.change_balance(mode)

    def get_live_deal(self, name, active, _type):
        return self.iqoption.get_live_deal(name, active, _type)

    def subscribe_live_deal(self, name, active, _type, buffersize):
        self.iqoption.subscribe_live_deal(name, active, _type, buffersize)

    def unscribe_live_deal(self, name, active, _type):
        self.iqoption.unscribe_live_deal(name, active, _type)

    def reset_practice_balance(self):
        self.iqoption.reset_practice_balance()

    def get_currency(self):
        return self.iqoption.get_currency()

    def get_all_ACTIVES_OPCODE(self):
        return self.iqoption.get_all_ACTIVES_OPCODE()

    def get_digital_current_profit(self, active, duration):
        return self.iqoption.get_digital_current_profit(active, duration)

    def is_asset_open(self, asset, asset_type="digital"):
        open_time = self.iqoption.get_all_open_time()
        asset_data = open_time.get(asset_type, {}).get(asset, {})
        return asset_data.get("open", False)

    def start_candles_stream (self, active, size):
        self.start_candles_stream(active, size)
        
    # buy digital
    def buy_digital_spot(self, amount,actives,action,duration, size):
        check,id=self.iqoption.buy_digital_spot(actives, amount, action, duration)
        
        if check:
            if id !="error":
               print('Operação realizada! Aguarde ...')
               while True:
                self.iqoption.start_candles_stream(actives, size, 10)
                check_win,win=self.iqoption.check_win_digital_v2(id)
                self.iqoption.subscribe_strike_list(actives, duration)  
                #PL=self.iqoption.get_digital_spot_profit_after_sale(id)

                # if(PL > (amount/100 * 15)):
                #     print(PL)
                #     self.iqoption.close_digital_option(id)
               
                # print(self.iqoption.get_remaning(duration)-25)                  
                      
                if check_win==True:
                    self.iqoption.unsubscribe_strike_list(actives, duration)
                    self.iqoption.stop_candles_stream(actives, size)
                    break

                return win, id                

        else:            
            return 0, None
    
    def get_digital_current_profit(self, actives, duration, amount):
        self.iqoption.subscribe_strike_list(actives, duration)
        profit = round((self.iqoption.get_digital_current_profit(actives, duration)),2)
        while profit == 0:
            profit = round((self.iqoption.get_digital_current_profit(actives, duration)),2)       
        self.iqoption.unsubscribe_strike_list(actives, duration)
        result = amount + (amount - (amount * (profit/100)))
        print("profit ->" + str(profit))
        return round(result)
    
    def get_next_amount(self, actives, duration, amount):
        profit = round((self.iqoption.get_digital_current_profit(actives, duration)),2)
        
        aposta = round((1 - (profit/100)) ,2)
        return aposta


    def get_profit(self, actives):
        d=self.iqoption.get_all_profit()
        return (d[actives]["turbo"])

    def fn_get_closed_candles(self, asset, interval, n_candles):
        self.iqoption.connect()
        candles = self.iqoption.get_candles(asset, interval, n_candles, time.time())
        print("verificando o historico...")
        if not candles:
            return []

        # Inclua todos os valores dos candles (open, max, min, close)
        candles_data = [(candle["open"], candle["max"], candle["min"], candle["close"]) for candle in candles]
        return candles_data
    
    def is_asset_open(self, asset, asset_type="digital"):
        open_time = self.iqoption.get_all_open_time()
        asset_data = open_time.get(asset_type, {}).get(asset, {})
        return asset_data.get("open", False)
    
    def wait_for_operation_result(self, execute_id):
        while True:
            check, win = self.iqoption.check_win_digital_v2(execute_id)
            if check:
                if win > 0:
                    result = win
                else:
                    result = win
                return result
            time.sleep(1)


