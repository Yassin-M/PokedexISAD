class EreduKontroladorea:

    def __init__(self, db):
        self.db = db

    def taldeak_kargatu(self, erabiltzailea):
        cursor = self.db.connection.cursor()
        query = "SELECT izena FROM Taldea WHERE erabiltzaileIzena = ?"
        cursor.execute(query, (erabiltzailea,))
        talde_zerrenda = [row["izena"] for row in cursor.fetchall()]
        cursor.close()
        return talde_zerrenda