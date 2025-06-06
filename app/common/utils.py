import os
from fastapi import HTTPException, Request
import jwt
import pyodbc
from dotenv import load_dotenv
from typing import Dict, Any, List
import datetime

load_dotenv()

system_sql_odbc_driver = os.getenv("SYSTEM_SQL_DRIVER");
system_server =   os.getenv("SYSTEM_SQL_SERVER"); 
system_database = os.getenv("SYSTEM_SQL_DATABASE"); 
system_username = os.getenv("SYSTEM_SQL_USERNAME"); 
system_password = os.getenv("SYSTEM_SQL_PASSWORD"); 

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXP_DELTA_SECONDS = int(os.getenv("JWT_EXP_DELTA_SECONDS")) # 1 hour expiration

def allow_anonymous(route_func):
    route_func.allow_anonymous = True
    return route_func

def get_db_connection():
    return pyodbc.connect(f'DRIVER={system_sql_odbc_driver};' f'SERVER={system_server};' f'DATABASE={system_database};' f'UID={system_username};' f'PWD={system_password}');

def call_stored_procedure(sp_name: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection();
    cursor = conn.cursor()
    params = params or {}
    results = [];

    param_placeholders = ', '.join(f"@{k} = ?" for k in params.keys())
    exec_str = f"EXEC {sp_name} {param_placeholders}" if params else f"EXEC {sp_name}"

    cursor.execute(exec_str, list(params.values()))

    try:
        columns = [col[0] for col in cursor.description]  # Get column names
        rows = cursor.fetchall()
        results = [dict(zip(columns, row)) for row in rows]  # Map columns to values
    except pyodbc.ProgrammingError as e:
        raise e;
    cursor.close()
    return results


def get_sql_server_driver():
    drivers = [driver for driver in pyodbc.drivers() if 'SQL Server' in driver]
    # Prioritize newer drivers first
    for preferred_driver in ['ODBC Driver 18 for SQL Server',
                             'ODBC Driver 17 for SQL Server',
                             'ODBC Driver 13 for SQL Server',
                             'SQL Server Native Client 11.0',
                             'SQL Server']:
        for driver in drivers:
            if preferred_driver == driver:
                return driver
    if drivers:
        return drivers[0]
    else:
        raise Exception("No suitable SQL Server ODBC driver found on system.")

def convert_datetime(obj):
    if isinstance(obj, dict):
        return {k: convert_datetime(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetime(i) for i in obj]
    elif isinstance(obj, datetime.datetime):
        return int(obj.timestamp())
    else:
        return obj

def _token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")
    
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload  # you can return specific values too like payload["user_code"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")