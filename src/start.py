import os 

import camelot
import pandas as pd
import logging
from unidecode import unidecode
from config.rules.regras import rules_dict
from config.tools.postgres import RDSPostgresSQLManager
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

class PDFTableExtrator:

    def __init__(self, file_name, config):
        self.path = os.path.abspath(f"Project_pdf_csv/src/files/pdf/{config['name'].lower()}/{file_name}.pdf")
        self.csv_path = os.path.abspath(f"Project_pdf_csv/src/files/csv")
        self.file_name = file_name
        self.config = config

    def start(self):
        logging.info(f"Start pdf - {self.file_name}")

        header = self.get_table_data(self.config["header_table_areas"], self.config["header_columns"],self.config["header_fix"])
        main = self.get_table_data(self.config["table_areas"], self.config["columns"],self.config["fix"])
        small = self.get_table_data(self.config["small_table_areas"], self.config["small_columns"],self.config["small_fix"])

        main = self.add_infos(header, main)
        small = self.add_infos(header, small)

        main = self.sanitize_column_names(main)
        if self.config["small_sanitize"]:
            small = self.sanitize_column_names(small)

        logging.info(f"Saving csv - {self.file_name}")
        
        self.save_csv(main, self.file_name)
        self.save_csv(small, f"{self.file_name}_small")

        logging.info(f"Saving to DB - {self.file_name}")
        self.send_to_db(main, f"Corretagem_{self.config['name']}".lower())
        self.send_to_db(small, f"Corretagem_{self.config['name']}_small".lower())

        return {"main": main, "small": small}


    def get_table_data(self, t_area, t_columns, fix):
        tables = camelot.read_pdf(
            self.path,
            flavor=self.config["flavor"],
            table_areas=t_area,
            columns=t_columns,
            strip_text=self.config["strip_text"],
            page=self.config["pages"],
            password=self.config["password"],
            
        )
        
        table_content = [self.fix_header(page.df) if fix else page.df for page in tables]

        result = pd.concat(table_content, ignore_index=True) if len(table_content) > 1 else table_content[0]

        return result

    def save_csv(self, df, file_name):
        if not os.path.exists(self.csv_path):
            os.makedirs(self.local_path, exist_ok=True)
        path = os.path.join(self.csv_path, f"{file_name}.csv")
        df.to_csv(path, sep=";", index=False)

    def add_infos(self, header, content):
        infos = header.iloc[0]
        df = pd.DataFrame([infos.values] * len(content), columns=header.columns)
        content = pd.concat([content.reset_index(drop=True)], axis=1)
        content["Data de Inserção"] = pd.Timestamp("today").normalize()
        return content

    @staticmethod
    def fix_header(df):
        df.columns = df.iloc[0]
        df = df.drop(0)
        df = df.drop(df.columns[0], axis=1)
        return df

    def sanitize_column_names(self, df):
        df.columns = df.columns.map(lambda x: unidecode(x))
        df.columns = df.columns.str.replace(" ", "_")
        df.columns = df.columns.str.replace(r"\W", "", regex=True)
        df.columns = df.columns.str.lower()
        return df   

    @staticmethod
    def send_to_db(df, table_name):
        try:
            connection = RDSPostgresSQLManager().alchemy()
            df.to_sql(table_name, connection, if_exists="append", index=False)
            logging.info(f"Dados salvos no banco de dados {table_name}")
        except Exception as e:
            logging.error(e)


def list_files(folder):
    try:
        files = [os.path.splitext(f)[0] for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        return files
    except FileNotFoundError:
        logging.info(f"Pasta {folder} não encontrada")
        return []
    except Exception as e:
        logging.info("Erro ao listar arquivos")
        return []


if __name__ == "__main__":

    corretora = "redrex"
    path = os.path.abspath(f"Project_pdf_csv/src/files/pdf/{corretora}/")
    files = list_files(path)

    for file in files:
        extractor = PDFTableExtrator(file, config=rules_dict[corretora]).start()
        
    logging.info("Todos os arquivos foram processados")