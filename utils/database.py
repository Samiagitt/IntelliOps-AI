
import os
import psycopg2
from dotenv import load_dotenv
from decimal import Decimal
from datetime import date, datetime
from psycopg2 import sql

load_dotenv()


# Convert database-specific data types
def serialize_value(value):

    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, (date, datetime)):
        return value.isoformat()

    return value


class DatabaseUtil:

    def __init__(self, db_config):
        self.db_config = db_config

    # Create a separate connection for each operation
    def get_connection(self):
        return psycopg2.connect(**self.db_config)

    # Retrieve database schema information
    def schema_details(self, schema_name):

        connection = None
        cursor = None

        schema_info_context = f"Database Schema: {schema_name}\n"

        try:
            connection = self.get_connection()
            connection.set_session(readonly=True)
            cursor = connection.cursor()

            # Retrieve table names
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s;
            """, (schema_name,))

            tables_list = cursor.fetchall()

            for table in tables_list:

                table_name = table[0]

                schema_info_context += f"\nTable: {table_name}\n"

                # Retrieve columns and data types
                cursor.execute("""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_schema = %s
                    AND table_name = %s
                    ORDER BY ordinal_position;
                """, (schema_name, table_name))

                columns_list = cursor.fetchall()

                for column in columns_list:

                    column_name = column[0]
                    data_type = column[1]

                    schema_info_context += (
                        f"  Column: {column_name}, "
                        f"Data Type: {data_type}\n"
                    )

                # Retrieve sample data
                sample_query = sql.SQL(
                    "SELECT * FROM {}.{} LIMIT 5;"
                ).format(
                    sql.Identifier(schema_name),
                    sql.Identifier(table_name)
                )

                cursor.execute(sample_query)

                sample_data = cursor.fetchall()

                schema_info_context += "  Sample Data:\n"

                for row in sample_data:
                    schema_info_context += f"    {row}\n"

        except Exception as e:

            print(f"Error fetching schema details: {e}")
            schema_info_context = f"Error fetching schema details: {e}"

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

        return schema_info_context

    # Execute SQL and return structured data
    def execute_sql(self, query):

        connection = None
        cursor = None

        try:
            connection = self.get_connection()

            # Initial database protection
            connection.set_session(readonly=True)

            cursor = connection.cursor()

            cursor.execute(
                "SET LOCAL search_path TO intelliops"
            )

            cursor.execute(query)

            # Retrieve column names
            columns = [
                desc[0] for desc in cursor.description
            ]

            # Retrieve records
            rows = cursor.fetchall()

            # Prevent duplicate column names from losing data
            if len(columns) != len(set(columns)):
                raise ValueError(
                    "SQL result contains duplicate column names. "
                    "Use unique column aliases."
                )

            # Convert records into a list of dictionaries
            result = [
                {
                    column: serialize_value(value)
                    for column, value in zip(columns, row)
                }
                for row in rows
            ]

            return result

        except Exception as e:

            print(f"Error executing query: {e}")
            return None

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()


# ---------------- Test Database ----------------

if __name__ == "__main__":

    obj = DatabaseUtil({
        "host": os.environ["host"],
        "port": int(os.environ["port"]),
        "user": os.environ["user"],
        "password": os.environ["password"],
        "dbname": os.environ["database"],
        "sslmode": "require"
    })

    result = obj.execute_sql(
        "SELECT COUNT(*) AS total_users FROM intelliops.users;"
    )

    print("Total users:", result)
