import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=tcp:eventhorizondatabase-sql.database.windows.net,1433;"
    "DATABASE=eventhorizonDB;"
    "UID=Admin1;" 
    "PWD=Luqman123;" 
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

try:
    with pyodbc.connect(conn_str) as conn:
        print("✅ Connected successfully to Azure SQL Database.")
except Exception as e:
    print("❌ Failed to connect:", e)
