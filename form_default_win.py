import PySimpleGUI as sg
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')
locale.setlocale(locale.LC_MONETARY, 'pt_BR.UTF-8')


class IqDefault:
    def default_window(api, tipo_conta, saldo):
        perfil = api.perfil() # Obtém os dados do usuário
        # Define as opções da combobox
        opcoes_ativos = ['EURGBP', 'EURUSD', 'EURJPY']

        # Monta campos da tela principal
        layout = [
            [sg.Text(f'Olá, {perfil["name"]}!', font='Helvetica 16 bold', text_color='#1c1c1c', justification='center', pad=((0,0),(10,0)))],
            [sg.Text(f'Tipo de conta: {tipo_conta}')],
            [sg.Text(f'Saldo em Conta: {locale.currency(float(saldo), grouping=True)}', key='-SALDO-')],
            [sg.Text('Ativo:'), sg.Combo(values=opcoes_ativos, default_value=opcoes_ativos[0], key='-ATIVO-')],

            [sg.Button('Desconectar')]
        ]

        tela = sg.Window('Dados do IQ Option', layout, finalize=True, size=(800,600))

        tela.UnHide() 
        while True:
            event, values = tela.read()
            if event == sg.WINDOW_CLOSED or event == 'Desconectar':
                api.disconnect()  # desconecta da API antes de fechar a janela
                tela.close()
                sg.Popup('Desconectado com sucesso!', title='Desconexão')
                import form_login
                form_login.start() # Abre a tela de login novamente
                break

        tela.close()
