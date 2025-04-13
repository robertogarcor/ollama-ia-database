import logging
import llm
from db_provider.MysqlDatabase import MysqlDatabase

logger = logging.getLogger(__name__)

def main() -> None:
    while True:
        question = input('User: ')
        if question.lower() == 'quit' or question.lower() == 'q':
            print('Adios!')
            break
        query_sql = llm.ask_to_sql(question)
        print(query_sql)
        try:
            mysql_db = MysqlDatabase()
            response_sql = mysql_db.query(query_sql)
            print(response_sql)
            response_ia = llm.result_sql_to_response(question, response_sql)
            print('Bot IA: ', response_ia)
        except Exception as e:
            error = f'Error occurred, {e}'
            logger.error(error)


if __name__ == '__main__':
    main()
