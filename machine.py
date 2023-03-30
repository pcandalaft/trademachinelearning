import talib
from iqoptionapi.stable_api import IQ_Option
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from iqConnector import IQConnector
from sklearn.model_selection import TimeSeriesSplit
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier

import pandas as pd
import time
from datetime import datetime, timedelta

email = "xxx"
password = "xxx"

def add_candlestick_patterns(candles_df):
    candles_df["ENGULFING"] = talib.CDLENGULFING(candles_df["open"], candles_df["max"], candles_df["min"], candles_df["close"])
    candles_df["HAMMER"] = talib.CDLHAMMER(candles_df["open"], candles_df["max"], candles_df["min"], candles_df["close"])
    candles_df["SHOOTING_STAR"] = talib.CDLSHOOTINGSTAR(candles_df["open"], candles_df["max"], candles_df["min"], candles_df["close"])
    candles_df["MORNING_STAR"] = talib.CDLMORNINGSTAR(candles_df["open"], candles_df["max"], candles_df["min"], candles_df["close"])
    candles_df["EVENING_STAR"] = talib.CDLEVENINGSTAR(candles_df["open"], candles_df["max"], candles_df["min"], candles_df["close"])
    return candles_df

def prepare_features(candles_df):
    features = candles_df[["open", "max", "min", "close", "ENGULFING", "HAMMER", "SHOOTING_STAR", "MORNING_STAR", "EVENING_STAR"]]
    return features


def train_predictor(candles_df, algorithm):
    features = candles_df[["open", "max", "min", "close", "ENGULFING", "HAMMER", "SHOOTING_STAR", "MORNING_STAR", "EVENING_STAR"]]
    target = (candles_df["close"].diff().shift(-1) > 0).astype(int)

    features_array = features.to_numpy()

    X_train, X_test, y_train, y_test = train_test_split(features_array, target, test_size=0.2, shuffle=False)

    if algorithm == "RandomForest":
        param_grid = {
            'n_estimators': [10, 50, 100, 200],
            'max_depth': [None, 10, 20, 30],
            'min_samples_split': [2, 5, 10]
        }
        model = RandomForestClassifier()
    elif algorithm == "NeuralNetwork":
        param_grid = {
            'hidden_layer_sizes': [(50, 50), (100,)],
            'activation': ['tanh', 'relu'],
            'solver': ['sgd', 'adam'],
            'alpha': [0.0001, 0.05],
            'learning_rate': ['constant', 'adaptive']
        }
        model = MLPClassifier()
    elif algorithm == "SVM":
        param_grid = {
            'C': [0.1, 1, 10, 100],
            'gamma': ['scale', 'auto', 0.1, 1, 10],
            'kernel': ['linear', 'rbf']
        }
        model = SVC()
    elif algorithm == "XGBoost":
        param_grid = {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.1, 0.2],
            'max_depth': [3, 6, 9],
            'subsample': [0.5, 0.75, 1],
            'colsample_bytree': [0.5, 0.75, 1]
        }
        model = XGBClassifier(eval_metric='logloss')  # Remova o parâmetro use_label_encoder
    else:
        raise ValueError("Algoritmo não suportado")

    tscv = TimeSeriesSplit(n_splits=5)
    grid_search = GridSearchCV(model, param_grid, cv=tscv, scoring='accuracy', n_jobs=-1)
    grid_search.fit(X_train, y_train)

    best_model = grid_search.best_estimator_
    y_pred = best_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    return best_model, accuracy

def main():
    email = "xxx"
    password = "xxx"
    api = IQConnector(email, password)
    
    if not api.connect():
        print("Erro ao conectar")
        return

    asset = "EURUSD"
    interval = 30
    n_candles = 2000

    candles = api.fn_get_closed_candles(asset, interval, n_candles)
    candles_df = pd.DataFrame(candles, columns=["open", "max", "min", "close"])
    candles_df = add_candlestick_patterns(candles_df)

    algorithms = ["RandomForest","NeuralNetwork"]
    #algorithms = ["RandomForest", "NeuralNetwork", "SVM", "XGBoost"]
    best_accuracy = 0
    best_algorithm = None
    best_model = None

    for algorithm in algorithms:
        model, accuracy = train_predictor(candles_df, algorithm)
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
    
    while datetime.now() < end_time:
        last_candles = api.fn_get_closed_candles(asset, interval, 38)  # Get the last 16 candles
        last_candles_df = pd.DataFrame(last_candles, columns=["open", "max", "min", "close"])
        last_candles_df = add_candlestick_patterns(last_candles_df)

        last_candle = prepare_features(last_candles_df).iloc[-1].values.reshape(1, -1)
        prediction = best_model.predict(last_candle)

        if prediction[0] == 1:
            action = "call"
            pattern = "Compra"
        elif prediction[0] == 0:
            action = "put"
            pattern = "Venda"
        else:
            continue

        print (action + " : " + pattern)

        amount = 18
        duration = 1

        if api.is_asset_open(asset):
            print(f"{pattern}: {action.capitalize()}")
            time.sleep(1)
            execute_id = api.buy_digital_spot(asset, amount, action, duration)

        else:
            print("O ativo não está aberto para negociação no momento")

        time.sleep(interval)
        if api.is_asset_open(asset):
            print(f"{pattern}: {action.capitalize()}")
        time.sleep(1)

        try:
            execute_id = api.buy_digital_spot(asset, amount, action, duration)
            

        except TypeError:
            print("Ocorreu um erro ao tentar executar a operação. Tentando novamente...")
            continue

    api.disconnect()

if __name__ == "__main__":
    main()




