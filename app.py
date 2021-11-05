import streamlit as st
import sqlite3
import pandas as pd
from binance import Client
from binance.exceptions import BinanceAPIException
import matplotlib.pyplot as plt

from modules import get_minutedata



# funcoes para o banco de dados 
conn = sqlite3.connect('data.db')
c = conn.cursor()
def create_usertable(): 
    """
    Funcao para criar o banco de dados para logins/senhas
    """
    c.execute('CREATE TABLE IF NOT EXISTS usertable(username TEXT, password TEXT)')

    return
def add_userdata(username: str = '', password: str=''): 
    """
    Funcao que adiciona um usuario novo ao banco de dados
    """
    try: 
        c.execute('INSERT INTO usertable(username, password) VALUES (?,?)', (username, password))
        conn.commit()
        return 0
    except: 
        return None
def login_user(username: str = '', password: str =''):
    """
    Funcao que faz o login do usuario
    """
    c.execute('SELECT * FROM usertable WHERE username=? AND password = ?', (username, password))
    data = c.fetchall()
    return data
def view_all_users():
    """
    Funcao que mostra todos os usuarios inscritos no banco de dados
    """
    c.execute('SELECT * FROM usertable')
    data = c.fetchall()
    return data 
#------------------------------------------------------------------------------



def main():
    """
    Funcao principal do app
    """
    st.title('BOT_Binance')
    menu = ['Página Inicial', 'Login', 'Sobre']

    aba = st.sidebar.selectbox('Menu', menu)

    if aba == 'Login':
        st.subheader('Login Page')
        
        username = st.sidebar.text_input('User')
        password = st.sidebar.text_input('Password', type='password')

        if st.sidebar.checkbox('Login'):
            #create_usertable()

            #result = login_user(username = username, password = password)
            #if result:
            st.success(f'Logged In as {username}')

            st.sidebar.text('Informações API Binance:')
            key = st.sidebar.text_input('Key - API', type='password')
            secret_key = st.sidebar.text_input('Secret Key - API', type='password')

            task = st.selectbox('Page', ['Binance Info', 'BOT', 'Histórico'])

            if task == 'Binance Info':
                st.subheader('Informaçoes da Binance')


                if key != '' and secret_key != '':
                    client = Client(api_key=key, api_secret=secret_key)

                    coins_dict = {'TICKER':[], 'QNT':[]}
                    coins_dict_for_price = {}
                    for cur in client.get_account()['balances']:
                        if float(cur['free']) > 0:
                            coins_dict['TICKER'].append(cur['asset'])
                            coins_dict['QNT'].append(cur['free'])
                            coins_dict_for_price[cur['asset']]=cur['free']

                    for corr in client.get_all_tickers():
                        new_ticker = corr['symbol'].replace('BUSD', '')
                        if new_ticker in coins_dict['TICKER']:
                            val = round(float(coins_dict_for_price[new_ticker])*float(corr['price']),2) # valor em USD

                            """
                            FALTA LINKAR MOEDAS COM VALORES DO OUTRO DF, MULTIPLICAR E CRIAR NOVA COLUNA
                            """



                        
                    
                    coins_df = pd.DataFrame.from_dict(coins_dict)

                    st.dataframe(coins_df)


                

                



            elif task == 'BOT':
                st.subheader('Menu do BOT')
                client = Client(api_key=key, api_secret=secret_key)

                coins_dict = {'TICKER':[], 'QNT':[]}
                mostrar_carteira = st.checkbox('Mostrar Carteira:')
                if mostrar_carteira:
                    for cur in client.get_account()['balances']:
                        if float(cur['free']) > 0:
                            coins_dict['TICKER'].append(cur['asset'])
                            coins_dict['QNT'].append(cur['free'])

                            coins_df = pd.DataFrame.from_dict(coins_dict)

                    st.dataframe(coins_df)


            elif task == 'Histórico':
                st.subheader('Histórico de Movimentações')
                client = Client(api_key=key, api_secret=secret_key)

                ticker = st.selectbox('Ticker', ['BTCBUSD', 'ETHBUSD'])

                df = get_minutedata(ticker=ticker, client=client)



                fig = plt.figure()
                ax = fig.add_subplot(1,1,1)

                plt.title(ticker)
                plt.ylabel('Close Price (USD)')
                plt.xlabel('Time (UTC)')
                ax.plot(df['Close'])

                st.write(fig)


                
                


            




    elif aba == 'Página Inicial': 
        st.subheader('Página Inicial')
        st.image('https://logodownload.org/wp-content/uploads/2021/03/binance-logo-0.png')

    elif aba == 'Sobre':
        st.subheader('Sobre:')
        st.text_area('Sobre', 
        value="WebApp de trade a partir da API da Binance")



    






if __name__ == '__main__':
    main()

