class EreduKontroladorea:

    def __init__(self, db):
        self.db = db

    def taldeak_kargatu(self, erabiltzailea):
      sql1 = "SELECT taldeIzena FROM Taldea WHERE erabiltzaileIzena = ?"
      taldeak = self.db.select(sql1, (erabiltzailea,))

      json4 = [izena for taldea in taldeak for izena in [{'izena': taldea[0]}]]
      return json4
    
    def sortu_talde_hutsa(self, erabiltzailea):
      sql2 = " INSERT INTO taldea (taldeIzena, erabiltzaileIzena) VALUES (?, ?)"
      taldeIzena = "Talde 4"
      self.db.insert(sql2, (taldeIzena, erabiltzailea))
      return taldeIzena
    
    def get_taldea():
       sql2 = " SELECT "