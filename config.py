import os
from dotenv import load_dotenv # importujemy dotenv aby pobrac dane zawarte w pliku .env, do tej funckji przekazujemy pełna sciezke pliku .env
from pathlib import Path    # pobieramy pełna sciezke pliku

base_dir = Path(__file__).resolve().parent    # zmienna base_dir przechowuje sciezke do folderu flask-book-library-api
# __file__ to nazwa pliku czyli config.poy
# resolve daje nam pełną sciezkę do tego pliku, parent zawraca nam folder w którym znajduje sie plik __file__(config.py)

env_file = base_dir / '.env'   # przechowuje pełna sciezke pliku .env
load_dotenv(env_file)    # ładuje nam ustawienia z pliku przekazengo w argumencie


class Config:    # klasa przechowująca ustawienia aplikacji, wartosci przechowujemy w atrybutach
    PER_PAGE = 5
    SECRET_KEY = os.environ.get('SECRET_KEY')    # moduł os wyciaga zmienna srodowiskowa SECRET_KEY
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False