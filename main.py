from binance import Client
from binance.exceptions import BinanceAPIException
import pandas as pd 
import numpy as np
import ta as ta
import os
import math
import ccxt
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


def slope_vol_strat(ticker: str='', quant: float = 0, open_position: bool=False, client: Client=''):
    """ 
    Funcao de trade com a estrategia de volume e estrategia de slope para 8 e 21 dias
    """     
    new_quant, buy_price, orders = 0, 0, 0
    while True:
        df = get_minutedata(ticker=ticker, client=client)

        if not open_position:

            VOL_TEST = df['Volume'].iloc[-1] > np.mean(df['Volume'].iloc[-21:-1])

            y_lr = list(df['Close'].dropna())
            x_lr = [f for f in range(len(y_lr))]
            lr_8 = get_slope(x_lr, y_lr, 8)
            lr_21 = get_slope(x_lr, y_lr, 21)

            LR = lr_21 > 0 and lr_8 > 0

            if LR and VOL_TEST:
                
                new_quant = get_ticker_infos(ticker=ticker, client=client, quant=quant)
                 
                ordem = client.order_market_buy(symbol=ticker, quantity=new_quant)

                print(f"COMPRA = {ordem}")
                buy_price = float(ordem['fills'][0]['price'])
                open_position = True
                usd_ = round(new_quant*buy_price,2)
                print(f"COMPREI {new_quant} {ticker} ({usd_} USD)")
                

        if open_position:

            while True:
                df = get_minutedata(ticker=ticker, client=client)


                y_lr = list(df['Close'].dropna())
                x_lr = [f for f in range(len(y_lr))]
                # 8 tempos
                lr_8_saida = get_slope(x_lr, y_lr, 8)

                
                lr_21_saida = get_slope(x_lr, y_lr, 21)
                #print(f"lr_8_saida={lr_8_saida}")


                # TESTE VOLUME SAIDA
                VOL_TEST_SAIDA = df['Volume'].iloc[-1] > np.mean(df['Volume'].iloc[-21:-1])

                # decisao de saída 
                LR_SAIDA = lr_8_saida < 0 and lr_21_saida < 0
                if LR_SAIDA and VOL_TEST_SAIDA:
                    ordem = client.order_market_sell(symbol=ticker, quantity=new_quant)
                    sell_price = float(ordem['fills'][0]['price'])

                    usd_venda = round(new_quant*sell_price, 2)
                    print(f'VENDI {new_quant} {ticker} ({usd_venda} USD)')
                    print(f"ganhos = {(sell_price-buy_price)*new_quant}")
                    print(f"profit = {(sell_price-buy_price)/buy_price}")
                    
                    open_position = False

                    break



if __name__ == '__main__':
    path_api = r'C:\Users\mateu\workspace\api_binance.txt'
    x, y = get_secret_and_key(path_api)
    client = init_client(x, y)

    slope_vol_strat(ticker='', quant=0, client=client)