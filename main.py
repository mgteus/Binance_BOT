import pandas as pd 
import numpy as np
import ta as ta
import os
import math
import ccxt
import time

from binance import Client
from modules import display_streamlit_text, get_secret_and_key, init_client, get_minutedata, get_slope, get_ticker_infos, show_buy_and_sell_w_streamlit
from modules import show_info_trade_w_streamlit, get_time_from_client, add_trade_to_hist, change_open_position_in_st, set_open_position_in_st

b = ccxt.binance({ 'options': { 'adjustForTimeDifference': True }})

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
    t = 0
    waiting_time = 14         # 60s
    if interval == 5:
        waiting_time = 30
    elif interval == 15:
        waiting_time = 90
    
    while True:
        df = get_minutedata(ticker=ticker, client=client, interval=interval)

        if not open_position:
            t = 0

            set_open_position_in_st(side=False)
            t = t + 1


            

            VOL_TEST = df['Volume'].iloc[-1] > np.mean(df['Volume'].iloc[-21:-1])
            
            PRICE = df['Close'].iloc[-1] > np.mean(df['Close'].iloc[-21:-1])

            y_lr = list(df['Close'].dropna())
            x_lr = [f for f in range(len(y_lr))]

            lr_8 = get_slope(x_lr, y_lr, 8)
            LR8 = lr_8 > 0
            lr_21 = get_slope(x_lr, y_lr, 21)
            LR21 = lr_21 > 0         
            
            LR =  LR8 and LR21

            # indicadores de entrada discretizados
            indicators = ['VOL_TEST', 'PRICE', 'LR8', 'LR21']
            # status de cada indicador
            status = [VOL_TEST, PRICE, LR8, LR21]
            

            if t % waiting_time == 0:
                show_info_trade_w_streamlit(open_position, status, indicators, client, t)


            if LR and VOL_TEST and PRICE:
                show_info_trade_w_streamlit(open_position, status, indicators, client, t)
                new_quant = get_ticker_infos(ticker=ticker, client=client, quant=quant)
                 
                ordem = client.order_market_buy(symbol=ticker,
                                                quantity=new_quant,
                                                recvWindow=10000)    # 10000 ms = 10s 

                buy_price = float(ordem['fills'][0]['price'])
                
                usd_ = round(new_quant*buy_price,2)
                orders = orders + 1
                show_buy_and_sell_w_streamlit(open_position, ticker, new_quant, usd_)
                open_position = True
                change_open_position_in_st()
                
            time.sleep(5)


        if open_position:

            while True:
                set_open_position_in_st(side=True)
                t = t + 1

                df = get_minutedata(ticker=ticker, client=client, interval=interval)

                y_lr = list(df['Close'].dropna())
                x_lr = [f for f in range(len(y_lr))]

                lr_8_saida = get_slope(x_lr, y_lr, 8)
                LR8_S = lr_8_saida < 0
                
                lr_21_saida = get_slope(x_lr, y_lr, 21)
                LR21_S = lr_21_saida < 0


                trix = ta.trend.trix(df['Close'], window=8).iloc[-1]
                TRIX = trix < 0


                # TESTE VOLUME SAIDA
                VOL_TEST_SAIDA = df['Volume'].iloc[-1] > np.mean(df['Volume'].iloc[-21:-1])

                # decisao de saída 
                LR_SAIDA = LR8_S and LR21_S


                indicators_s = ['LR8', 'LR21', 'TRIX']
                status_s = [LR8_S, LR21_S, TRIX]

                if t % waiting_time == 0:
                    show_info_trade_w_streamlit(open_position, status_s, indicators_s, client, t)

                if LR_SAIDA and TRIX:
                    show_info_trade_w_streamlit(open_position, status_s, indicators_s, client, t)
                    ordem = client.order_market_sell(symbol=ticker,
                                                     quantity=new_quant,
                                                     recvWindow=10000)


                    sell_price = float(ordem['fills'][0]['price'])

                    usd_venda = round(new_quant*sell_price, 2)
                    orders = orders + 1
                    show_buy_and_sell_w_streamlit(open_position, ticker, new_quant, usd_venda)


                    ganhos = (sell_price-buy_price)*new_quant
                    profit = (sell_price-buy_price)/buy_price
                    display_streamlit_text(f"GANHOS = {ganhos}")
                    display_streamlit_text(f"PROFIT = {profit}")

                    data_final_venda = get_time_from_client(client=client)

                    add_trade_to_hist(date=data_final_venda,
                                        entry=buy_price,
                                        out=sell_price,
                                        profit=profit,
                                        ganhos=ganhos)

                    
                    open_position = False

                    change_open_position_in_st()

                if LR_SAIDA and VOL_TEST_SAIDA:
                    break
                
                time.sleep(5)

if __name__ == '__main__':
    path_api = r'C:\Users\mateu\workspace\api_binance.txt'
    x, y = get_secret_and_key(path_api)
    client = init_client(x, y)

    slope_vol_strat(ticker='', quant=0, client=client)