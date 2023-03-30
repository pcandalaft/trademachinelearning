from iqoption_connector import IQOptionConnector

iq_option = IQOptionConnector("xxx", "xxx")
iq_option.connect()


# Definir os parâmetros da função
asset = "EURUSD-OTC"              # Ativo que você deseja analisar
interval = 60                 # Intervalo de tempo em segundos para os candles (1 minuto)
amount = 1                    # Montante que você deseja investir em cada operação
monitoring_duration = 3600    # Duração do monitoramento em segundos (1 hora)
time_frame = 14               # Período para o cálculo do indicador stochastic (valor padrão 14)

# Chamar a função analyze_stochastic_and_candles
iq_option.analyze_stochastic_and_candles(asset, interval, amount, monitoring_duration, time_frame)

# Desconectar da plataforma IQ Option
iq_option.disconnect()



