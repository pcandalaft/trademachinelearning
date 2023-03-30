from iqoption_connector import IQOptionConnector
from config import IQOPTION_EMAIL, IQOPTION_PASSWORD

def main():
    iqoption = IQOptionConnector(IQOPTION_EMAIL, IQOPTION_PASSWORD)
    check = iqoption.connect()

    if check:
        print("Conexão bem-sucedida!")
        account_type = iqoption.get_balance_type()
        print(f"Você está usando: {account_type}")

        open_assets = iqoption.get_open_assets(include_otc=False)
        print("Ativos abertos (incluindo OTC):", open_assets)

        # Parâmetros da compra
        asset_to_buy = "EURUSD"
        amount_to_buy = 1
        duration_to_buy = 1
        direction_to_buy = "call"

        # Compra de opção digital
        check, order_id = iqoption.buy_digital_option(asset_to_buy, amount_to_buy, duration_to_buy, direction_to_buy)
        if check:
            print(f"Ordem bem-sucedida! ID da ordem: {order_id}")
        else:
            print("Erro ao comprar opção digital")

        iqoption.disconnect()
    else:
        print("Falha na conexão")
