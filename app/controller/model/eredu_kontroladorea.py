from app.database import db
class EreduKontroladorea:

   #metodos
   def __init__(self):
      pass

   def notifikazioenInformazioaLortu():
      query = "SELECT J.JarraituaIzena, N.DataOrdua, N.deskripzioa FROM JarraitzenDu J JOIN Notifikatu N ON J.JarraituaIzena = N.ErabiltzaileIzena WHERE J.JarraitzaileIzena = %s ORDER BY N.DataOrdua DESC;"
      return db.select(query)