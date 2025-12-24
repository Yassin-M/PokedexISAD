from app.database import db

   #metodos
def __init__(self):
   pass

def notifikazioenInformazioaLortu(erabiltzaile_izena):
   query = "SELECT J.JarraituIzena, N.DataOrdua, N.deskripzioa FROM JarraitzenDu J JOIN Notifikatu N ON J.JarraituIzena = N.ErabiltzaileIzena WHERE J.JarraitzaileIzena = ? ORDER BY N.DataOrdua DESC;"
   return db.select(query, (erabiltzaile_izena,))