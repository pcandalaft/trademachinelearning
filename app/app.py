from library.IqApiConnector import ApiIqOptConnector
from library.brain import IWantGetMoney
import time
import pandas as pd
from datetime import datetime, timedelta

def get_closed_candles(api, asset, interval, n, duration_in_seconds):
    current_timestamp = int(time.time())
    adjusted_timestamp = current_timestamp - duration_in_seconds
    all_candles = api.fn_get_closed_candles(asset, interval, n + 1)

    closed_candles = []
    for candle in all_candles:
        if candle[0] < adjusted_timestamp:  # Ajustar aqui
            closed_candles.append(candle)

    return closed_candles[:n]





def main():

    brain = IWantGetMoney
    email = "xxx"
    password = "xxx"
    asset = "EURUSD"   
    duration = 1
    size = 60     
    amount = 2
    amount_original = amount
    n_candles = 2000    

    api = ApiIqOptConnector(email, password)
    api.connect() # Conectando na API

    if True:   
        # Aqui podemos alternar entre "PRACTICE"/"REAL"
        # api.change_balance("REAL") 

        versao = api.get_version()
        tipo_conta = api.get_balance_type() # Tipo de conta  
        saldo = api.get_balance()

        header =          "_____________IQ Option "+ versao +"________________\n\n"
        header = header + "    Você esta conectado em uma " + tipo_conta + ".\n"
        header = header + "    Seu saldo atual é de " + api.get_currency() + ": " + str(saldo) + "\n"
        header = header + "    A moeda selecionada é " + asset + "\n"
        header = header + "______________________________________________\n"  
        print (header)
      
        candles = api.fn_get_closed_candles(asset, duration, n_candles)
        candles_df = pd.DataFrame(candles, columns=["open", "max", "min", "close"])
        candles_df = brain.add_candlestick_patterns(candles_df)        
        algorithms = ["XGBoost","RandomForest" ,  "NeuralNetwork" ]
        best_accuracy = 0
        best_algorithm = None
        best_model = None

        for algorithm in algorithms:
            model, accuracy = brain.train_predictor(candles_df, algorithm)
            print(f"Acurácia do modelo ({algorithm}): {accuracy}")

            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_algorithm = algorithm
                best_model = model

            print(f"Melhor algoritmo: {best_algorithm} com acurácia: {best_accuracy}")

            monitoring_duration = 8 * 60 * 60  # 2 hours in seconds
            start_time = datetime.now()
            end_time = start_time + timedelta(seconds=monitoring_duration)

            print("verificando o historico...")
            
            duration_in_seconds = duration * 60  # Assumes duration is in minutes
            last_candle_timestamp = 0

    while datetime.now() < end_time:
        current_timestamp = int(time.time())
        adjusted_timestamp = current_timestamp - duration_in_seconds
        last_candles = get_closed_candles(api, asset, duration, 38, duration_in_seconds)

        # Verificar se há um novo candle fechado
        if last_candles and last_candles[0][0] > last_candle_timestamp:
            last_candle_timestamp = last_candles[0][0]
            last_candles_df = pd.DataFrame(last_candles, columns=["open", "max", "min", "close"])
            last_candles_df = brain.add_candlestick_patterns(last_candles_df)

        last_candle = brain.prepare_features(last_candles_df).iloc[-1].values.reshape(1, -1)
        prediction = best_model.predict(last_candle)

        print(f"Prediction: {prediction[0]}")

        if prediction[0] == 1:
            action = "call"
            pattern = "Compra"
        elif prediction[0] == 0:
            action = "put"
            pattern = "Venda"
        else:
            continue

        if api.is_asset_open(asset):
            print(f"{pattern}: {action.capitalize()}")
            print("Valor do investimento:" + str(amount))
            time.sleep(1)
            result = api.buy_digital_spot(amount, asset, action, duration, size)
            print("Result: " + str(result))
            if result < 0:
                amount = amount * 2
            elif result > 0:
                amount = amount_original

        else:
            print("O ativo não está aberto para negociação no momento")

        time.sleep(duration)


        api.disconnect()

if __name__ == "__main__":
    main()