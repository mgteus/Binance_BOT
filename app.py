import streamlit as st
import matplotlib.pyplot as plt
from binance import Client
from streamlit.elements.selectbox import SelectboxMixin

from main import slope_vol_strat
from modules import check_valid_user, crypto_df_binance, get_hist_df, get_minutedata, add_user, check_users_login
from modules import encrypt_first_login, get_max_quant_trade, set_infos_to_session_in_st, check_valid_api_and_secret
from modules import get_ticker_infos,get_min_quant_in_float




def main():
    """
    Funcao principal do app
    """
    st.title('BOT_Binance')
    menu = ['Página Inicial', 'Login', 'Sobre', 'Sign Up']

    aba = st.sidebar.selectbox('Menu', menu)

    if aba == 'Login':
        st.subheader('Menu')
        
        username = st.sidebar.text_input('User')
        password = st.sidebar.text_input('Password', type='password')



        if st.sidebar.checkbox('Login'):
            result, api, secret = check_users_login(username, password)
            if result:
                st.sidebar.success(f'Logged In as {username}')
                client = Client(api_key=api, api_secret=secret)
                task = st.selectbox('Page', ['Binance Info', 'BOT', 'BUY-SELL ZONE'])
                df_balance = crypto_df_binance(client=client)

                if task == 'Binance Info':
                    st.subheader('Informaçoes da Binance')
                    
                    st.dataframe(df_balance)

                    st.subheader(f"TOTAL: U${round(sum(df_balance['VALUE (USD)']),2)}")


            
                elif task == 'BOT':
                    st.subheader('Parametros do BOT')
                    st.subheader('Escolha a sua estrategia:')
                    if st.checkbox('MACD'):
                        ticker_macd = st.selectbox('Ticker', df_balance.loc[df_balance['VALUE (USD)'] > 10]['TICKER'])
                        st.warning(f'MACD em {ticker_macd}')

                    elif st.checkbox('SLOPE+VOL'):
                        # definindo variavel inicial para compra
                        st.session_state['open_position'] = False
                        ticker_col, min_range_col, max_range_col, quant_col, interval_col = st.columns(5)
                        ticker_slope = ticker_col.selectbox('Ticker', df_balance.loc[df_balance['VALUE (USD)'] > 15]['TICKER'])
                        min_range = min_range_col.selectbox('Range Min', [i for  i in range(1, 12)], index=7)
                        max_range = max_range_col.selectbox('Range Max', [i for i in range(15,31)], index=6)
                        quant_max_by_ticker = get_max_quant_trade(list(df_balance.loc[df_balance['TICKER'] == ticker_slope]['VALUE (USD)']))
                        quant = quant_col.selectbox('Quantity (USD)', [i for i in range(15,quant_max_by_ticker)], index=0)
                        interval = interval_col.selectbox('Interval (min)', [1,5,15], index=1)
                        
                        infos = ['ticker_slope', 'quant_slope', 'interval_slope']
                        st.warning(f'SLOPE+VOL em {ticker_slope} com range_min = {min_range}, \
                                     range_max = {max_range} e quantity = {quant} no intervalo de {interval}min')


                        if st.checkbox('Iniciar Trade'):
                            set_infos_to_session_in_st(infos, [ticker_slope, quant, interval])

                            slope_vol_strat(ticker=st.session_state['ticker_slope']+'BUSD', 
                                            quant=st.session_state['quant_slope'], 
                                            open_position=st.session_state['open_position'], 
                                            client=client, 
                                            interval=st.session_state['interval_slope'])
                            
                # st.session_state['trade_hist']= {'DATE': ['2021-12-20',],
                #                           'ENTRADA': [23423,],
                #                           'SAIDA': [2523,],
                #                           'PROFIT':[0.3,],
                #                           'GANHOS':[10,]}
                # adicionar mais tarde
                elif task == 'BUY-SELL ZONE':
                    ticker_col2, min_range_col2, max_range_col2, quant_col2, interval_col2 = st.columns(5)
                    ticker_test = ticker_col2.selectbox('Ticker', df_balance.loc[df_balance['VALUE (USD)'] > 15]['TICKER'])
                    min_range_test = min_range_col2.selectbox('Range Min', [i for  i in range(1, 12)], index=7)
                    max_range_test = max_range_col2.selectbox('Range Max', [i for i in range(15,31)], index=6)
                    quant_max_by_ticker_test = get_max_quant_trade(list(df_balance.loc[df_balance['TICKER'] == ticker_test]['VALUE (USD)']))
                    quant_test = quant_col2.selectbox('Quantity (USD)', [i for i in range(10,quant_max_by_ticker_test)], index=0)
                    interval_test = interval_col2.selectbox('Interval (min)', [1,5,15], index=1)

                    infos2 = ['ticker_slope', 'quant_slope', 'interval_slope']
                    st.warning(f'SLOPE+VOL em {ticker_test} com range_min = {min_range_test}, \
                                     range_max = {max_range_test} e quantity = {quant_test} no intervalo de {interval_test}min')

                    if st.button('COMPRA'):
                        new_quant_test = get_ticker_infos(ticker=ticker_test+'BUSD', client=client, quant=quant_test)
                        min_quant_test = get_min_quant_in_float(client.get_symbol_info(ticker_test+'BUSD')['filters'][2]['minQty'])
                        new_quant_test = f"{new_quant_test:.8f}"
                        min_quant_test = f"{min_quant_test:.8f}"
                        st.button(f'QUANT={new_quant_test}')
                        st.button(f'QUANT_MIN={min_quant_test}')
                
                 
                        if float(new_quant_test) < float(min_quant_test):
                            new_quant_test = min_quant_test

                        recvwindow_test = 10000

                        while True:
                            try:    
                                st.text(f"TENTANDO COMPRAR {new_quant_test}")
                                ordem_test = client.order_market_buy(symbol=ticker_test+"BUSD",
                                                            quantity=new_quant_test,
                                                            recvWindow=recvwindow_test)    # 10000 ms = 10s 
                                st.text(ordem_test)
                                break
                            except Exception as e:
                                if recvwindow_test < 20000:
                                    recvwindow_test+=100
                                st.error(e)
                                if float(new_quant_test) + float(min_quant_test) < quant_test*1.2:
                                    new_quant_test_aux = 100*float(min_quant_test) + float(new_quant_test)
                                    new_quant_test = f"{new_quant_test_aux:.8f}"

                        st.success('COMPREI E DEU TUDO CERTO')  

                show_hist = st.sidebar.checkbox('Histórico de Trades')
                if show_hist:
                    if 'trade_hist' not in st.session_state:
                        st.sidebar.button('Sem histórico de trades')
                    else:
                        st.sidebar.button('Funcionalidade em produção')
                        #st.sidebar.dataframe(get_hist_df(st.session_state['trade_hist']))
                    

            else:  # else do login, caso para senha invalida
                st.error('Impossivel Fazer Login')

    elif aba == 'Página Inicial': 
        st.subheader('Página Inicial')
        st.image('https://logodownload.org/wp-content/uploads/2021/03/binance-logo-0.png')

    elif aba == 'Sobre':
        st.subheader('Sobre:')
        st.text_area('Sobre', 
        value="WebApp de trade a partir da API da Binance")

    elif aba == 'Sign Up':
        st.subheader('Crie seu novo Usuário')
        new_user = st.text_input('Usuário')

        if st.checkbox('Validate New User'):
            if check_valid_user(new_user=new_user):
                st.text('Usuário aceito')

                

                # sessao de infos do usuario    
                st.subheader('Api-Key')
                api_key_from_input = st.text_input(' ', key='aa')
                    
                st.subheader('Secret')
                secret_from_input = st.text_input(' ', key='ss')

                if st.checkbox('Criptografar informacoes e criar usuario'):
                    
                    if not check_valid_api_and_secret():

                        users_password, password_enc, api_enc, secret_enc = encrypt_first_login(api_key_from_input, secret_from_input)
                        st.warning(f"Seu password eh: {users_password}")
                        st.warning(f"Anote o password acima em um papel ou em u local seguro, só sera possível logar utilizando-o")

                        try: 
                            add_user(user=new_user,
                                    password=password_enc,
                                    api_key=api_enc,
                                    secret=secret_enc)
                            st.success('Usuario Criado com Sucesso.')
                            st.success('Faça Login na aba de Login')

                        except:
                            st.error('Tente Novamente')
                    else:
                        st.warning('Possível problema com suas credenciais da API')
                        st.text('Gere novas credenciais no aplicativo da Binance e lembre de liberar o trade/spot')


            else:
                st.text('Usuário Repetido')

            

if __name__ == '__main__':
    main()
    pass
    #print(str('ksjdhfksd', 'b'))
    #k = 'sdfsd6454fsf'
    #print(str.encode(k))
    # """ TESTES COM O BANCO DE DADOS """

    # login = 'lucas'


    # salt, password_en = encrypt(login=login)
    # print(f"Sua senha eh: {salt.decode('ascii')}")


    # l = decrypt(password_en=password_en, salt=salt.decode('ascii'))
    # print(l.decode('ascii'))







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