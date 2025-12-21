import sqlite3
import os

from config import Config

class Connection:
   def __init__(self):
      self.connection = sqlite3.connect(
         Config.DB_PATH,
         check_same_thread=False
         )
      self.connection.row_factory = sqlite3.Row
      self._taulak_hasieratu()

   def _taulak_hasieratu(self):
       if os.path.exists('schema.sql'):
           try:
               with open('schema.sql', 'r', encoding='utf-8') as f:
                   self.connection.executescript(f.read())
           except sqlite3.Error as e:
               print(f"Error inicializando tablas: {e}")

   def select(self, sentence, parameters=None):
      cursor = self.connection.cursor()
      if parameters:
         cursor.execute(sentence, parameters)
      else:
         cursor.execute(sentence)
      rows = cursor.fetchall()
      cursor.close()
      return rows
   
   def insert(self, sentence, parameters=None):
        cursor = self.connection.cursor()
        if parameters:
            cursor.execute(sentence, parameters)
        else:
            cursor.execute(sentence)
        self.connection.commit()
        cursor.close()
   
   def update(self, sentence, parameters=None):
        cursor = self.connection.cursor()
        if parameters:
            cursor.execute(sentence, parameters)
        else:
            cursor.execute(sentence)
        self.connection.commit()
        cursor.close()
   
   def delete(self, sentence, parameters=None):
        cursor = self.connection.cursor()
        if parameters:
            cursor.execute(sentence, parameters)
        else:
            cursor.execute(sentence)
        self.connection.commit()
        cursor.close()