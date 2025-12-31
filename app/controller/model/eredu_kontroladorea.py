class EreduKontroladorea:

    def __init__(self, db):
        self.db = db

    def taldeak_kargatu(self, erabiltzailea):
      sql1 = "SELECT taldeIzena FROM Taldea WHERE erabiltzaileIzena = ?"
      taldeak = self.db.select(sql1, (erabiltzailea,))

      json4 = [izena for taldea in taldeak for izena in [{'izena': taldea[0]}]]
      return json4