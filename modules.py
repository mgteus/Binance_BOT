from binance import Client



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

    return


if __name__ == '__main__':
    pass