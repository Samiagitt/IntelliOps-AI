import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

class DatabaseUtil:

    def __init__(self, db_config):
        self.db_config = db_config

        try: 
            self.connection = psycopg2.connect(**db_config) 

        except Exception as e:
            print(f"Error connecting to the database: {e}")
            self.connection = None
    def get_connection(self):
        return psycopg2.connect(**self.db_config)

    def schema_details(self,schema_name):

        schema_info_context = ""
        #Separate connections: Reliability
        connection = self.get_connection()   
        #If schema_details() closes a connection, execute_sql() cannot reuse it. 
        #Creating a new connection for each operation prevents this problem.
        cursor = connection.cursor()

        schema_info_context = f"Database Schema: {schema_name}\n"

        try: 

            cursor.execute("SELECT table_name from information_schema.tables where table_schema = %s;", (schema_name,))
            tables_list = cursor.fetchall()

            for table in tables_list:
                table_name = table[0]
                schema_info_context = f"{schema_info_context}\nTable: {table_name}\n"

                # Adding Columns & Data Types
                cursor.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = %s AND table_name = %s;""", (schema_name, table_name))
                columns_list = cursor.fetchall()

                for column in columns_list:
                    column_name = column[0]
                    data_type = column[1]
                    schema_info_context = f"{schema_info_context}  Column: {column_name}, Data Type: {data_type}\n"

                # Adding Sample Data
                cursor.execute(f"SELECT * FROM {schema_name}.{table_name} LIMIT 5;")
                sample_data = cursor.fetchall()
                schema_info_context = f"{schema_info_context}  Sample Data:\n"
                for row in sample_data:
                    schema_info_context = f"{schema_info_context}    {row}\n"

        except Exception as e:
            print(f"Error fetching schema details: {e}")
            schema_info_context = f"Error fetching schema details: {e}"

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        
        return schema_info_context

    def execute_sql(self, query):
        connection = None
        cursor = None

        try:
            connection = self.get_connection()
            connection.set_session(readonly=True) #initial data protection
            #Our AI agent will generate SQL queries. We want it to retrieve data without accidentally modifying the database.

            cursor = connection.cursor()
            cursor.execute("SET LOCAL search_path TO intelliops") #Simplifies SQL queries and schema selection.
            #SET LOCAL applies only to the current transaction.
            cursor.execute(query)

            result = cursor.fetchall()
            return str(result)

        except Exception as e:
            print(f"Error executing query: {e}")
            return None

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


obj = DatabaseUtil({
    "host": os.environ["host"],
    "port": int(os.environ["port"]),
    "user": os.environ["user"],
    "password": os.environ["password"],
    "dbname": os.environ["database"],
    "sslmode": "require"
})

result = obj.execute_sql(
    "SELECT COUNT(*) FROM intelliops.users;"
)

print("Total users:", result)