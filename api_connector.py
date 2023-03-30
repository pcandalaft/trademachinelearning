from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
import time, json
from dateutil import tz

print(IQ_Option.__version__)

class ApiConnector:
    # Conexão com a API
    def __init__(self, email, pasword):
        self.iqoption = IQ_Option(email, pasword)

    # Conectar
    def connect(self):
       I_want_money = self.iqoption
       check = self.iqoption.connect()
       print(self.iqoption.check_connect())
       print(self.iqoption.get_server_timestamp())
       print(self.iqoption.get_balance())
       print(self.iqoption.get_currency())
       
       # print(self.iqoption.reset_practice_balance())
       return check
    
    # desconecta a API
    def disconnect(self):
        self.iqoption.api.close()
        print(self.iqoption.check_connect())
        

    # Change account type
    def altera_conta(self,tipo_conta):
        self.iqoption.change_balance(tipo_conta)

    # Esta função identifica em qual tipo de conta eu estou conectado
    def get_balance_type(self):
        balance_mode = self.iqoption.get_balance_mode()

        if balance_mode == "REAL":
            return "Conta Real"
        elif balance_mode == "PRACTICE":
            return "Conta Demo"
        else:
            return "Conta Demo"

    # Vamos trazer os dados básicos do usuário
    def perfil(self):
        perfil = json.loads(json.dumps(self.iqoption.get_profile_ansyc()))

        return perfil
    # Retorna o saldo total
    def saldo_total(self):
        saldo = self.iqoption.get_balance()
        return saldo

    # Converte data e hora
    def timestamp_converter(x):
        hora = datetime.strptime(datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        hora = hora.replace(tzinfo=tz.gettz('GMT'))	
        return str(hora.astimezone(tz.gettz('America/Sao Paulo')))

    # trazer até 1000 velas
    def get_candle(self, par):
        vela = self.iqoption.get_candles(par, 60, 10, time.time())
        for velas in vela:
            print(str(velas['from'])+'  - abertura: '+str(velas['open']))
            #print('Hora inicio: '+str(self.timestamp_converter(velas['from']))+' abertura: '+str(velas['open']))
    
    def realtime_candles(self, par):
        API = self.iqoption
        API.start_candles_stream(par, 60, 1)
        time.sleep(1)

        while True:
            vela = API.get_realtime_candles(par, 60)
            for velas in vela:
                print(vela[velas]['close'])
            time.sleep(1)
            API.stop_candles_stream(par, 60)

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

        return open_assets, all_assets                
    
    # Verifica mercados abertos
    def is_asset_open(self, asset, asset_type="digital"):
        open_time = self.iqoption.get_all_open_time()
        asset_data = open_time.get(asset_type, {}).get(asset, {})
        return asset_data.get("open", False)
    
    def payout(self, par, tipo, timeframe = 1):
        API= self.iqoption
        if tipo == 'turbo':
            a = API.get_all_profit()
            return int(100 * a[par]['turbo'])
            
        elif tipo == 'digital':
        
            API.subscribe_strike_list(par, timeframe)
            while True:
                d = API.get_digital_current_profit(par, timeframe)
                if d != False:
                    d = int(d)
                    break
                time.sleep(1)
            API.unsubscribe_strike_list(par, timeframe)
            return d