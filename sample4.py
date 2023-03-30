from iqoption_connector import IQOptionConnector
import time

connector  = IQOptionConnector("xxxx", "xxxx")
connector .connect() #connect to iqoption

ACTIVES = "EURUSD-OTC"
asset = "EURUSD-OTC"
interval = 15
amount = 28.02
monitoring_duration = 3600
historic_candles_count = 10 

# monitoramento de candles
connector.analyze_candles(amount, asset, interval, monitoring_duration, historic_candles_count=25)
