# model reprezentuje zasób "autorzy ksiażek", w tym pliku przechowujemy wszystkie utworzone modele

from book_library_app import db
from datetime import datetime
from marshmallow import Schema, fields, validate, validates, ValidationError



class Author(db.Model):  # klasa Author() reprezentuje obiekt autorzy ksiazek, przekaując db.Model klasa Author dziedziczy po klasie Model z instancji db
    __tablename__ = 'authors'  # nazwa tabeli
    id = db.Column(db.Integer, primary_key=True)  # kolumna,  w argumencie przekazujemy typ danych
    first_name = db.Column(db.String(50), nullable=False)  # 50 max liczba znaków, nullable czyli wartosc first_name musi byc zawsze ustawiona i nie moze to byc null
    last_name = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)

    def __repr__(self):  # metoda zwraca tekstowa reprezentacje modelu
        return f'<{self.__class__.__name__}>:{self.first_name} {self.last_name}'
    # nie tworzymy tutaj __init__ poniewaz metoda ta jest niejawnie tworzona przez SQLAlchemy


class AuthorSchema(Schema):    # klasa Schema, na podstawie tego schematu obiekty będą przekształcane na format JSON czyli dokonujemy "serializacji"
    # dodajemy atrybuty które bedą uzywane podczas serializacji
    id = fields.Integer(dump_only=True) # fields pochodzi z pakietu marshmallow, dump_only pomija ten argument podczas validacji
    first_name = fields.String(required=True, validate=validate.Length(max=50))    # przekazujemy zawsze w zapytaniu HTTP w metodzie POST, required waliduje nam przekazane dane, dzieki temu mamy pewnosc, że jesli którys atrybut zostanie pominiety dostaniemy bład validate ERROR
    last_name = fields.String(required=True, validate=validate.Length(max=50))    # przekazujemy zawsze w zapytaniu HTTP w metodzie POST, required waliduje nam przekazane dane, dzieki temu mamy pewnosc, że jesli którys atrybut zostanie pominiety dostaniemy bład validate ERROR
    birth_date = fields.Date('%d-%m-%Y', required=True)    # przekazujemy zawsze w zapytaniu HTTP w metodzie POST, required waliduje nam przekazane dane, dzieki temu mamy pewnosc, że jesli którys atrybut zostanie pominiety dostaniemy bład validate ERROR

    @validates('birth_date')     # dodajemy własna implementacje fukcji validującej
    def validate_birth_date(self, value):
        if value > datetime.now().date():
            raise ValidationError(f'Birth date must be lower than {datetime.now().date()}')

    # sprawdzamy czy przesłane dane sa w poprawnym schemacie


author_schema = AuthorSchema()
