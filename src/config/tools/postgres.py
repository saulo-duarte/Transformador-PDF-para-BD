import os
import psycopg2
from sqlalchemy import create_engine

class RDSPostgresSQLManager:
    def __init__(self, db_name=None, db_user=None, db_password=None, db_host=None, db_port="5432"):
        # Primeiro, verificamos se as variáveis de ambiente estão configuradas
        env_vars_configured = self.check_environment_variables()

        # Se as variáveis de ambiente não estiverem configuradas e nenhum argumento foi passado, levanta um erro
        if not env_vars_configured and (db_name is None or db_user is None or db_password is None or db_host is None):
            raise ValueError("As credenciais do banco de dados não foram fornecidas")
        
        # Utiliza as variáveis de ambiente como fallback caso não sejam passadas como argumentos
        self.db_name = db_name or os.getenv("DB_NAME")
        self.db_user = db_user or os.getenv("DB_USER")
        self.db_password = db_password or os.getenv("DB_PASSWORD")
        self.db_host = db_host or os.getenv("DB_HOST")
        self.db_port = db_port

    def connect(self):
        try:
            conn = psycopg2.connect(
                dbname=self.db_name,
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port,
            )
            print("Conexão com o banco de dados bem sucedida")
            return conn
        except Exception as e:
            print(f"Erro ao conectar com o banco de dados: {e}")
            return None

    def execute_query(self, query):
        try:
            connection = self.connect()
            if connection:
                cursor = connection.cursor()
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                connection.commit()
                connection.close()
                return result
            else:
                print("Não foi possível executar a query")
        except psycopg2.Error as e:
            print(f"Erro ao executar a query: {e}")
            return None

    @staticmethod
    def check_environment_variables():
        if (
            not os.getenv("DB_NAME")
            or not os.getenv("DB_USER")
            or not os.getenv("DB_PASSWORD")
            or not os.getenv("DB_HOST")
        ):
            print("Variáveis de ambiente não configuradas")
            return False
        else:
            print("Variáveis de ambiente configuradas")
            return True

    def alchemy(self):
        self.engine = create_engine(
            f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        )
        return self.engine
