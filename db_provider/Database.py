import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Credenciales DataBase
load_dotenv()
user_name = os.getenv('USER_NAME')
user_password = os.getenv('USER_PASSWORD')
host_name = os.getenv('HOST_NAME')
db_name = os.getenv('DB_NAME')


class Database:

    __instance = None
    __connection = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Database, cls).__new__(cls)
        return cls.__instance


    def get_connect(self):
        if self.__connection is None or not self.__connection.is_connected():
            try:
                self.__connection = mysql.connector.connect(host=host_name,
                                                            user=user_name,
                                                            password=user_password,
                                                            database=db_name)
                if self.__connection or self.__connection.is_connected():
                    print("Conexión exitosa a la base de datos MySQL")
            except Error as e:
                print(f"Error al conectar a la base de datos MySQL: {e}")
                self.__connection = None
        return self.__connection


    #Cierra la conexión a la base de datos MySQL.
    def disconnect(self):
        if self.__connection and self.__connection.is_connected():
            self.__connection.close()
            print("Conexión cerrada.")
