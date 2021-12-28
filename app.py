import streamlit as st
import sqlite3
import pandas as pd
from binance import Client
from binance.exceptions import BinanceAPIException
import matplotlib.pyplot as plt
from main import make_prints, slope_vol_strat
from modules import check_valid_user, crypto_df_binance, get_minutedata, add_user, get_users_data, check_users_login
from modules import encrpyt_string, encrypt_first_login, decrypt



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
                task = st.selectbox('Page', ['Binance Info', 'BOT', 'Histórico'])
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
                        ticker_col, min_range_col, max_range_col, quant_col = st.columns(4)
                        ticker_slope = ticker_col.selectbox('Ticker', df_balance.loc[df_balance['VALUE (USD)'] > 10]['TICKER'])
                        min_range = min_range_col.selectbox('Range Min', [i for  i in range(1, 12)], index=7)
                        max_range = max_range_col.selectbox('Range Max', [i for i in range(15,31)], index=6)
                        quant = quant_col.selectbox('Quantity (USD)', [i for i in range(20,76)], index=10)
                        st.warning(f'SLOPE+VOL em {ticker_slope} com range_min = {min_range}, range_max = {max_range} e quantity = {quant} ')
 
                        if st.checkbox('Iniciar Trade'):
                            st.subheader('Selecione o intervalo:')
                            interval = st.selectbox('Interval', [1, 5])

                            #make_prints(interval)
                            slope_vol_strat(ticker=ticker_slope+'BUSD', quant=quant, open_position=False, client=client, interval=interval)
                            


                elif task == 'Histórico':
                    st.subheader('Histórico de Movimentações')

                    ticker = st.selectbox('Ticker', ['BTCBUSD', 'ETHBUSD'])

                    df = get_minutedata(ticker=ticker, client=client)



                    fig = plt.figure()
                    ax = fig.add_subplot(1,1,1)

                    plt.title(ticker)
                    plt.ylabel('Close Price (USD)')
                    plt.xlabel('Time (UTC)')
                    ax.plot(df['Close'])

                    st.write(fig)


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

                    users_password, password_enc, api_enc, secret_enc = encrypt_first_login(api_key_from_input, secret_from_input)
                    st.warning(f"Seu password eh: {users_password}")
                    st.warning(f"Anote o password acima em um papel ou em u local seguro, só sera possível logar utilizando-o")

                    try: 
                        add_user(user=new_user,
                                password=password_enc,
                                api_key=api_enc,
                                secret=secret_enc)
                        st.success('Usuario Criado com Sucesso.')
                        st.success('Faca Login na aba de Login')

                    except:
                        st.error('Tente Novamente')



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