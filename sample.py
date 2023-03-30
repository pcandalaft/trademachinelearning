from iqoption_connector import IQOptionConnector
import time
import random


I_want_money = IQOptionConnector("xxx", "xxx")
I_want_money.connect() #connect to iqoption

ACTIVES = "EURUSD-OTC"

duration=1#minute 1 or 5
amount=20
action="put"#call
interval = 60
expiration_time = int(time.time()) + duration * 60
#execute = I_want_money.fn_buy_or_sell("EURUSD-OTC", 20, 'call', 1)
#execute = I_want_money.buy_digital_spot("EURUSD-OTC", 20, 'call', 1)
#execute = I_want_money.fn_buy_or_sell(ACTIVES,amount, action, duration)
execute =I_want_money.buy_digital_spot( "EURUSD-OTC", 1, "put", duration)

print (execute)