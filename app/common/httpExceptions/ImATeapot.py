from werkzeug.exceptions import ImATeapot
from flask import make_response, json

class ImATeapot(ImATeapot):
    def __init__(self, description=None):
        self.responseText = self.description if description == None else description

    def get_response(self, environ):
        return make_response(json.jsonify({'Error': self.responseText}), 418)
