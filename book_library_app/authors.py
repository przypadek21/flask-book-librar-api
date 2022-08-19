from book_library_app import app, db
from webargs.flaskparser import use_args  # parsuje i sprawdza poprawnosc przesłanych danych w zapytaniu HTTP, łaczymy go z pakietem marshmallow w celu walidacji naszych danych
from flask import jsonify, request    # request wyciąga informacje z ciała zapytania HTTP
from book_library_app.models import Author, AuthorSchema, author_schema
from book_library_app.utils import validate_json_content_type


@app.route('/api/v1/authors', methods=['GET'])   # jesli pominiemy argument methods to Flask domyslnie ustawi methods na GET
def get_authors():
    authors = Author.query.all()   # trybut query zwraca nowy obiekt query, który udostępnia szereg metod: filtrowanie, srtowanie danych, all() zwraca wszystkie dostepne rekordy w tabeli Authors
    author_schema = AuthorSchema(many=True)    # many informuje pakiet marshmallow, że bedziemy przekazywac liste obiektów

    return jsonify({
        'success': True,
        'data': author_schema.dump(authors),    # w odpowiedzi serwera w kluczu 'data' przesyłamy liste obiektów w JSONie, dump przekształca obiekty w format JSON
        # jako argument przekazuje wyciagniete obiekty bazy danych
        'number_of_records' : len(authors)
    })


@app.route('/api/v1/authors/<int:author_id>', methods=['GET'])   # jesli pominiemy argument methods to Flask domyslnie ustawi methods na GET
def get_author(author_id: int):
    author = Author.query.get_or_404(author_id, description=f'Author id: {author_id} not found')    # get_or_404 wyciaga rekord na podstawie przekazanego klucza podstawowego, jak go nie odnajdzie to zwroci kod błedu 404
    return jsonify({
        'success': True,
        'data': author_schema.dump(author)
    })


@app.route('/api/v1/authors', methods=['POST'])   # jesli pominiemy argument methods to Flask domyslnie ustawi methods na GET
@validate_json_content_type
@use_args(author_schema, error_status_code=400)    # dekorator waliduje dane przesłane w zapytaniu HTTP z wykozystaniem klasy AuthorSchema i zwraca je w postaci słownika
def create_author(args: dict):
    author = Author(**args)

    db.session.add(author)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': author_schema.dump(author)
    }), 201


@app.route('/api/v1/authors/<int:author_id>', methods=['PUT'])   # jesli pominiemy argument methods to Flask domyslnie ustawi methods na GET
@validate_json_content_type
@use_args(author_schema, error_status_code=400)    # # dekorator waliduje dane przesłane w zapytaniu HTTP z wykozystaniem klasy AuthorSchema i zwraca je w postaci słownika
def update_author(args: dict, author_id: int):    # args przechowuje poprawnie zwalidowane dane z wykorzystaniem dekoratora @use_args
    author = Author.query.get_or_404(author_id, description=f'Author id: {author_id} not found')

    author.first_name = args['first_name']
    author.last_name = args['last_name']
    author.birth_date = args['birth_date']

    db.session.commit()

    return jsonify({
        'success': True,
        'data': author_schema.dump(author)
    })


@app.route('/api/v1/authors/<int:author_id>', methods=['DELETE'])   # jesli pominiemy argument methods to Flask domyslnie ustawi methods na GET
def delete_author(author_id: int):
    author = Author.query.get_or_404(author_id, description=f'Author id: {author_id} not found')

    db.session.delete(author)
    db.session.commit()
    return jsonify({
        'success': True,
        'data': f'Author id: {author_id} has been deleted'
    })