import backtrader as bt
import random
import pandas as pd
from datetime import datetime, timedelta

class MyStrategy(bt.Strategy):
    
    def __init__(self):
        self.hammer_detected = False
        self.evening_star_detected = False
        
    def next(self):
        # Detectar padrão de martelo
        if not self.hammer_detected and self.data.close[-1] < self.data.open[-1] and \
        self.data.open[-1] > self.data.low[-1] + (self.data.high[-1] - self.data.low[-1]) * 0.6 and \
        self.data.close[-1] > self.data.high[-1] - (self.data.high[-1] - self.data.low[-1]) * 0.4:
            self.hammer_detected = True
            self.sell()
            
        # Detectar padrão de estrela da noite
        if not self.evening_star_detected and self.data.close[-1] < self.data.open[-1] and \
        self.data.close[-2] < self.data.open[-2] and \
        self.data.close[-1] < self.data.close[-2] and self.data.open[-1] < self.data.open[-2] and \
        self.data.open[-1] > self.data.close[-2] and self.data.close[-1] < self.data.open[-2] and \
        self.data.close[-1] < self.data.low[-1] + (self.data.high[-1] - self.data.low[-1]) * 0.2:
            self.evening_star_detected = True
            self.sell()
    
    def buy(self):
        print("Sinal de compra!")
        
    def sell(self):
        print("Sinal de venda!")

# Gerar dados aleatórios com padrões de candlestick
prices = [
    [datetime.now() - timedelta(days=i), random.randint(1, 100), random.randint(1, 100), random.randint(1, 100), random.randint(1, 100)]
    for i in range(100)
]

# Converter lista de preços em DataFrame do pandas
df = pd.DataFrame(prices, columns=["date", "open", "high", "low", "close"])
df.set_index("date", inplace=True)

# Criar feed de dados
data = bt.feeds.PandasData(dataname=df)

# Criar cerebro
cerebro = bt.Cerebro()

# Adicionar feed de dados
cerebro.adddata(data)

# Adicionar estratégia
cerebro.addstrategy(MyStrategy)

# Rodar o backtest
cerebro.run()
