import streamlit as st
import sqlite3
import pandas as pd
from binance import Client
from binance.exceptions import BinanceAPIException
import matplotlib.pyplot as plt
from modules import get_minutedata


import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC



from base64 import b64encode

def encrypt(login: str=''):
    """ 
    Funcao que encrypta e salva as informacoes no banco de dados
    """
    salt = os.urandom(8)
    #print(f"salt_para_guardar={salt}")
    password = b64encode(salt).decode('ascii')

    #print(f"password.encode('ascii')={password.encode('ascii')}")
    new_salt = b64encode(password.encode('ascii'))
    #print(f"new_salt = {new_salt}")
    
    #print(f"new_salt_1 = {b64encode(new_salt).decode('ascii')}")


    #print(f"guarde isso={b64encode(salt).decode('utf-8')}")
    #print(f"b64encode(password)={b64encode(password.encode())}")
    kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=new_salt,
    iterations=390000,)


    #print(f'password.encode()={password.encode()} | KEY')
    key = base64.urlsafe_b64encode(kdf.derive(new_salt))
    #print(f'KEY = {key}')
    encrypter = Fernet(key)



    #print(f"login.encode()={login.encode()} | LOGIN")
    login_enc = encrypter.encrypt(login.encode())
    #print(f"password.encode()={password.encode()} | PASSWORD")
    password_enc = encrypter.encrypt(new_salt)


    return new_salt, password_enc

def decrypt(password_en: str='', salt: str=''):
    """ 
    Funcao que vai descriptografar as informacoes a partir da password do usuario
    """
    #salt = os.urandom(16)
    print(f"senha encrypt = {password_en.decode('ascii')}")
    salt = salt.encode('ascii')
    kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=390000,)

    key = base64.urlsafe_b64encode(kdf.derive(salt))
    #print(f'KEY_d ={key}')
    decrypter = Fernet(key)

    password_ = decrypter.decrypt(password_en)
    #login_    = decrypter.decrypt(login_en)


    #print(f"password_={password_}")
    #print(f"login_={login_}")
    print(f"password_.decode('ascii')={password_.decode('ascii')}")
    #print(f"login_.decode('ascii')={login_.decode('ascii')}")

    return password_

#------------------------------------------------------------------------------
# funcoes para o banco de dados 
conn = sqlite3.connect('data.db')
c = conn.cursor()
def create_usertable(): 
    """
    Funcao para criar o banco de dados para logins/senhas
    """
    c.execute('CREATE TABLE IF NOT EXISTS usertable(username TEXT, password TEXT, api_key TEXT, secret TEXT)')

    return
def add_userdata(username: str = '', password: str='', api_key: str='', secret: str=''): 
    """
    Funcao que adiciona um usuario novo ao banco de dados
    """
    try: 
        c.execute('INSERT INTO usertable(username, password, api_key, secret) VALUES (?,?,?,?)', (username, password, api_key, secret))
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
        
        if st.sidebar.checkbox('First Access'):
            username = st.sidebar.text_input('User')

            st.sidebar.text(f"Sua senha eh:")

        username = st.sidebar.text_input('User')
        password = st.sidebar.text_input('Password', type='password')



        if st.sidebar.checkbox('Login'):
            create_usertable()

            result = login_user(username = username, password = password)
            if result:
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
    #main()

    #print(str('ksjdhfksd', 'b'))
    #k = 'sdfsd6454fsf'
    #print(str.encode(k))
    # """ TESTES COM O BANCO DE DADOS """

    # create_usertable()
    # add_userdata(username='teste', password='teste', api_key='teste', secret='teste')
    # data = view_all_users()
    # print(data)


    """ TESTE PARA LOGIN DE USUARIO """
    login = 'lucas'


    salt, password_en = encrypt(login=login)
    print(f"Sua senha eh: {salt.decode('ascii')}")


    l = decrypt(password_en=password_en, salt=salt.decode('ascii'))
    print(l.decode('ascii'))


    """ 
    FALTA FAZER FUNCAO QUE ESCREVE LOGIN (NON-ENCRYPT) E SENHA (ENCRYPTED) NO DB,
    FALTA FAZER UMA FUNCAO QUE RECEBE O LOGIN E SENHA E BUSCA ESSES DADOS NO BANCO DE DADOS,
    FALTA FAZER UMA FUNCAO QUE RECEBE UMA STRING_ENCRYPTED E TENTA DESCRYPTAR COM A KEY (PASSWORD_USER) ENVIADA,
    """



    # key = Fernet.generate_key()
    # pw = b'teste'

    # first_cryto = Fernet(key)

    # print(f'first={first_cryto.encrypt(pw)}')
    # print(f"second_decrypt={first_cryto.decrypt(first_cryto.encrypt(pw))}")

    # salt = os.urandom(16)

    # kdf = PBKDF2HMAC(
    # algorithm=hashes.SHA256(),
    # length=32,
    # salt=salt,
    # iterations=390000,)

    # key_2 = base64.urlsafe_b64encode(kdf.derive(pw))
    # second_crypto = Fernet(key_2)

    # print(f"second2={second_crypto.encrypt(pw)}")
    # print(f"second_decrypt2={second_crypto.decrypt(second_crypto.encrypt(pw))}")



    # salt = os.urandom(16)

    # kdf = PBKDF2HMAC(
    # algorithm=hashes.SHA256(),
    # length=32,
    # salt=salt,
    # iterations=390000,)

    # key_2 = base64.urlsafe_b64encode(kdf.derive(pw))
    # second_crypto = Fernet(key_2)

    # print(f"second2={second_crypto.encrypt(pw)}")
    # print(f"second_decrypt2={second_crypto.decrypt(second_crypto.encrypt(pw))}")

    pass

    """
    AJUSTA SEÇAO DE LOGIN PARA A PASSWORD VIRAR A KEY DE ENCRIPTACAO DAS INFOS DO USUARIO, 
    ASSIM PODENDO DEIXAR AS INFORMACOES NO BANCO DE DADOS
    """
    
