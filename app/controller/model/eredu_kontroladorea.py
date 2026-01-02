from app.database import db

   #metodos
def __init__(self):
   pass

def notifikazioenInformazioaLortu(erabiltzaile_izena, bilatutako_izena):
   query = "SELECT J.JarraituIzena, N.DataOrdua, N.deskripzioa FROM JarraitzenDu J JOIN Notifikatu N ON J.JarraituIzena = N.ErabiltzaileIzena WHERE J.JarraitzaileIzena = ?"

   if bilatutako_izena != None and bilatutako_izena != '':
      query += "AND J.JarraituIzena LIKE ?"

   query += "ORDER BY N.DataOrdua DESC;"

   if bilatutako_izena != None and bilatutako_izena != '':
      notifikazioZerrenda = db.select(query, (erabiltzaile_izena, bilatutako_izena))
   else:
      notifikazioZerrenda = db.select(query, (erabiltzaile_izena,))
   
   notifikazioJSON = []
   for notifikazio in notifikazioZerrenda:
      notifikazioJSON.append({
         'JarraituIzena': notifikazio[0],
         'DataOrdua': notifikazio[1],
         'deskripzioa': notifikazio[2]
      })

   return notifikazioJSON