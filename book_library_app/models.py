# model reprezentuje zasób "autorzy ksiażek", w tym pliku przechowujemy wszystkie utworzone modele

import re
from flask import request, url_for
from flask_sqlalchemy import BaseQuery
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.expression import BinaryExpression
from typing import Tuple
from book_library_app import db
from datetime import datetime
from marshmallow import Schema, fields, validate, validates, ValidationError


from book_library_app import Config


COMPARSION_OPERATORS_RE = re.compile(r'(.*)\[(gte|gt|lte|lt)\]')      # zmienna globalna, która kompiluje nasze wyrazenie regularne

class Author(db.Model):  # klasa Author() reprezentuje obiekt autorzy ksiazek, przekaując db.Model klasa Author
    # dziedziczy po klasie Model z instancji db
    __tablename__ = 'authors'  # nazwa tabeli
    id = db.Column(db.Integer, primary_key=True)  # kolumna,  w argumencie przekazujemy typ danych
    first_name = db.Column(db.String(50), nullable=False)  # 50 max liczba znaków, nullable czyli wartosc first_name
    # musi byc zawsze ustawiona i nie moze to byc null
    last_name = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)

    def __repr__(self):  # metoda zwraca tekstowa reprezentacje modelu
        return f'<{self.__class__.__name__}>:{self.first_name} {self.last_name}'
    # nie tworzymy tutaj __init__ poniewaz metoda ta jest niejawnie tworzona przez SQLAlchemy

    @staticmethod
    def get_schema_args(fields: str) -> dict:    # w zaleznoci od wysłanego zapytania HTTP dynamicznie tworzy argumenty
        # do klasy author_schema
        schema_args = {'many': True}
        if fields:      # sprawdzamy czy zmienna fields nie jest pustym obiektem
            schema_args['only'] = [field for field in fields.split(',') if field in Author.__table__.columns]
            # jesli znajduja sie tam wartosci to dodajemy dodatkowy klucz 'only'
            # aby wyciagnac odpowiednie klucze tego parametru uzywamy .split(',') i przekazujemy przecinek
        return schema_args

    @staticmethod
    def apply_order(query: BaseQuery, sort_keys: str) -> BaseQuery:
        if sort_keys:  # sprawdzamy czy sort_keys nie jest pusty
            for key in sort_keys.split(','):    # jesli znajduja sie dane w tym obiekie to beda oddzielone przecinkiem,
                # latego uzywamy split zeby wyodrebnic kazdy klucz
                desc = False  # budujemy query w zaleznosci od tego czy znak minus znajduje sie w obiekcie key
                if key.startswith('-'):
                    key = key[1:]
                    desc = True
                column_attr = getattr(Author, key, None)  # zamieniamy fukcja getattr() typ str na obiekt SQLalchemy
                # Author-nazwa modelu, key-nazwa atrybutu -> str, None zwracamy w przypadku gdy nie znajdujemy takiego klucza
                if column_attr is not None: # sprawdzamy czy zmienna column_attr nie jest None
                    query = query.order_by(column_attr.desc()) if desc else query.order_by(column_attr)
                    # dodajemy metode desc przy budowaniu obiektu query ktora
                    # bedzie sortowała dane malejąco , ale tylko wtedy gdy flaga desc bedzie True
                    # w innym przypdku dodajemy metode order by z całą nazwą kolumny w celu sortowania danych rosnąco
        return query

    @staticmethod
    def get_filter_argument(column_name: InstrumentedAttribute, value: str, operator: str)-> BinaryExpression:
        operator_mapping = {
            '==': column_name == value,
            'gte': column_name >= value,
            'gt': column_name > value,
            'lte': column_name <= value,
            'lt': column_name < value
        }
        return operator_mapping[operator]

    @staticmethod
    def apply_filter(query:BaseQuery) -> BaseQuery: # iterujemy po kazdym parametrze w adresie URL
        # i jezeli nazwa parametru odpowiada nazwie kolumny w tabeli authors to do metody filters w obiekcie query dodamy odpowiedni argument
        for param, value in request.args.items(): # metoda .items() pozwoli nam pobrac nazwe parametru URL oraz przypisana do niego wartosc
            if param not in {'fields', 'sort', 'page', 'limit'}:
                operator = '=='
                match = COMPARSION_OPERATORS_RE.match(param)
                if match is not None:
                    param, operator = match.groups()
                column_attr = getattr(Author, param, None)
                if column_attr is not None:
                    if param == 'birth_date':
                        try:
                            value = datetime.strptime(value, '%d-%m-%Y').date()
                        except ValueError:
                            continue
                    filter_argument = Author.get_filter_argument(column_attr, value, operator)
                    query = query.filter(filter_argument)
        return query

    @staticmethod
    def get_pagination(query: BaseQuery) -> Tuple[list, dict]:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', Config.PER_PAGE, type=int)
        params = {key: value for key, value in request.args.items() if key != 'page'}
        paginate_obj = query.paginate(page, limit, False)
        pagination = {
            'total_pages': paginate_obj.pages,
            'total_records': paginate_obj.total,
            'current_page': url_for('authors.get_authors', page=page, **params)
        }

        if paginate_obj.has_next:
            pagination['next_page'] = url_for('get_authors', page=page+1, **params)

        if paginate_obj.has_prev:
            pagination['prev_page'] = url_for('get_authors', page=page-1, **params)

        return paginate_obj.items, pagination



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
