from api_connector import ApiConnector
from iqoption_connector import IQOptionConnector

from config import IQOPTION_EMAIL, IQOPTION_PASSWORD
import json, pprint

# Efetuar conexão
def app():
    iq = ApiConnector(IQOPTION_EMAIL, IQOPTION_PASSWORD)
    check = iq.connect()

    ic = IQOptionConnector(IQOPTION_EMAIL, IQOPTION_PASSWORD)
    ic.connect()

    if check:
        print("Conexão bem sucedida!")

        # Essa linha altera a conta onde você pode selecionar "PRATICE" ou "REAL"
        iq.altera_conta('REAL')
        # Armazena o tipo de conta atual
        account_type = iq.get_balance_type() 
        saldo = iq.saldo_total()      
        print (saldo)
        # imprime o tipo de conta conectada
        if check:
            print(f'Você esta usando a conta {account_type} ')
        else:
            print(f'Sei la, deu merda para selecionar a conta!')
        duration = 1 #minute 1 or 5
        amount = 50
        action = "call" #put
        active = "EURUSD"
        
        #Efetua uma compra
        print('Efetuando compra')
        ic.fn_buy_or_sell(active, duration, amount, action)

        # PEGANDO PARIDADES ABERTAS E PAYOUT
        
        # abertos, par = iq.get_open_assets(False)

        # for paridade in par['turbo']:
        #     if par['turbo'][paridade]['open'] == True:
        #         print('[ TURBO ]: '+paridade+' | Payout: '+str(iq.payout(paridade, 'turbo')))
        # print('\n')

        # for paridade in par['digital']:
        #     if par['digital'][paridade]['open'] == True:
        #         print('[ DIGITAL ]: '+paridade+' | Payout: '+str( iq.payout(paridade, 'digital') ))

        
        # Retorna os dados do usuario
       #  perfil = iq.perfil()
        # pprint.pprint(perfil)
        # data = json.loads(str(perfil))
        # iq.get_candle('EURUSD')

        # Velas em tempo real
        # iq.realtime_candles('EURUSD-OTC')
        # open_assets = iq.get_open_assets(include_otc=False)
        # print("Ativos abertos (incluindo OTC):", open_assets)

        # print(data.get('balance'))




    else:
        print("Falha na conexão!")

    iq.disconnect()

app()