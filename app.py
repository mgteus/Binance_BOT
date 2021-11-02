import streamlit as st
import sqlite3



# funcoes para o banco de dados 
conn = sqlite3.connect('data.db')
c = conn.cursor()
def create_usertable(): 
    """
    Funcao para criar o banco de dados para logins/senhas
    """
    c.execute('CREATE TABLE IF NOT EXISTS usertable(username TEXT, password TEXT)')

    return
def add_userdata(username: str = '', password: str=''): 
    """
    Funcao que adiciona um usuario novo ao banco de dados
    """
    try: 
        c.execute('INSERT INTO usertable(username, password) VALUES (?,?)', (username, password))
        conn.commit()
        return 0
    except: 
        return None
def login_user(username: str = '', password: str =''):
    """
    Funcao que faz o login do usuario
    """
    c.execute('SELECT * FROM usertable WHERE username=? AND password = ?', (username, password))
    data = c.fetchall()
    return data
def view_all_users():
    """
    Funcao que mostra todos os usuarios inscritos no banco de dados
    """
    c.execute('SELECT * FROM usertable')
    data = c.fetchall()
    return data 
#------------------------------------------------------------------------------



def main():
    """
    Funcao principal do app
    """
    st.title('BOT_Binance')
    menu = ['Login', 'Perfil']

    aba = st.sidebar.selectbox('Menu', menu)

    if aba == 'Login':
        st.subheader('Login Page')
        login = st.checkbox('Login')

        if login: 
            aba = 'Perfil'

    elif aba == 'Perfil': 
        st.subheader('Perfil page')



    






if __name__ == '__main__':
    main()

