import os.path
from flask import Flask
from app.database.database import Connection
from app.controller.view.bista_kontroladorea import pokedex_blueprint
from app.controller.view.bista_kontroladorea import itemdex_blueprint


def create_app():
    app = Flask(__name__)

    # Inicializar la DB
    db = Connection()

    # Registrar blueprint de Itemdex
    app.register_blueprint(itemdex_blueprint(db))
    app.register_blueprint(pokedex_blueprint(db))
    return app