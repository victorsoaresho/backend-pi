import mysql.connector
from mysql.connector import Error
from fastapi import FastAPI
import uvicorn

class Procedimentos:
    host = 'mysqltrabalho.mysql.database.azure.com'
    database = 'pi'
    user = 'arthur'
    password = '741258ar@'
    port = 3306

    @classmethod
    def conectar(cls):
        try:
            cnx = mysql.connector.connect(
                user=cls.user,
                password=cls.password,
                host=cls.host,
                port=cls.port,
                database=cls.database,
                ssl_disabled=False  # Não desabilitar SSL
            )
            if cnx.is_connected():
                print("Conexão bem-sucedida!")
            return cnx
        except Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            return None

    @classmethod
    def consulta(cls, query: str, params=None):
        cnx = cls.conectar()
        if cnx:
            try:
                cursor = cnx.cursor()
                cursor.execute(query, params)
                record = cursor.fetchall()
                cnx.close()  # Fechar a conexão após a consulta
                return record
            except Error as e:
                print(f"Erro ao executar a consulta: {e}")
                return None
        else:
            print("Não foi possível estabelecer a conexão.")
            return None

    @classmethod
    def insert_return_id(cls, query: str, params=None):
        cnx = cls.conectar()
        if cnx:
            try:
                cursor = cnx.cursor()
                cursor.execute(query, params)
                cnx.commit()
                last_id = cursor.lastrowid
                cnx.close()  # Fechar a conexão após a operação
                return last_id
            except Error as e:
                print(f"Erro ao executar a inserção: {e}")
                return None
        else:
            print("Não foi possível estabelecer a conexão.")
            return None

    @classmethod
    def init(app):
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
