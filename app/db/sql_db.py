
import os
from dotenv import load_dotenv
import pyodbc
import json



load_dotenv()
# Define your MS SQL connection string
server =   os.getenv("SQL_SERVER"); 
database = os.getenv("SQL_DATABASE"); 
username = os.getenv("SQL_USERNAME"); 
password = os.getenv("SQL_PASSWORD"); 


system_server =   os.getenv("SYSTEM_SQL_SERVER"); 
system_database = os.getenv("SYSTEM_SQL_DATABASE"); 
system_username = os.getenv("SYSTEM_SQL_USERNAME"); 
system_password = os.getenv("SYSTEM_SQL_PASSWORD"); 


# conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
#                       f'SERVER={server};'
#                       f'DATABASE={database};'
#                       f'UID={username};'
#                       f'PWD={password}')





def execute_query(query):
    query = query.replace("`", "")
    query = query.replace("sql", "")
    cursor = conn.cursor()
    print(query)
    cursor.execute(query)
    results = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    results_with_columns = [dict(zip(column_names, row)) for row in results]
     
    # Prepare the results to send to ChatGPT
    formatted_results = "\n".join([str(row) for row in results])
    column_names = [desc[0] for desc in cursor.description]

    # Format results with column names
    formatted_results = [dict(zip(column_names, row)) for row in results]
    return formatted_results  # Returns a list of dictionaries (JSON-like format)



def insert_chat_log(data):
    """ Inserts a record into the chat_bot_log table using the stored procedure. """
    try:
        # Establish database connection
        sys_conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                      f'SERVER={system_server};'
                      f'DATABASE={system_database};'
                      f'UID={system_username};'
                      f'PWD={system_password}')
        
        cursor = sys_conn.cursor()

        # data = json.loads(json_data)

        user_code = data.get("user_code")
        chat_history_code = data.get("chat_history_code")
        question_asked = data.get("question_asked")
        related_context_retrieved = data.get("related_context_retrieved")
        sql_query = data.get("sql_query")

        # Ensure required fields are present
        if not all([user_code, chat_history_code, question_asked, related_context_retrieved, sql_query]):
            raise ValueError("Missing required fields in JSON data")

        # Execute stored procedure
        cursor.execute("EXEC InsertChatBotLog ?, ?, ?, ?, ?", 
                       user_code, chat_history_code, question_asked, related_context_retrieved, sql_query)

        # Commit the transaction
        sys_conn.commit()
        print("Record inserted successfully!")

    except Exception as e:
        print(f"Error inserting record: {e}")

    finally:
        # Close connection
        if cursor:
            cursor.close()
        if sys_conn:
            sys_conn.close()