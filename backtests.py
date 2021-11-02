import yfinance as yf
import numpy as np 
from binance import Client
import ta as ta
from binance.exceptions import BinanceAPIException
import pandas as pd
import time
import math

import matplotlib.pyplot as plt

for x in [5]: 
    data = yf.download(tickers='LTC-USD', 
                    period = f'{7*x}d',
                    interval = f"{x}m",
                    threads = True)
    data.reset_index(drop=False, inplace=True)

    # grafico de analise dos indicadores 
    # plt.figure()
    # plt.subplot(211)
    # plt.plot(data['Close'])

    # plt.subplot(212)
    # plt.plot(ta.volume.force_index(data['Close'], data['Volume']))
    # plt.show()

    order_position = False
    ordem = 1
    ganhos = []
    for i in range(data.shape[0]):

        if not order_position:
            df = data.iloc[0+i:80+i]
            df.reset_index(drop=True, inplace=True)
            #print(f"----------{i}----------------------")
            #print(f"-1 = {ta.trend.macd_diff(df['Close']).iloc[-1]}", ta.trend.macd_diff(df['Close']).iloc[-1] > 0)
            #print(f"-2 = {ta.trend.macd_diff(df['Close']).iloc[-2]}", ta.trend.macd_diff(df['Close']).iloc[-2] < 0)
            #print(f"----------{i}----------------------")

            #--------------------- indicadores entrada ------------------------


            #macd_hist = df['Close'].hist().mean() > 0 
            macd_line = ta.trend.macd_diff(df['Close'])
            macd_line = macd_line.iloc[-1] > 0 and macd_line.iloc[-2] < 0
            MACD = macd_line



            # aroon_up = ta.trend.aroon_up(df['Close']).iloc[-1]
            # aroon_down = ta.trend.aroon_down(df['Close']).iloc[-1]
            # AROON = aroon_up > aroon_down and aroon_up > 70


            #adx = ta.trend.adx(df['High'], df['Low'], df['Close']).iloc[-1]
            #ADX = adx > 25
            
            # fi = ta.volume.force_index(df['Close'], df['Volume'])
            # fi = fi.iloc[-1] > fi.mean()


            # FORCE_INDEX = fi



            trix = ta.trend.trix(df['Close'], window=7).iloc[-1]  
            TRIX = trix < 0


            # decisao de compra
            if TRIX and MACD:
                #print("Comprei")
                buy_price = df['Close'].iloc[-1]
                order_position = True
                continue
            else:
                pass
        if order_position:
            df = data.iloc[0+i:80+i]
            df.reset_index(drop=True, inplace=True)


            #------------------- indicadores saida ----------------------------
            # aroon_up = ta.trend.aroon_up(df['Close']).iloc[-1]
            # aroon_down = ta.trend.aroon_down(df['Close']).iloc[-1]
            # AROON = aroon_down > aroon_up and aroon_down > 70
            macd_line = ta.trend.macd_diff(df['Close'])
            MACD = macd_line.iloc[-1] < 0 and macd_line.iloc[-2] > 0
            

            trix = ta.trend.trix(df['Close']).iloc[-1]  
            
            TRIX = trix > 0

            # decisao de saída 
            if MACD and TRIX:
                sell_price = df['Close'].iloc[-1]

                #print(f"COMPRA E VENDA {ordem} FINALIZADA")
                ordem += 1
                #print(f"profit = {(sell_price-buy_price)/buy_price}")
                ganhos.append((sell_price-buy_price)/buy_price)
                order_position = False
                    
            else:
                pass


    if len(ganhos) > 0:
        plt.plot(ganhos, lw=3, label=f"% de ganho")
        plt.title(f'Gráfico dos ganhos para intervalos de {x}min')
        plt.plot(np.array(ganhos).cumsum(), c='k', ls='--', 
                    label=f"SomaCum = {round(np.array(ganhos).cumsum()[-1],3)}%")
        plt.legend()
        plt.show()

        plt.hist(ganhos)
        plt.vlines(x=np.array(ganhos).mean(), ls='--', lw=2, ymax=0, ymin=202,
                        label=f'{round(np.array(ganhos).mean(), 5)}', colors='k')
        plt.title(f"Histograma de {ordem} C|V Realizadas")
        plt.legend()
        plt.show()


if __name__ == '__main__':
    pass