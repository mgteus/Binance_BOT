from operator import truth
from binance import Client
from binance.exceptions import BinanceAPIException
import pandas as pd
import time





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


def get_minutedata(ticker: str = '', client: Client=''):

    if client != '':
        try:
            df = pd.DataFrame(client.get_historical_klines(ticker,
                                                        Client.KLINE_INTERVAL_1MINUTE,
                                                        '40m UTC'))
        except BinanceAPIException as error:
            print(error)
            time.sleep(60)
            df = pd.DataFrame(client.get_historical_klines(ticker,
                                                        Client.KLINE_INTERVAL_1MINUTE,
                                                        '40m UTC'))
        df = df.iloc[:,:6]
        df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        df.set_index('Time', inplace=True)
        df.index = pd.to_datetime(df.index, unit='ms')
        df = df.astype(float)

        return df
    
    return None


    

if __name__ == '__main__':
    pass