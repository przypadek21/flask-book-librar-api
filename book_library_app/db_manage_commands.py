# wczytuje dane z pliku authors.json i wgrywa je do tabeli authors
# skrypt dostarczony przez pakiet flask został utworzony przy pomocy modulu click.
# CLICK umozliwa tworzenie skryptów konsolowych

import json
from pathlib import Path  # klasa path umozliwa nam wyviagniecie sciezki do pliku authors.json
from datetime import datetime
from book_library_app import app, db
from book_library_app.models import Author    # importujemy z pliku models klase Authors


@app.cli.group() # tworzymy grupe w skypcie flask
def db_manage():
    """Database management commands"""
    pass


@db_manage.command()
def add_data():    # komenda add_data znajduje sie w grupie komend db_manage
    """Add sample data to database"""
    try:
        authors_path = Path(__file__).parent / 'samples' / 'authors.json'  # pobieramy sciezke do pliku authors.json
        with open(authors_path) as file:  # context menagerem pobieramy dane znajdujace sie w tym pliku
            data_json = json.load(file)  # wczytujemy dane z pliku
        for item in data_json:  # iterujemy po tyhc danych
            item['birth_date'] = datetime.strptime(item['birth_date'], '%d-%m-%Y').date()
            author = Author(**item)  # ** powoduje wypakowanie obiektu item
            db.session.add(
                author)  # wypakowany obiekt mozemy dodac do sesji db, ktory nastepnie zostanie wprowadzony do bazy danych
        db.session.commit()  # commitujemy te zmiany
        print('Data has been successfully added.')
    except Exception as exc:
        print("Unexpected error: {}".format(exc))



@db_manage.command()
def remove_data():
    """Remove all data from database"""
    try:
        db.session.execute('TRUNCATE TABLE authors')    # usuwamy wszystkie dane z tabeli oraz resetuje klucz podstawowy
        db.session.commit()  # commitujemy te zmiany
        print('Data has been successfully removed.')
    except Exception as exc:
        print("Unexpected error: {}".format(exc))