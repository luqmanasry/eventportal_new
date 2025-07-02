import os

class Config:
    SECRET_KEY = 'your-secret-key'

    SQLALCHEMY_DATABASE_URI = os.environ.get('AZURE_SQL_CONNECTIONSTRING') or \
        'mssql+pytds://Admin1:Luqman123@eventhorizondatabase-sql.database.windows.net/eventhorizonDB?charset=utf8'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
