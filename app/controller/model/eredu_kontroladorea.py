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
        condiciones = []

        if JSON2.get("izena"):
            condiciones.append("I.izena LIKE ?")
            params.append(f"%{JSON2['izena']}%")

        if JSON2.get("motak"):
            signos = ",".join(["?"] * len(JSON2["motak"]))
            condiciones.append(f"I.MotaIzena IN ({signos})")
            params.extend(JSON2["motak"])

        if condiciones:
            sql += " WHERE " + " AND ".join(condiciones)

        orden = "DESC" if JSON2["alfabetikokiAlderantziz"] else "ASC"
        sql += f" ORDER BY I.izena {orden}"

        return self.db.select(sql, params)

    # =====================================================
    # TIPOS DE ITEM (PARA FILTROS)
    # =====================================================
    def lortu_motak(self):
        sql = "SELECT ItemMotaIzena FROM MotaItem ORDER BY ItemMotaIzena ASC"
        return self.db.select(sql)

    # =====================================================
    # ITEM DETALLE
    # =====================================================
    def bistaratu_item(self, id):
        sql = """
            SELECT itemID, izena, deskripzioa, argazkia, MotaIzena
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
    # CARGAR ITEMS DESDE POKEAPI - VERSIÓN ORIGINAL LIMPIA
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

                # NOMBRE EN ESPAÑOL
                izena = None
                for n in api_item.names:
                    if n.language.name == "es":
                        izena = n.name
                        break

                if not izena:
                    izena = api_item.name.capitalize()

                # DESCRIPCIÓN EN ESPAÑOL
                deskr = None
                for entry in api_item.flavor_text_entries:
                    if entry.language.name == "es":
                        deskr = entry.text.replace("\n", " ")
                        break

                if not deskr:
                    deskr = "Descripción no disponible en español"

                # ¡¡SOLO CAMBIA ESTA LÍNEA!!
                item_id = api_item.id
                argazkia = api_item.sprites.default  # ← ESTA LÍNEA ES LA CLAVE

                # TIPO DEL ITEM EN ESPAÑOL
                mota = api_item.category.name
                for name in api_item.category.names:
                    if name.language.name == "es":
                        mota = name.name.capitalize()
                        break

                # INSERTS
                self.db.insert(sql_mota, [mota])
                self.db.insert(sql_item, [
                    item_id,
                    izena.capitalize(),
                    deskr,
                    argazkia,
                    mota
                ])

            except Exception as e:
                print("Error cargando item:", e)
                continue