from binance import Client
import pandas as pd 

from modules import get_secret_and_key, init_client




if __name__ == '__main__':
    path_api = r'C:\Users\mateu\workspace\api_binance.txt'
    x, y = get_secret_and_key(path_api)
    init_client(x, y, balance=True)