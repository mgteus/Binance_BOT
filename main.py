from binance import Client
from binance.exceptions import BinanceAPIException
import pandas as pd 
import ta as ta
import os
import math

from modules import get_secret_and_key, init_client, get_minutedata



def MACD_strat(ticker: str='', quant: float = 0, open_position: bool=False, client: Client=''):
    """
    Funcao da estrategia de MACD
    """
    new_quant, buy_price = 0, 0 
    while True:
        df = get_minutedata(ticker=ticker, client=client)

        if not open_position:
            if ta.trend.macd_diff(df['Close']).iloc[-1] > 0 and ta.trend.macd_diff(df['Close']).iloc[-2] < 0:
                new_quant = float(str(15/df['Close'].iloc[-1])[:10])
                ordem = client.create_order(ticker, 'BUY', 'MARKET', new_quant)
                print(f"COMPRA = {ordem}")
                buy_price = float(ordem['fills'][0]['price'])
                open_position = True
                
                break

        if open_position:

            while True:
                df = get_minutedata(ticker=ticker, client=client)
                if ta.trend.macd_diff(df['Close']).iloc[-1] < 0 and ta.trend.macd_diff(df['Close']).iloc[-2] > 0:
                    ordem = client.create_order(ticker, 'SELL', 'MARKET', new_quant)
                    sell_price = float(ordem['fills'][0]['price'])
                    print(f"VENDA = {ordem}")
                    print(f"ganhos = {(sell_price-buy_price)}")
                    print(f"profit = {(sell_price-buy_price)/buy_price}")
                    break


            


if __name__ == '__main__':
    path_api = r'C:\Users\mateu\workspace\api_binance.txt'
    x, y = get_secret_and_key(path_api)
    client = init_client(x, y)
    df = get_minutedata('BTCBUSD', client)
    print(df)
    #MACD_strat(ticker='', quant=0, client=client)