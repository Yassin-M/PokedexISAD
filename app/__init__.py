import os.path
import sqlite3


from flask import Flask

# los controladores
from app.database.database import Connection

def init_db():
   pass
def create_app():
   app = Flask(__name__)

   #datu basea hasieratu
   db = Connection()

   return app