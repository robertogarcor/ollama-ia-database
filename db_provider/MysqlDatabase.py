import json
from db_provider.IDatabaseDao import IDatabaseDao
from db_provider.Database import Database
from mysql.connector import Error


class MysqlDatabase(IDatabaseDao):

    __instance = None
    __connection = None
    __cursor = None
    __schema_file = ''

    def __init__(self):
        self.__instance = Database()
        self.__connection = self.__instance.get_connect()
        self.__cursor = self.__connection.cursor(dictionary=True)


    # Obtiene el esquema de la Base de Datos
    def get_schema(self) -> str:
        schema = {}
        try:
            with open(self.__schema_file, 'r') as file:
                schema = json.load(file)

        except FileNotFoundError:
            print(f"El archivo {self.__schema_file} no se encuentra.")
        except json.JSONDecodeError:
            print(f"Error al procesar el archivo JSON.")
        except Exception as e:
            print(f"Error al leer el archivo de esquema: {e}")

        return schema


    # Ejecuta la consulta query SQL
    def query(self, sql: str) -> list[dict] | None:
        try:
            self.__cursor.execute(sql)
            result = self.__cursor.fetchall()
            return result
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            return None
        finally:
            self.__connection = None
