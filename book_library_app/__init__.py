from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
import pymysql  # uzywamy do połaczenia sie z serwerem MySQL
from flask_migrate import Migrate



app = Flask(__name__)
app.config.from_object(Config)    # aplikacja wczytuje dane z klasy Config z pliku config.py
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# results = db.session.execute('show databases')  # testujemy połaczenie do serwera MySQL (zwraca obiekt RESULT PROXY)
# for row in results:  # iterujemy po obiekcie results zeby wyciagnac z niego dane
#     print(row)


from book_library_app import authors    # importujemy to ponizej ap poniewaz w authors.py kozystamy z instancji app
from book_library_app import models
from book_library_app import db_manage_commands
from book_library_app import errors
from book_library_app import utils

