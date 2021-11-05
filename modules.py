from operator import truth
from binance import Client
from binance.exceptions import BinanceAPIException
import pandas as pd
import time
import math





def get_secret_and_key(path: str='') -> str and str:
    """
    Funcao simples que le a primeira linha de um txt do path e splita na virgula
    devolvendo a api key e api secret.
    """
    try:
        with open(path, 'r') as file:  # lendo as infos da api
            line = file.read()
            api_key, api_secret = line.split(',')
        return api_key, api_secret

    except Exception as e:
        print(e)
        return '', ''
        
def init_client(key: str = '', secret: str = '', balance: bool = False) -> bool:
    """
    Funcao que inicia o client da binance dado pela key e secret.
    Retorna True caso o cliente funcione
    """

    client = Client(api_key=key, api_secret=secret)

    if balance:
        for cur in client.get_account()['balances']:
            if float(cur['free']) > 0:
                print(cur['asset'], cur['free'])

    return client


def add_log(path: str = '', order_buy: dict = {}, order_sell: dict = {}) -> None:
    """ 
    Funcao que adiciona o resultado de uma ordem de compra e a ordem de venda ao arquivo no path
    """
    
    #if order_buy != {} and order_sell != {}:
    ticker     = 4#float(order_buy['symbol'])
    price_buy  = 3#float(order_buy['fills'][0]['price'])
    buy_tax    = 1#float(order_buy['fills'][0]['price'])*.99
    price_sell = 2#float(order_sell['fills'][0]['price'])
    sell_tax   = 4#float(order_sell['fills'][0]['price'])*.99
    percent    = 4#((price_sell-sell_tax) - (price_buy+buy_tax))/price_buy
    profit_usd = round(price_sell - price_buy - buy_tax - sell_tax, 2)

    log_dict = {'TICKER': [ticker],
                'P-COMPRA': [price_buy],
                'TAXA-CMP': [buy_tax],
                'P-VENDA': [price_sell],
                'TAXA-VND': [sell_tax],
                'PROFIT': [percent],
                'GAIN (USD)' : [profit_usd]}

    df = pd.DataFrame.from_dict(log_dict)
    print(df)


def get_minutedata(ticker: str = '', client: Client=''):

    if client != '':
        try:
            df = pd.DataFrame(client.get_historical_klines(ticker,
                                                        Client.KLINE_INTERVAL_5MINUTE,
                                                        '200m UTC'))
        except BinanceAPIException as error:
            print(error)
            time.sleep(60)
            df = pd.DataFrame(client.get_historical_klines(ticker,
                                                        Client.KLINE_INTERVAL_5MINUTE,
                                                        '200m UTC'))
        df = df.iloc[:,:6]
        df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        df.set_index('Time', inplace=True)
        df.index = pd.to_datetime(df.index, unit='ms')
        df = df.astype(float)

        return df
    
    return None



if __name__ == '__main__':

    client = init_client('b1ttKpCMSUrWZkGlwTjzyf5EPm13GzYNs4lyVDizgn0ixxRhhqEXvRHW1REVYwBI',
                'jUm5R1lugi2h0ujhQJTZVfdUu5VdZnAc1odW4ypsLBL2YCQRsOdkitw4wgpvEGEc')
    # coins_dict = {'TICKER':[], 'QNT':[]}
    # coins_dict_for_price = {}
    # for cur in client.get_account()['balances']:
    #     if float(cur['free']) > 0:
    #         coins_dict['TICKER'].append(cur['asset'])
    #         coins_dict['QNT'].append(cur['free'])
    #         coins_dict_for_price[cur['asset']]=cur['free']
    # print(coins_dict)
    # print(coins_dict_for_price)
    # for corr in client.get_all_tickers():
    #     if corr['symbol'].replace('BUSD', '') in coins_dict['TICKER']:
    #         print(corr)
    #         print(round(float(coins_dict_for_price[corr['symbol'].replace('BUSD', '')])*float(corr['price']),2))
        

    # df = get_minutedata('BTCBUSD', client)
    # print(df)
    