import sqlite3

#------------------------------------------------------------------------------
# funcoes para o banco de dados 
conn = sqlite3.connect('data.db')
c = conn.cursor()
def create_usertable(): 
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    """
    Funcao para criar o banco de dados para logins/senhas
    """
    c.execute("CREATE TABLE IF NOT EXISTS usertable(username TEXT, password TEXT, api TEXT, secret TEXT)")
    c.close()
    return

def add_userdata(username: str = '', password: str='', api_key: str='', secret: str=''): 
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    """
    Funcao que adiciona um usuario novo ao banco de dados
    """
    c.execute(f"INSERT INTO usertable(username, password, api, secret) VALUES ({username},{password},{api_key},{secret})")
    conn.commit()
    c.close()
    return 

def login_user(username: str = '', password: str =''):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    """
    Funcao que faz o login do usuario
    """
    c.execute("SELECT * FROM usertable WHERE username=? AND password = ? WHERE type = 'table'", (username, password))
    data = c.fetchall()
    c.close()
    return data

def view_all_users():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()   
    """
    Funcao que mostra todos os usuarios inscritos no banco de dados
    """
    c.execute("SELECT * FROM usertable WHERE type = 'table'")
    data = c.fetchall()
    c.close()
    return data 
#------------------------------------------------------------------------------
