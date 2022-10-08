from book_library_app import db
from webargs.flaskparser import use_args  # parsuje i sprawdza poprawnosc przesłanych danych w zapytaniu HTTP, łaczymy go z pakietem marshmallow w celu walidacji naszych danych
from flask import jsonify, request    # request wyciąga informacje z ciała zapytania HTTP
from book_library_app.models import Author, AuthorSchema, author_schema
from book_library_app.utils import validate_json_content_type
from book_library_app.authors import authors_bp

@authors_bp.route('/api/v1/authors', methods=['GET'])   # jesli pominiemy argument methods to Flask domyslnie ustawi methods na GET
def get_authors():
    query = Author.query    # trybut query zwraca nowy obiekt query, który udostępnia szereg metod: filtrowanie, srtowanie danych, all() zwraca wszystkie dostepne rekordy w tabeli Authors
    schema_args = Author.get_schema_args(request.args.get('fields'))
    query = Author.apply_order(query, request.args.get('sort')) # drugi argument to wartosc klucza sort (wyciagamy wartosc w parametrze  sort znajdujacego sie w adresie URL
                                                                # metoda przyjmuje query i w zaleznosci od znajadujacych sie w adresie URL parametrow bedzie budowała query dynamicznie
    query = Author.apply_filter(query)
    items, pagination = Author.get_pagination(query)
    authors = AuthorSchema(**schema_args).dump(items) # przekazujemy wartosci schema_args do author_schema (**schema_args-wypakowyjemy zawartosc tego słownika)
                                                # instancja klasy author_schema jest ynamicznie tworzona na podstawie przekazanych parametrów do zapytania HTTP
                                                # dump przekształca obiekty w format JSON

    return jsonify({
        'success': True,
        'data': authors,    # w odpowiedzi serwera w kluczu 'data' przesyłamy liste obiektów w JSONie, dump przekształca obiekty w format JSON
        # jako argument przekazuje wyciagniete obiekty bazy danych
        'number_of_records': len(authors),
        'pagination': pagination
    })


authors_bp.route('/api/v1/authors/<int:author_id>', methods=['GET'])   # jesli pominiemy argument methods to Flask domyslnie ustawi methods na GET
def get_author(author_id: int):
    author = Author.query.get_or_404(author_id, description=f'Author id: {author_id} not found')    # get_or_404 wyciaga rekord na podstawie przekazanego klucza podstawowego, jak go nie odnajdzie to zwroci kod błedu 404
    return jsonify({
        'success': True,
        'data': author_schema.dump(author)
    })


authors_bp.route('/api/v1/authors', methods=['POST'])   # jesli pominiemy argument methods to Flask domyslnie ustawi methods na GET
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


authors_bp.route('/api/v1/authors/<int:author_id>', methods=['PUT'])   # jesli pominiemy argument methods to Flask domyslnie ustawi methods na GET
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


authors_bp.route('/api/v1/authors/<int:author_id>', methods=['DELETE'])   # jesli pominiemy argument methods to Flask domyslnie ustawi methods na GET
def delete_author(author_id: int):
    author = Author.query.get_or_404(author_id, description=f'Author id: {author_id} not found')

    db.session.delete(author)
    db.session.commit()
    return jsonify({
        'success': True,
        'data': f'Author id: {author_id} has been deleted'
    })