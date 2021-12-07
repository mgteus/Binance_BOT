import yfinance as yf
import numpy as np 
from binance import Client
import ta as ta
from sklearn.linear_model import LinearRegression
from binance.exceptions import BinanceAPIException
import pandas as pd
import time
import math

np.seterr(divide='ignore', invalid='ignore')
import matplotlib.pyplot as plt



def get_slope(x, y, L):
    try:
        m, _ = np.polyfit(x[:L], y[:L], 1)
        #plt.plot(x[:L+1],y[:L+1])
        #plt.show()
        return m
    except:
        return 0 


def back():
    for x in [5, 15]: 
        start = '2021-10-08'
        end = '2021-12-06'
        ticker = 'BNB-USD' 
        data = yf.download(tickers=ticker, 
                        period = f'{4*x}d',
                        interval = f"{x}m",
                        threads = True,
                        start=start)

        # data = yf.download(tickers=ticker, 
        #                 interval = f"{x}d",
        #                 threads = True,
        #                 start=start, end=end)
        #print(data)
        data.reset_index(drop=False, inplace=True)
        
        #print(data)

        #grafico de analise dos indicadores 
        plt.figure()
        plt.subplot(211)
        plt.title(f"{ticker}")
        plt.plot(data['Datetime'], data['Close'])
        plt.xticks(rotation=45)
        plt.show()

        # plt.subplot(212)
        # plt.title('MACD_DIFF')
        # plt.plot(ta.trend.macd_diff(data['Close']))
        # plt.show()

        order_position = False
        ordem = 1
        ganhos = []
        lista_compras = {'DATA':[], 'CLOSE':[]}
        lista_vendas = {'DATA':[], 'CLOSE':[]}
        trix_on = True
        for i in range(data.shape[0]):

            if not order_position:
                
                df = data.iloc[0+i:56+i]
                
                df.reset_index(drop=True, inplace=True)

                #print(f"----------{i}----------------------")
                #print(f"-1 = {ta.trend.macd_diff(df['Close']).iloc[-1]}", ta.trend.macd_diff(df['Close']).iloc[-1] > 0)
                #print(f"-2 = {ta.trend.macd_diff(df['Close']).iloc[-2]}", ta.trend.macd_diff(df['Close']).iloc[-2] < 0)
                #print(f"----------{i}----------------------")

                #--------------------- indicadores entrada ------------------------


                #macd_hist = df['Close'].hist().mean() > 0 
                #macd_line = ta.trend.macd_diff(df['Close'])
                #macd_line = macd_line.iloc[-1] > 0 and macd_line.iloc[-2] < 0
                #MACD = macd_line


                # aroon_up = ta.trend.aroon_up(df['Close']).iloc[-1]
                # aroon_down = ta.trend.aroon_down(df['Close']).iloc[-1]
                # AROON = aroon_up > aroon_down and aroon_up > 70


                #adx = ta.trend.adx(df['High'], df['Low'], df['Close']).iloc[-1]
                #ADX = adx > 25
                
                # fi = ta.volume.force_index(df['Close'], df['Volume'])
                # fi = fi.iloc[-1] > fi.mean()


                # FORCE_INDEX = fi

                # trix = ta.trend.trix(df['Close'], window=8).iloc[-1]  
                # TRIX = trix > 0

                # if not TRIX:
                #     trix_on = True
                #TRIX = TRIX and trix_on

                VOL_TEST = df['Volume'].iloc[-1] > np.mean(df['Volume'].iloc[-21:-1])

                
                # teste LR
                #print(df['Close'])
                #testeNA = df['Close'].dropna()
                #print(testeNA)
                #print(len(df['Close'].dropna()))
                y_lr = list(df['Close'].dropna())
                x_lr = [f for f in range(len(y_lr))]
                # 8 tempos
                lr_8 = get_slope(x_lr, y_lr, 8)
                
                #print(f'lr_8={lr_8}')
                # 21 tempos
                lr_21 = get_slope(x_lr, y_lr, 21)
                #print(f"lr_21={lr_21}")
                # 55 tempos
                #lr_55 = get_slope(x_lr, y_lr, 55)
                #print(f"lr_55={lr_55}")


                LR = lr_21 > 0 and lr_8 > 0 # and lr_8 > 0 

                # decisao de compra
                if LR and VOL_TEST:
                    
                    #comprei!
                    lista_compras['DATA'].append(df[df.columns[0]].iloc[-1])
                    lista_compras['CLOSE'].append(df['Close'].iloc[-1])

                    
                    buy_price = df['Close'].iloc[-1]
                    order_position = True
                    continue
                else:
                    pass

            if order_position:
                df = data.iloc[0+i:56+i]
                df.reset_index(drop=True, inplace=True)


                #------------------- indicadores saida ----------------------------
                # aroon_up = ta.trend.aroon_up(df['Close']).iloc[-1]
                # aroon_down = ta.trend.aroon_down(df['Close']).iloc[-1]
                # AROON = aroon_down > aroon_up and aroon_down > 70

                # macd_line = ta.trend.macd_diff(df['Close'])
                # MACD = macd_line.iloc[-1] < 0 and macd_line.iloc[-2] > 0
                

                #TRIX = trix < 0
                # trix = ta.trend.trix(df['Close'], window=8).iloc[-1]
                # TRIX = trix < 0

                #lucro = df['Close'].iloc[-1]/buy_price

                #LUCRO = lucro > 1.1

                # if LUCRO:
                #     trix_on = False

                #VOL_TEST = df['Close'].iloc[-1] < np.mean(df['Volume'].iloc[-6:-1])



                # LR saida
                
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
                    # vendi !

                    lista_vendas['DATA'].append(df[df.columns[0]].iloc[-1])
                    lista_vendas['CLOSE'].append(df['Close'].iloc[-1])


                    sell_price = df['Close'].iloc[-1]

                    #print(f"COMPRA E VENDA {ordem} FINALIZADA")
                    ordem += 1
                    #print(f"profit = {(sell_price-buy_price)/buy_price}")
                    ganhos.append(((sell_price-buy_price)/buy_price)*100)
                    order_position = False
                        
                else:
                    pass 
            
        print(f'Terminei para {x}min')

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

            
            plt.figure()
            plt.subplot(211)
            plt.title(f"{x}m")
            plt.plot(data[df.columns[0]], data['Close'], lw=2, c= 'k')
            plt.plot(lista_compras['DATA'], lista_compras['CLOSE'], 'go-', lw=3)
            plt.plot(lista_vendas['DATA'], lista_vendas['CLOSE'] ,'ro-', lw=3)

            """
            TROCAR SIMBOLO DE COMPRA E VENDA NO GRAFICO COM O PLT.SCATTER
            """
            #plt.scatter(lista_compras['DATA'], lista_compras['CLOSE'], marker='go', lw=3)
            #plt.scatter(lista_vendas['DATA'], lista_vendas['CLOSE'] ,marker='ro', lw=3)





            """
            FAZER BOLINHAS DE ENTRADA COM COR DEPENDENDO DO MOTIVO DE ENTRADA
            FAZER BOLINHAS DE SAIDA COM COR DEPENDENDO DO MOTIVO DE SAIDA TBM
            """
            plt.subplot(212)
            plt.title(f"{x}m")
            plt.plot(ganhos, lw=3, label=f"% de ganho")
            #plt.title(f'Gráfico dos ganhos para intervalos de {x}min')
            plt.plot(np.array(ganhos).cumsum(), c='k', ls='--', 
                        label=f"SomaCum = {round(np.array(ganhos).cumsum()[-1],3)}%")
            plt.legend()
            plt.show()
    
    return 



def LR_test():
    ticker = 'BTC-USD' 
    data = yf.download(tickers=ticker, 
                    period = f'20d',
                    interval = f"5m",
                    threads = True)
    data.reset_index(drop=False, inplace=True)
    
    print(data['Close'].head())
    x = list(data['Datetime'])
    y = list(data['Close'])
    x = [j for j in range(len(x))]

    for lookback in [8, 21, 55]:
        m, b = np.polyfit(x[:lookback+1], y[:lookback+1], 1)
        plt.title(f'LR para {lookback}| m={m}')
        plt.plot(x, [m*i + b for i in x])

        plt.show()


    return 

if __name__ == '__main__':
    #lista_ = [x for x in range(55)]
    #for j in [8, 21, 55]:
        #print(lista_[:j], len(lista_[:j]))
    back()