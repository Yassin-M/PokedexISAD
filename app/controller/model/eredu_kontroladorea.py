import pokebase as pb

class EreduKontroladorea:

    def __init__(self, db):
        self.db = db

    # =====================================================
    # ITEMDEX
    # =====================================================
    def itemdex_kargatu(self, JSON2):

        if not self.itemak_konprobatu():
            self.itemak_kargatu()

        sql = """
            SELECT I.itemID, I.izena, I.argazkia
            FROM Item I
        """
        params = []

        if JSON2["motak"]:
            signos = ",".join(["?"] * len(JSON2["motak"]))
            sql += f" WHERE I.MotaIzena IN ({signos})"
            params.extend(JSON2["motak"])

        orden = "DESC" if JSON2["alfabetikokiAlderantziz"] else "ASC"
        sql += f" ORDER BY I.izena {orden}"

        return self.db.select(sql, params)

    # =====================================================
    # ITEM DETALLE
    # =====================================================
    def bistaratu_item(self, id):
        sql = """
            SELECT itemID, izena, deskripzioa, argazkia
            FROM Item
            WHERE itemID = ?
        """
        return self.db.select(sql, [id])[0]

    # =====================================================
    # COMPROBAR ITEMS
    # =====================================================
    def itemak_konprobatu(self):
        return len(self.db.select("SELECT * FROM Item LIMIT 1")) > 0

    # =====================================================
    # CARGAR ITEMS DESDE POKEAPI
    # =====================================================
    def itemak_kargatu(self):
        sql_mota = """
            INSERT OR IGNORE INTO MotaItem (ItemMotaIzena)
            VALUES (?)
        """
        sql_item = """
            INSERT OR IGNORE INTO Item
            (itemID, izena, deskripzioa, argazkia, MotaIzena)
            VALUES (?, ?, ?, ?, ?)
        """
        for item in pb.APIResourceList("item"):
            try:
                api_item = pb.item(item["name"])

                item_id = api_item.id
                izena = api_item.name.capitalize()

                # DESCRIPCIÓN EN ESPAÑOL
                deskr = "Sin descripción"
                for entry in api_item.flavor_text_entries:
                    if entry.language.name == "es":
                        deskr = entry.text.replace("\n", " ")
                        break

                argazkia = api_item.sprites.default
                mota = api_item.category.name

                self.db.insert(sql_mota, [mota])
                self.db.insert(sql_item, [
                    item_id,
                    izena,
                    deskr,
                    argazkia,
                    mota
                ])

            except Exception as e:
                print("Error cargando item:", e)
