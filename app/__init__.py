import os.path
import sqlite3


from flask import Flask

# los controladores
from app.database.database import Connection
from app.controller.view.bista_kontroladorea import pokedex_blueprint


def create_app():
   app = Flask(__name__)

   #datu basea hasieratu
   db = Connection()

   app.register_blueprint(pokedex_blueprint(db))

   return app