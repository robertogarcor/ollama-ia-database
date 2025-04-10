from abc import ABC, abstractmethod
from typing import Any


class IDatabaseDao(ABC):
    # Metodo abstracto para ejecutar consultas
    @abstractmethod
    def query(self, sql: str) -> list[dict]:
        pass

    # Metodo abstracto para obtener el esquema de la base de datos
    @abstractmethod
    def get_schema(self) -> str:
        pass


