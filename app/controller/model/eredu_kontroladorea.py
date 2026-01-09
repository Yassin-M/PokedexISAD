from werkzeug.security import check_password_hash
from app.database.database import Connection
import json
import sqlite3

class EreduKontroladorea:

   def __init__(self):
      self.db = Connection()
   
   def saioHasi(self, erabiltzaile_izena, pasahitza):
      """Kredentzialak egiaztatu datu-basean"""
      query = "SELECT izena, pasahitza, rola FROM Erabiltzailea WHERE izena = ?"
      emaitza = self.db.select(query, (erabiltzaile_izena,))
      erabiltzailea = emaitza[0] if emaitza else None
      
      if not erabiltzailea:
         return False, None, None, "Erabiltzailea ez da existitzen"
      
      if erabiltzailea['pasahitza'] == pasahitza:
         return True, erabiltzailea['izena'], erabiltzailea['rola'], "Saioa hasi da"
      else:
         return False, None, None, "Pasahitza okerra"
   
   def balioztatu_pasahitza(self, pasahitza, pasahitza_berretsi):
      """Pasahitzak balioztatu: bat etortzea eta karaktere debekatuak"""
      karaktere_debekatuak = "|'¬£$^;#~=@"
      
      if pasahitza != pasahitza_berretsi:
         return False, "Pasahitzak ez datoz bat"
      
      for karakterea in pasahitza:
         if karakterea in karaktere_debekatuak:
            return False, f"Pasahitzak ezin du karaktere hau izan: {karakterea}"
      
      return True, "Pasahitza zuzena"
   
   def erregistratu(self, izena, email, jaiotze_data, pasahitza, pasahitza_berretsi):
      """Erabiltzaile berria datu-basean erregistratu"""
      query = "SELECT izena FROM Erabiltzailea WHERE izena = ?"
      dagoen_erabiltzaile = self.db.select(query, (izena,))
      if dagoen_erabiltzaile:
         return False, "Erabiltzailea jada existitzen da"
      
      baliozko, mezua = self.balioztatu_pasahitza(pasahitza, pasahitza_berretsi)
      if not baliozko:
         return False, mezua
      
      query = "INSERT INTO Erabiltzailea (izena, pasahitza, email, jaiotze_data, rola) VALUES (?, ?, ?, ?, ?)"
      try:
         self.db.insert(query, (izena, pasahitza, email, jaiotze_data, 'usuario'))
         return True, "Erabiltzailea behar bezala erregistratu da"
      except sqlite3.IntegrityError:
         return False, "Erabiltzailea jada existitzen da"
      except Exception as e:
         return False, f"Errorea erabiltzailea erregistratzerakoan: {str(e)}"
   
   def eguneratu_erabiltzailea(self, izena_zaharra, izena_berria=None, email=None, jaiotze_data=None, pasahitza=None):
      """Erabiltzaile datuak eguneratu datu-basean (soilik aldatutako datuak)"""
      try:
         query = "SELECT izena, pasahitza, rola FROM Erabiltzailea WHERE izena = ?"
         emaitza = self.db.select(query, (izena_zaharra,))
         erabiltzailea_zaharra = emaitza[0] if emaitza else None
         if not erabiltzailea_zaharra:
            return False, "Erabiltzailea ez da existitzen"
         
         if not izena_berria or izena_berria == "":
            izena_berria = izena_zaharra
         if not email or email == "":
            query = "SELECT email FROM Erabiltzailea WHERE izena = ?"
            result = self.db.select(query, (izena_zaharra,))
            email = result[0]['email'] if result else None
         if not jaiotze_data or jaiotze_data == "":
            query = "SELECT jaiotze_data FROM Erabiltzailea WHERE izena = ?"
            result = self.db.select(query, (izena_zaharra,))
            jaiotze_data = result[0]['jaiotze_data'] if result else None
         
            if izena_berria != izena_zaharra:
               query = "SELECT izena FROM Erabiltzailea WHERE izena = ?"
               dagoen_berria = self.db.select(query, (izena_berria,))
               if dagoen_berria:
                  return False, "Izen hori hartuta dago"
         
         if pasahitza and pasahitza != "":
            query = "UPDATE Erabiltzailea SET izena = ?, email = ?, jaiotze_data = ?, pasahitza = ? WHERE izena = ?"
            self.db.update(query, (izena_berria, email, jaiotze_data, pasahitza, izena_zaharra))
         else:
            query = "UPDATE Erabiltzailea SET izena = ?, email = ?, jaiotze_data = ? WHERE izena = ?"
            self.db.update(query, (izena_berria, email, jaiotze_data, izena_zaharra))
         
         return True, "Datuak behar bezala eguneratu dira"
      except Exception as e:
         return False, f"Errorea datuak eguneratzerakoan: {str(e)}"
   
   def erabiltzaileakKargatu(self):
      """Datu-baseko erabiltzaile guztiak lortu JSON formatuan"""
      query = "SELECT izena, email, rola, jaiotze_data FROM Erabiltzailea ORDER BY izena"
      try:
         erabiltzaileak = self.db.select(query)
         erabiltzaileak_lista = []
         for erabiltzaile in erabiltzaileak:
            erabiltzaileak_lista.append({
               'id': erabiltzaile['izena'],
               'izena': erabiltzaile['izena'],
               'email': erabiltzaile['email'],
               'admin': 1 if erabiltzaile['rola'] == 'admin' else 0,
               'jaiotze_data': erabiltzaile['jaiotze_data']
            })
         return json.dumps(erabiltzaileak_lista, ensure_ascii=False)
      except Exception as e:
         print(f"Errorea erabiltzaileak lortzerakoan: {str(e)}")
         return json.dumps([], ensure_ascii=False)
   
   def lortu_erabiltzaile_bat(self, erabiltzaile_izena):
      """Erabiltzaile bat lortu datu-basetik - KUDEATU ATALERAKO"""
      query = "SELECT izena, pasahitza, rola, email, jaiotze_data FROM Erabiltzailea WHERE izena = ?"
      try:
         emaitza = self.db.select(query, (erabiltzaile_izena,))
         return emaitza[0] if emaitza else None
      except Exception as e:
         print(f"Errorea erabiltzailea lortzerakoan: {str(e)}")
         return None
   
   def ezabatu(self, erabiltzaile_izena):
      """Erabiltzaile bat ezabatu datu-basetik"""
      query = "DELETE FROM Erabiltzailea WHERE izena = ?"
      try:
         self.db.delete(query, (erabiltzaile_izena,))
         return True, "Erabiltzailea behar bezala ezabatu da"
      except Exception as e:
         return False, f"Errorea erabiltzailea ezabatzerakoan: {str(e)}"
   
   def  baimendu(self, erabiltzaile_izena, admin_egin):
      """Erabiltzaile bati admin rola eman edo kendu"""
      rola_berria = 'admin' if admin_egin else 'usuario'
      query = "UPDATE Erabiltzailea SET rola = ? WHERE izena = ?"
      try:
         self.db.update(query, (rola_berria, erabiltzaile_izena))
         mezua = "Erabiltzailea admin bihurtu da" if admin_egin else "Admin rola kendu da"
         return True, mezua
      except Exception as e:
         return False, f"Errorea rola aldatzerakoan: {str(e)}"
   
   def lagunakKargatu(self, erabiltzaile_izena):
      """Erabiltzaile batek jarraitzen dituen pertsonak lortu"""
      query = """
         SELECT JarraituIzena, Notifikazioak
         FROM JarraitzenDu 
         WHERE JarraitzaileIzena = ?
         ORDER BY JarraituIzena
      """
      try:
         emaitza = self.db.select(query, (erabiltzaile_izena,))
         jarraitutakoak = []
         for jarraitua in emaitza:
            jarraitutakoak.append({
               'izena': jarraitua['JarraituIzena'],
               'notifikazioak': bool(jarraitua['Notifikazioak'])
            })
         return json.dumps(jarraitutakoak, ensure_ascii=False)
      except Exception as e:
         print(f"Errorea jarraitutakoak lortzerakoan: {str(e)}")
         return json.dumps([], ensure_ascii=False)
   
   def utzi_jarraitzen(self, jarraitzailea, jarraitua):
      """Erabiltzaile bat jarraitzen uztea"""
      query = "DELETE FROM JarraitzenDu WHERE JarraitzaileIzena = ? AND JarraituIzena = ?"
      try:
         self.db.delete(query, (jarraitzailea, jarraitua))
         return True, "Jarraitzea eten da"
      except Exception as e:
         return False, f"Errorea jarraitzea eteterakoan: {str(e)}"
   
   def gehituErabiltzailea(self, jarraitzailea, jarraitua):
      """Erabiltzaile bat jarraitzen hastea"""
      query = "SELECT * FROM JarraitzenDu WHERE JarraitzaileIzena = ? AND JarraituIzena = ?"
      emaitza = self.db.select(query, (jarraitzailea, jarraitua))
      
      if emaitza:
         return False, "Jada jarraitzen duzu erabiltzaile hau"
      
      if jarraitzailea == jarraitua:
         return False, "Ezin duzu zure burua jarraitu"
      
      query = "INSERT INTO JarraitzenDu (JarraitzaileIzena, JarraituIzena) VALUES (?, ?)"
      try:
         self.db.insert(query, (jarraitzailea, jarraitua))
         return True, "Orain jarraitzen duzu erabiltzaile hau"
      except Exception as e:
         return False, f"Errorea jarraitzen hastean: {str(e)}"
   
   def bilatu_erabiltzaileak(self, bilaketa, current_user):
      """Erabiltzaileak bilatu izenaren arabera - LAGUNAK GEHITU ATALERAKO"""
      query = """SELECT E.Izena AS izena, E.Email AS email
                 FROM Erabiltzailea E 
                 WHERE E.Izena LIKE ? AND E.Izena != ?
                 ORDER BY E.Izena"""
      try:
         bilaketa_pattern = f"%{bilaketa}%"
         emaitza = self.db.select(query, (bilaketa_pattern, current_user))
         erabiltzaileak = []
         for erabiltzaile in emaitza:
            query_jarraitzen = "SELECT * FROM JarraitzenDu WHERE JarraitzaileIzena = ? AND JarraituIzena = ?"
            jarraitzen_emaitza = self.db.select(query_jarraitzen, (current_user, erabiltzaile['izena']))
            
            erabiltzaileak.append({
               'izena': erabiltzaile['izena'],
               'email': erabiltzaile['email'],
               'jarraitzen': len(jarraitzen_emaitza) > 0
            })
         return json.dumps(erabiltzaileak, ensure_ascii=False)
      except Exception as e:
         print(f"Errorea erabiltzaileak bilatzerakoan: {str(e)}")
         return json.dumps([], ensure_ascii=False)
   
   def eguneratu_notifikazioak(self, jarraitzailea, jarraitua, notifikazioak):
      """Notifikazio baten egoera aldatu (aktibatu/desgaitu)"""
      query = "UPDATE JarraitzenDu SET Notifikazioak = ? WHERE JarraitzaileIzena = ? AND JarraituIzena = ?"
      try:
         self.db.update(query, (notifikazioak, jarraitzailea, jarraitua))
         return True, "Notifikazioak eguneratuta daude"
      except Exception as e:
         return False, f"Errorea notifikazioak eguneratzerakoan: {str(e)}"