import PySimpleGUI as sg
from api_connector import ApiConnector
from form_default_win import IqDefault

# Debug mode on¶
# import logging
# logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s')

layout = [[sg.Text('Email:'), sg.InputText(default_text='xxx')],
          [sg.Text('Senha:'), sg.InputText(password_char='*', default_text='xxx')],
          [sg.Text('Tipo de conta:'), sg.Combo(['Conta Demo', 'Conta Real'], key='-TIPO_CONTA-', default_value='Conta Demo')],
          [sg.Button('Login')]]

window = sg.Window('Login', layout)

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    elif event == 'Login':
        email = values[0]
        password = values[1]
        tipo_conta = values['-TIPO_CONTA-']
        if not tipo_conta:
            sg.popup('Selecione o tipo de conta')
            continue
        api = ApiConnector(email, password)
        connected = api.connect()
        if connected:
            api.altera_conta('PRACTICE' if tipo_conta == 'Conta Demo' else 'REAL')
            saldo = api.saldo_total()
            window.hide() 
            # Abre a tela principal
            IqDefault.default_window(api, tipo_conta, saldo)                 
        else:
            sg.popup('Falha na conexão. Verifique seu email e senha.')
        window.close()
