from binance import Client
from binance.exceptions import BinanceAPIException
import pandas as pd 
import numpy as np
import ta as ta
import os
import math
import ccxt
import time
import streamlit as st
b = ccxt.binance({ 'options': { 'adjustForTimeDifference': True }})

from modules import get_secret_and_key, init_client, get_minutedata, get_slope, get_ticker_infos



def MACD_strat(ticker: str='', quant: float = 0, open_position: bool=False, client: Client=''):
    """
    Funcao da estrategia de MACD e TRIX
    """
    new_quant, buy_price, orders = 0, 0, 0
    while True:
        df = get_minutedata(ticker=ticker, client=client)

        if not open_position:
            macd_line = ta.trend.macd_diff(df['Close'])
            macd_line = macd_line.iloc[-1] > 0 and macd_line.iloc[-2] < 0
            MACD = macd_line

            trix = ta.trend.trix(df['Close'], window=7).iloc[-1]  
            TRIX = trix < 0

            if TRIX and MACD:
                
                new_quant = math.floor(float(str(15/df['Close'].iloc[-1])[:10]))
                ordem = client.create_order(symbol=ticker, 
                                            side='BUY', 
                                            type='MARKET', 
                                            quantity = new_quant)
                print(f"COMPRA = {ordem}")
                buy_price = float(ordem['fills'][0]['price'])
                open_position = True

                print(f'COMPREI {new_quant} {ticker}')
                

        if open_position:

            while True:
                df = get_minutedata(ticker=ticker, client=client)


                macd_line = ta.trend.macd_diff(df['Close'])
                MACD = macd_line.iloc[-1] < 0 and macd_line.iloc[-2] > 0
                
                trix = ta.trend.trix(df['Close']).iloc[-1]   
                TRIX = trix > 0


                if MACD and TRIX:

                    ordem = client.create_order(symbol =ticker,
                                                side = 'SELL', 
                                                type = 'MARKET', 
                                                quantity = new_quant)
                    sell_price = float(ordem['fills'][0]['price'])

                    print(f"ganhos = {(sell_price-buy_price)*new_quant}")
                    print(f"profit = {(sell_price-buy_price)/buy_price}")
                    print(f'VENDI {new_quant} {ticker}')
                    open_position = False

                    break


def slope_vol_strat(ticker: str='', quant: float = 0, open_position: bool=False, client: Client='', interval: int=0):
    """ 
    Funcao de trade com a estrategia de volume e estrategia de slope para 8 e 21 dias
    """     
    new_quant, buy_price, orders = 0, 0, 0
    while True:
        df = get_minutedata(ticker=ticker, client=client, interval=interval)

        if not open_position:

            st.button('BUSCANDO COMPRA', key='compra')

            VOL_TEST = df['Volume'].iloc[-1] > np.mean(df['Volume'].iloc[-21:-1])
            
            PRICE = df['Close'].iloc[-1] > np.mean(df['Close'].iloc[-21:-1])

            y_lr = list(df['Close'].dropna())
            x_lr = [f for f in range(len(y_lr))]
            lr_8 = get_slope(x_lr, y_lr, 8)
            lr_21 = get_slope(x_lr, y_lr, 21)

            #display no app
            col1, col2, col3, col4 = st.columns(4)

            lr8_b = st.empty()
            lr21_b = st.empty()
            lrv_b = st.empty()
            lrp_b = st.empty()

            if VOL_TEST:            
                lr8_b.col3.button("VOL: ✅", key='vol')
            else:
                lr8_b.col3.button("VOL: ❌", key='vol')
            
            if PRICE:
                col4.button("PRICE: ✅", key='price')
            else:
                col4.button("PRICE: ❌", key='price')
            if lr_8 > 0:
                col1.button("LR8: ✅", key='lr8')
            else:
                col1.button("LR8: ❌",key='lr8')

            if lr_21 > 0:
                col2.button("LR21: ✅", key='lr21')
            else:
                col2.button("LR21: ❌", key='lr21')
            
            
            LR = lr_21 > 0 and lr_8 > 0

            if LR and VOL_TEST and PRICE:
                
                new_quant = get_ticker_infos(ticker=ticker, client=client, quant=quant)
                 
                ordem = client.order_market_buy(symbol=ticker,
                                                quantity=new_quant,
                                                recvWindow=10000)    # 10000 ms = 10s 

                #print(f"COMPRA = {ordem}")
                buy_price = float(ordem['fills'][0]['price'])
                open_position = True
                usd_ = round(new_quant*buy_price,2)
                st.text(f"COMPREI {new_quant} {ticker} ({usd_} USD)")
            #print(f"LR => 8 - {lr_8} | 21 - {lr_21}")
            #print(f"VOL_TEST => { df['Volume'].iloc[-1]} > {np.mean(df['Volume'].iloc[-21:-1])}")
            time.sleep(60)

        if open_position:

            st.button('BUSCANDO VENDA', key='venda')

            while True:
                df = get_minutedata(ticker=ticker, client=client, interval=interval)


                y_lr = list(df['Close'].dropna())
                x_lr = [f for f in range(len(y_lr))]
                # 8 tempos
                lr_8_saida = get_slope(x_lr, y_lr, 8)

                
                lr_21_saida = get_slope(x_lr, y_lr, 21)
                #print(f"lr_8_saida={lr_8_saida}")


                trix = ta.trend.trix(df['Close'], window=8).iloc[-1]
                TRIX = trix < 0

                if TRIX:
                    st.button("TRIX_SAIDA: ✅", key='trix')
                else:
                    st.buuton("TRIX_SAIDA: ❌", key='trix')

                # TESTE VOLUME SAIDA
                VOL_TEST_SAIDA = df['Volume'].iloc[-1] > np.mean(df['Volume'].iloc[-21:-1])

                # decisao de saída 
                LR_SAIDA = lr_8_saida < 0 and lr_21_saida < 0

                if LR_SAIDA:
                    st.button("LR_SAIDA: ✅", key='lr_saida')
                else:
                    st.buuton("LR_SAIDA: ❌", key='lr_saida')

                if LR_SAIDA and TRIX:
                    ordem = client.order_market_sell(symbol=ticker,
                                                     quantity=new_quant,
                                                     recvWindow=10000)


                    sell_price = float(ordem['fills'][0]['price'])

                    usd_venda = round(new_quant*sell_price, 2)
                    st.text(f'VENDI {new_quant} {ticker} ({usd_venda} USD)')
                    st.text(f"ganhos = {(sell_price-buy_price)*new_quant}")
                    st.text(f"profit = {(sell_price-buy_price)/buy_price}")
                    
                    open_position = False

                #print(f"LR_SAIDA => 8 - {lr_8_saida} | 21 - {lr_21_saida}")
                #print(f"VOL_TEST_SAIDA => { df['Volume'].iloc[-1]} > {np.mean(df['Volume'].iloc[-21:-1])}")
                
                if LR_SAIDA and VOL_TEST_SAIDA:
                    break
                time.sleep(60)

def make_prints(j):
    for i in range(23):
        st.text(f'AHHHHHHH {j}')
    return

if __name__ == '__main__':
    path_api = r'C:\Users\mateu\workspace\api_binance.txt'
    x, y = get_secret_and_key(path_api)
    client = init_client(x, y)

    slope_vol_strat(ticker='', quant=0, client=client)