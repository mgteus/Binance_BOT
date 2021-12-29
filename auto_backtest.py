import yfinance as yf
import numpy as np 
from binance import Client

from binance.exceptions import BinanceAPIException
import pandas as pd


import matplotlib.pyplot as plt



def auto_backtesting(weighted_indicator: dict = {},
                    configs: dict = {},
                    plot: bool= False) -> plt.figure:
    """
    Funcao que backtesta automaticamente dependendo de um dicionario com pesos
    para cada indicador disponível
    """

    # setar configuracoes inicias
    # intervalo
    # moeda 
    


    # dar um jeito de somar os resultados de cada indicador ate o valor X
    # tal que, resultados > X implicam em compra\venda

    # lista de indicadores disponiveis
    # MACD, AROON, ADX, FORCE_INDEX, TRIX, VOLUME
    # 
    # 
    #  

    return 



if __name__ == '__main__':
    wei_dct = {'MACD':0,
                'AROON':0,
                'ADX':0,
                'FORCE_INDEX':0,
                'TRIX':0,
                'VOLUME':0}

   #auto_backtesting(wei_dct)
