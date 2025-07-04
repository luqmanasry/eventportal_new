import pyodbc

# Azure SQL connection info
server = 'eventhorizondatabase-sql.database.windows.net'
database = 'eventhorizonDB'
username = 'Admin1'
password = 'Luqman123'
driver = '{ODBC Driver 17 for SQL Server}'  # Must be installed

try:
    conn = pyodbc.connect(
        f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}'
    )
    cursor = conn.cursor()

    # Drop table if exists (optional for testing)
    # cursor.execute("DROP TABLE IF EXISTS users")

    # Create users table
    create_table_query = '''
    CREATE TABLE users (
        id INT PRIMARY KEY IDENTITY(1,1),
        username NVARCHAR(100) NOT NULL,
        email NVARCHAR(255) NOT NULL UNIQUE,
        password NVARCHAR(255) NOT NULL,
        role NVARCHAR(50) NOT NULL DEFAULT 'user',  -- 'user' or 'organizer'
        is_active BIT NOT NULL DEFAULT 1,
        created_at DATETIME DEFAULT GETDATE()
    );
    '''

    cursor.execute(create_table_query)
    conn.commit()
    print("? Table 'users' created successfully!")

except Exception as e:
    print("? Error:", e)

finally:
    cursor.close()
    conn.close()