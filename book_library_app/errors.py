from flask import Response, jsonify
from book_library_app import app, db
# import instancji klasy flask

# w przypadku wystapienia jakiegokolwiek błedu chcemy zwracac zawsze ten sam jego format
# klasa response tworzy własna implementacje obiekty response w formacie JSON


class ErrorResponse:
    def __init__(self, message: str, http_status: int):
        self.payload = {      # payload zwracamy w ciele odpowiedzi serwera
            'success': False,
            'message': message
        }
        self.http_status = http_status    # status odpowiedzi

    def to_response(self) -> Response:    # przekształca instancje klasy ErrorResponse na obiekt response
        response = jsonify(self.payload)# tworze własny obiekt Response przy pomocy funkcji jsonify z pakietu flask
        # zmieniamy kod odopowiedzi obiektu response
        response.status_code = self.http_status
        return response


@app.errorhandler(404)    # do tej metody mozemy podac kod odpowiedzi albo rzucony wyjątek
def not_found_error(err):    # funkcja bedzie odpalana w momencie wystapienia tego kodu odpowiedzi
    return ErrorResponse(err.description, 404).to_response()    # to_response przekształca ta instancje na obiekt typu response


@app.errorhandler(400)
def bad_request_error(err):
    messages = err.data.get('messages', {}).get('json', {})
    return ErrorResponse(messages, 400).to_response()


@app.errorhandler(415)
def unsupported_media_type_error(err):
    return ErrorResponse(err.description, 415).to_response()


@app.errorhandler(500)
def internal_server_error(err):
    db.session.rollback()    # metoda czysci sesje
    return ErrorResponse(err.description, 500).to_response()