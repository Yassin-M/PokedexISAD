import os.path
import sqlite3


from flask import Flask

# los controladores
from app.database.database import Connection

from app.controller.view.bista_kontroladorea import bista_bp

def init_db():
   pass
def create_app():
   app = Flask(__name__)

   #datu basea hasieratu
   db = Connection()

   app.register_blueprint(bista_bp)
   return app