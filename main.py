from binance import Client
from binance.exceptions import BinanceAPIException
import pandas as pd 
import ta as ta
import os
import math

from modules import get_secret_and_key, init_client, get_minutedata



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


            


if __name__ == '__main__':
    path_api = r'C:\Users\mateu\workspace\api_binance.txt'
    x, y = get_secret_and_key(path_api)
    client = init_client(x, y)
    df = get_minutedata('BTCBUSD', client)
    print(df)
    #MACD_strat(ticker='', quant=0, client=client)