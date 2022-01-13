
import os 
import time
import math
import base64
import datetime

import pandas as pd
import numpy as np
import streamlit as st

from binance import Client
from base64 import b64encode
from cryptography.fernet import Fernet
from sklearn.linear_model import LinearRegression
from cryptography.hazmat.primitives import hashes
from binance.exceptions import BinanceAPIException
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC





def encrypt_first_login(api: str='', secret: str='') -> tuple([bytes, bytes]):
    """ 
    Funcao que encrypta o primeiro login de um usuario devolvendo sua senha e infos criptografadas

    return new_salt, password_enc, api_enc, secret_enc
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
    kdf_e2 = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=new_salt,
    iterations=390000,)


    #print(f'password.encode()={password.encode()} | KEY')
    key = base64.urlsafe_b64encode(kdf_e2.derive(new_salt))
    #print(f'KEY = {key}')
    encrypter = Fernet(key)


    #print(f"password.encode()={password.encode()} | PASSWORD")
    password_enc = encrypter.encrypt(new_salt).decode('ascii')
    api_enc = encrypter.encrypt(api.encode('ascii')).decode('ascii')
    secret_enc = encrypter.encrypt(secret.encode('ascii')).decode('ascii')


    return new_salt.decode('ascii'), password_enc, api_enc, secret_enc

def decrypt(text_en: str='', salt: str=''):
    """ 
    Funcao que vai descriptografar as informacoes a partir da password do usuario
    """
    salt = salt.encode('ascii')

    kdf_d = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=390000,)

    key = base64.urlsafe_b64encode(kdf_d.derive(salt))
    #print(f'KEY_d ={key}')
    decrypter = Fernet(key)

    password_ = decrypter.decrypt(text_en.encode('ascii'))
    #login_    = decrypter.decrypt(login_en)


    #print(f"password_={password_}")
    #print(f"login_={login_}")
    #print(f"password_.decode('ascii')={password_.decode('ascii')}")
    #print(f"login_.decode('ascii')={login_.decode('ascii')}")

    return password_.decode('ascii')

def encrpyt_string(text: str = '', key: str =''):
    """
    Funcao que encrypta informacoes do usuario a partir da key enviada
    """

    key_ = b64encode(key.encode('ascii'))

    kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=key_,
    iterations=390000,)


    #print(f'password.encode()={password.encode()} | KEY')
    key = base64.urlsafe_b64encode(kdf.derive(key_))
    #print(f'KEY = {key}')
    encrypter = Fernet(key)

    return encrypter.encrypt(text.encode('ascii'))

def get_users_data():
    """
    Funcao que vai ler o csv de infos dos usuarios e o devolve como dataframe
    """
    df = pd.read_csv('users_data.csv')


    return df

def add_user(user: str='', password: str= '', api_key:str='', secret: str=''):
    """
    Funcao que adiciona um novo usuario ao csv 
    """
    df = get_users_data()
    my_dict = {'USER': user,
               'PASSWORD': password,
               'API_KEY': api_key,
               'SECRET': secret}
    new_user_df = pd.DataFrame(data=my_dict, columns=my_dict.keys(), index=[0])
    
    df = df.append(new_user_df, ignore_index=True)

    df.to_csv('users_data.csv', index=False)

    return 

def check_valid_user(new_user:str=''):
    """
    Funcao que retorna se eh possivel criar novo usuario com login escolhido.
    Nao podemos ter dois usuarios com o mesmo user
    """ 
    if len(new_user) < 15 and not new_user.isnumeric() and not new_user[0].isnumeric():
        df = get_users_data()

        users_list = list(df['USER'])

        if new_user in users_list:
            # ja existe usuario com esse login
            return False
        else:
            # novo usuario liberado 
            return True
    else:
        return False

def check_valid_api_and_secret(api:str = '', secret: str=''):
    """
    Funcao simples que testa a api_key e a secret_key do usuario criando um client_test

    Retorna True caso OK
    """
    try: 
        client_test = Client(api_key=api, api_secret=secret)

        client_test.create_test_order(
        symbol='BNBBTC',
        side='BUY',
        type="MARKET",
        quantity=1,
        newClientOrderId='123123', 
        recvWindow=10000)

        return True
    except Exception as e:
        print(e)
        return False

def check_users_login(user: str='', password: str=''):
    """
    Funcao que faz o login do usuario recebido
    """

    df = get_users_data()
    df_user = df.loc[df['USER']==user].copy()

    if df_user.shape[0] == 0:
        return False, 1, 1

    else:

        password_enc = df_user['PASSWORD'].item()
        api_key_enc  = df_user['API_KEY'].item()
        secret_enc   = df_user['SECRET'].item()

        try: 
            decrypt(text_en=password_enc, salt=password)
            #print('Senha aceita')
            return True, decrypt(api_key_enc, password), decrypt(secret_enc, password)
        
        except:
            #print('Senha Invalida')
            return False, None, None

def get_secret_and_key(path: str='') -> str and str:
    """
    Funcao simples que le a primeira linha de um txt do path e splita na virgula
    devolvendo a api key e api secret.
    """
    try:
        with open(path, 'r') as file:  # lendo as infos da api
            line = file.read()
            api_key, api_secret = line.split(',')
        return api_key, api_secret

    except Exception as e:
        print(e)
        return '', ''
        
def init_client(key: str = '', secret: str = '', balance: bool = False) -> bool:
    """
    Funcao que inicia o client da binance dado pela key e secret.
    Retorna True caso o cliente funcione
    """

    client = Client(api_key=key, api_secret=secret)

    if balance:
        for cur in client.get_account()['balances']:
            if float(cur['free']) > 0:
                print(cur['asset'], cur['free'])

    return client

def add_log(path: str = '', order_buy: dict = {}, order_sell: dict = {}) -> None:
    """ 
    Funcao que adiciona o resultado de uma ordem de compra e a ordem de venda ao arquivo no path
    """
    
    #if order_buy != {} and order_sell != {}:
    ticker     = 4#float(order_buy['symbol'])
    price_buy  = 3#float(order_buy['fills'][0]['price'])
    buy_tax    = 1#float(order_buy['fills'][0]['price'])*.99
    price_sell = 2#float(order_sell['fills'][0]['price'])
    sell_tax   = 4#float(order_sell['fills'][0]['price'])*.99
    percent    = 4#((price_sell-sell_tax) - (price_buy+buy_tax))/price_buy
    profit_usd = round(price_sell - price_buy - buy_tax - sell_tax, 2)

    log_dict = {'TICKER': [ticker],
                'P-COMPRA': [price_buy],
                'TAXA-CMP': [buy_tax],
                'P-VENDA': [price_sell],
                'TAXA-VND': [sell_tax],
                'PROFIT': [percent],
                'GAIN (USD)' : [profit_usd]}

    df = pd.DataFrame.from_dict(log_dict)
    print(df)

def get_minutedata(ticker: str = '', client: Client='', interval: int = 0):
    """
    Funcao que recebe um ticker, client e intervalo (1min, 5min ou 15min) e devolve
    um dataframe do valor de fechamente desse ticker em funcao do intervalo escolhido


    return df
    """

    if isinstance(client, Client):
        if interval == 5:
            try:
                df = pd.DataFrame(client.get_historical_klines(ticker,
                                                            Client.KLINE_INTERVAL_5MINUTE,
                                                            '200m UTC'))
            except BinanceAPIException as error:
                print(error)
                time.sleep(60)
                df = pd.DataFrame(client.get_historical_klines(ticker,
                                                            Client.KLINE_INTERVAL_5MINUTE,
                                                            '200m UTC'))
            df = df.iloc[:,:6]
            df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
            df.set_index('Time', inplace=True)
            df.index = pd.to_datetime(df.index, unit='ms')
            df = df.astype(float)

            return df

        elif interval == 1:
            try:
                df = pd.DataFrame(client.get_historical_klines(ticker,
                                                            Client.KLINE_INTERVAL_1MINUTE,
                                                            '200m UTC'))
            except BinanceAPIException as error:
                print(error)
                time.sleep(60)
                df = pd.DataFrame(client.get_historical_klines(ticker,
                                                            Client.KLINE_INTERVAL_1MINUTE,
                                                            '200m UTC'))
            df = df.iloc[:,:6]
            df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
            df.set_index('Time', inplace=True)
            df.index = pd.to_datetime(df.index, unit='ms')
            df = df.astype(float)

            return df

        elif interval == 15:
            try:
                df = pd.DataFrame(client.get_historical_klines(ticker,
                                                            Client.KLINE_INTERVAL_15MINUTE,
                                                            '1 day ago UTC'))
            except BinanceAPIException as error:
                print(error)
                time.sleep(60)
                df = pd.DataFrame(client.get_historical_klines(ticker,
                                                            Client.KLINE_INTERVAL_15MINUTE,
                                                            '1 day ago UTC'))
            df = df.iloc[:,:6]
            df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
            df.set_index('Time', inplace=True)
            df.index = pd.to_datetime(df.index, unit='ms')
            df = df.astype(float)

            return df

        else:
            return None
    return None

def get_ticker_infos(ticker: str = '', client: Client='', quant: int=0, val: bool=True):
    """
    Funcao que devolve as informacoes importantes sobre o ticker que estamos usando.
        if val retorna a quantidade correta para o trade;
        else retorna todas as infos usadas para fazer o calculo da quantidade correta.
    """
    infos = client.get_symbol_info(symbol=ticker)['filters'][2]
    price  = float(client.get_symbol_ticker(symbol=ticker)['price'])

    amount = quant/price

    min = float(infos['minQty'])
    step = float(infos['stepSize'])

    if val:
        new_quant = round((amount // step)*step, len(infos['stepSize']))
        return new_quant
    else: 
        return min, step

def get_slope(x, y, L):
    """
    Funcao que retorna o slope da serie temporal dos dados
    """
    try:
        x=np.array(x).reshape(-1, 1)
        y=np.array(y).reshape(-1, 1)
        lr=LinearRegression()
        lr.fit (x[:L],y[:L])
        return lr.coef_[0][0]      
    except:
        return 0 

def crypto_df_binance(client: Client=''):
    """
    Funcao que retorna um dataframe com as infos da carteira associada ao client

    return df
    """
    balances = client.get_account()['balances']
    wallet = {'ticker':[], 'qnt': [], 'price':[], 'tot':[]}
    for coin_dict in balances:
        if float(coin_dict['free']) > 0:
            if coin_dict['asset'] == 'BUSD':
                wallet['ticker'].append(coin_dict['asset'])
                wallet['qnt'].append(float(coin_dict['free']))
                wallet['price'].append(1)
                wallet['tot'].append(round(float(coin_dict['free']),2))
            else:
                wallet['ticker'].append(coin_dict['asset'])
                wallet['qnt'].append(float(coin_dict['free']))
                ticker = coin_dict['asset'] 
                price = round(float(client.get_symbol_ticker(symbol=ticker+'BUSD')['price']), 2)
                wallet['price'].append(price)
                wallet['tot'].append(round(float(coin_dict['free'])*price, 2))
    df = pd.DataFrame(wallet)
    df.columns = ['TICKER', 'QUANTITY', 'PRICE (USD)', 'VALUE (USD)'] 
    return df

def show_info_trade_w_streamlit(open_position: bool=False, status_list: list = [],
                         indicators_list: list = [], client: Client ='', b_index: int=0):
    """
    Funcao que ira criar os _botoes_ no app para monstrar quais indicadores
    estao em posicao de compra ou venda
    """

    def check_icon(x):
        if x:
            return "✅"
        else:
            return "❌"

    server_time = int(client.get_server_time()['serverTime'])/1000
    if not open_position:  # buscando compra
        col1, col2 = st.columns([1,3])
        col1.button('Buscando Compra', key=str(os.urandom(7))+str(b_index))
        col2.button(datetime.datetime.fromtimestamp(server_time).strftime('%Y-%m-%d %H:%M:%S')+' (BOT)'+ " - " +
                    datetime.datetime.utcfromtimestamp(server_time).strftime('%Y-%m-%d %H:%M:%S')+' (UTC)', 
                    key=str(os.urandom(7))+str(b_index))

        cols = st.columns(len(indicators_list))
        cols_indices = [i for i  in range(len(indicators_list))]

        for status, indicator, col_index in zip(status_list, indicators_list, cols_indices):
            cols[col_index].button(f"{indicator}: {check_icon(status)}",
                                     key=str(os.urandom(7))+str(b_index))

    else:
        col1, col2 = st.columns([1,3])
        col1.button('Buscando Venda', key=str(os.urandom(7))+str(b_index))
        col2.button(datetime.datetime.fromtimestamp(server_time).strftime('%Y-%m-%d %H:%M:%S')+' (BOT)' + " - " +
                    datetime.datetime.utcfromtimestamp(server_time).strftime('%Y-%m-%d %H:%M:%S')+' (UTC)',
                     key=str(os.urandom(7))+str(b_index))

        cols = st.columns(len(indicators_list))
        cols_indices = [i for i  in range(len(indicators_list))]

        for status, indicator, col_index in zip(status_list, indicators_list, cols_indices):
            cols[col_index].button(f"{indicator}: {check_icon(status)}",
             key=str(os.urandom(7))+str(b_index))

    return

def show_buy_and_sell_w_streamlit(open_position:bool=False, 
                                    ticker:str='', 
                                    quant: int=0,
                                    usd: int=0,):
    """
    Funcao que printa as infos de compra ou venda no app
    """
    if not open_position:
        st.markdown(f"COMPRA de {quant} {ticker} ({usd}USD)")
    else:
        st.markdown(f"VENDA de {quant} {ticker} ({usd}USD)")
 
    return 

def display_streamlit_text(text: str=''):
    """
    Funcao simples que apresenta _text_ no app
    """

    st.markdown("**"+text+"**")


    return

def get_max_quant_trade(values: list = []):
    """
    Funcao simples que retorna o math.floor do valor maximo de uma lista

    return math.floor(max)
    """

    return math.floor(max(values))

def add_trade_to_hist(date: str='N/A', entry:int = 0, \
                    out: int = 0, profit: float = 0., ganhos: float=0. ):
    """
    Funcao que vai adicionar informacoes de uma trade completa na variavel de
    historico da sessao do app atual
    """
    if 'trade_hist' not in st.session_state:
        st.session_state['trade_hist'] = {'DATE': [date,],
                                          'ENTRADA': [entry,],
                                          'SAIDA': [out,],
                                          'PROFIT':[profit,],
                                          'GANHOS':[ganhos,]}
    else:
        st.session_state['trade_hist']['DATE'].append(date)
        st.session_state['trade_hist']['ENTRADA'].append(date)
        st.session_state['trade_hist']['SAIDA'].append(date)
        st.session_state['trade_hist']['PROFIT'].append(date)
        st.session_state['trade_hist']['GANHOS'].append(date) 
    
    return 

def get_time_from_client(client: Client=''):
    """
    Funcao simples que retorna uma string do tempo (BOT) atual
    """
    server_time = int(client.get_server_time()['serverTime'])/1000
    date = datetime.datetime.fromtimestamp(server_time).strftime('%Y-%m-%d %H:%M:%S') 
    return date

def get_hist_df(hist_dict: dict={}):
    """
    Funcao que recebe o dicionario com o historico de trade e devolve um dataframe


    return df
    """
    cols = ['DATA', 'ENTRADA (USD)', 'SAIDA (USD)', 'PROFIT (%)', 'GANHOS (USD)']
    df = pd.DataFrame(hist_dict)

    df.columns = cols

    return df

def set_open_position_in_st(side:bool=False):
    """
    Funcao simples que cria a variavel open_position da sessao no app 
    """
    if 'open_position' not in st.session_state:
        if side:
            st.session_state['open_position'] = True
        else:
            st.session_state['open_position'] = False         
            return 
    else:
        return 

def change_open_position_in_st():
    """ 
    Funcao simples que troca o booleano da variavel de open_position dentro do app
    """
    if st.session_state['open_positon']:
        st.session_state['open_position'] = False
    else:
        st.session_state['open_position'] = True

    return 

def set_infos_to_session_in_st(infos_list:list=[], values_list: list=[]):
    """
    Funcao que vai salvar as informaçoes escolhidas para o trade na sessao do app
    """
    for item, val in zip(infos_list, values_list):
        if item not in st.session_state:
            st.session_state[item] = val
        else:
            st.session_state[item] = val
    
    return
  
    
if __name__ == '__main__':


    # t = 1
    # times ={"1":0,"5":0, "15":0}

    # for t in range(181):

    #     if t%14==0:
    #         times['1']+=1
    #     if t%30==0:
    #         times['5']+=1
    #     if t%90==0:
    #         times['15']+=1
        

    # print(times) 

    path_api = r'C:\Users\mateu\workspace\api_binance.txt'
    x, y = get_secret_and_key(path_api)

    check_valid_api_and_secret(x,y)

    




    # hist_dict = {'DATE': ['2021-12-20',],
    #                                       'ENTRADA': [23423,],
    #                                       'SAIDA': [2523,],
    #                                       'PROFIT':[0.3,],
    #                                       'GANHOS':[10,]}

    # print(get_hist_df(hist_dict=hist_dict))                                     
    #show_info_trade_w_streamlit(client=client)

    #print(pd.DataFrame(client.get_historical_klines("BNBBUSD",
                                                            #  Client.KLINE_INTERVAL_15MINUTE,
                                                            #  '1 day ago UTC')))

    #print(crypto_df_binance(client=client))
    #print(get_minutedata("BNBBUSD", client, 15))



    # new_salt, password_enc, api_enc, secret_enc = encrypt_first_login(api='api', secret='secret')

    # print(f"senha={new_salt}")

    # add_user(user='admin1',
    #         password=password_enc,
    #         api_key=api_enc,
    #         secret=secret_enc)


    # first = check_users_login(user='admin1', password='123455')
    # print(f"first = {first}")

    # second = check_users_login(user='admin1', password=new_salt)
    # print(f"second = {second}")
    # if new_salt.decode('ascii') == decrypt(text_en=password_enc.decode('ascii'), salt=senha):
    #     print('Senha aceita')
    #     print(decrypt(api_enc.decode('ascii'), senha))
    #     print(decrypt(secret_enc.decode('ascii'), senha))
    #     print(decrypt(password_enc.decode('ascii'), senha))



    #check_users_login(user='teste1', password='')
    #print(get_ticker_infos(ticker='BTCBUSD', quant=9))
    # coins_dict = {'TICKER':[], 'QNT':[]}
    # coins_dict_for_price = {}
    # for cur in client.get_account()['balances']:
    #     if float(cur['free']) > 0:
    #         coins_dict['TICKER'].append(cur['asset'])
    #         coins_dict['QNT'].append(cur['free'])
    #         coins_dict_for_price[cur['asset']]=cur['free']
    # print(coins_dict)
    # print(coins_dict_for_price)
    # for corr in client.get_all_tickers():
    #     if corr['symbol'].replace('BUSD', '') in coins_dict['TICKER']:
    #         print(corr)
    #         print(round(float(coins_dict_for_price[corr['symbol'].replace('BUSD', '')])*float(corr['price']),2))
        

    # df = get_minutedata('BTCBUSD', client)
    # print(df)
    