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
            SELECT I.itemID as ID, I.izena, I.argazkia
            FROM Item I
            WHERE 1=1
        """
        params = []

        # Filtro por nombre
        if JSON2.get("izena"):
            sql += " AND I.izena LIKE ?"
            params.append(f"%{JSON2['izena']}%")

        # Filtro por tipos - Usando MotaIzena directa de Item
        if JSON2.get("motak") and len(JSON2["motak"]) > 0:
            signos = ",".join(["?"] * len(JSON2["motak"]))
            sql += f" AND I.MotaIzena IN ({signos})"
            params.extend(JSON2["motak"])

        # Orden alfabético
        orden = "DESC" if JSON2.get("alfabetikokiAlderantziz", False) else "ASC"
        sql += f" ORDER BY I.izena {orden}"

        return self.db.select(sql, params)

    # =====================================================
    # TIPOS DE ITEM (PARA FILTROS)
    # =====================================================
    def lortu_motak(self):
        sql = "SELECT ItemMotaIzena FROM MotaItem ORDER BY ItemMotaIzena ASC"
        return self.db.select(sql)

    # =====================================================
    # ITEM DETALLE - CORREGIDO para incluir MotaIzena
    # =====================================================
    def bistaratu_item(self, id):
        sql = """
            SELECT itemID, izena, deskripzioa, argazkia, MotaIzena
            FROM Item
            WHERE itemID = ?
            LIMIT 1
        """
        resultado = self.db.select(sql, [id])
        return resultado[0] if resultado else None

    # =====================================================
    # COMPROBAR ITEMS
    # =====================================================
    def itemak_konprobatu(self):
        resultado = self.db.select("SELECT * FROM Item LIMIT 1")
        return len(resultado) > 0

    # =====================================================
    # CARGAR ITEMS DESDE POKEAPI
    # =====================================================
    def itemak_kargatu(self):
        sql_mota = """
                   INSERT \
                   OR IGNORE INTO MotaItem (ItemMotaIzena)
            VALUES (?) \
                   """

        sql_item = """
                   INSERT \
                   OR IGNORE INTO Item
            (itemID, izena, deskripzioa, argazkia, MotaIzena)
            VALUES (?, ?, ?, ?, ?) \
                   """

        # Diccionario de traducciones COMPLETO
        traducciones = {
            # ==================== TIPOS QUE SÍ APARECEN ====================
            # Poké Balls
            "standard-balls": "Poké Balls estándar",
            "special-balls": "Poké Balls especiales",
            "apricorn-balls": "Poké Balls de Bayas",

            # Medicina y curación
            "healing": "Curación",
            "status-cures": "Cura estados",
            "pp-recovery": "Recupera PP",
            "revival": "Revivir",
            "vitamins": "Vitaminas",
            "stat-boosts": "Mejora estadísticas",
            "medicine": "Medicina",
            "picky-healing": "Curación exigente",
            "baking-only": "Solo para hornear",
            "type-protection": "Protección tipo",
            "in-a-pinch": "En apuros",

            # Objetos equipables
            "held-items": "Objetos equipables",
            "bad-held-items": "Objetos equipables malos",
            "choice": "Elección",
            "type-enhancement": "Mejora de tipo",

            # Entrenamiento
            "training": "Entrenamiento",
            "effort-training": "Entrenamiento esfuerzo",
            "effort-drop": "Aumento esfuerzo",

            # Máquinas
            "all-machines": "Todas las máquinas",
            "machines": "Máquinas",
            "machine": "Máquina",

            # Específicos
            "species-specific": "Específico por especie",
            "dex-completion": "Completar Pokédex",
            "collectibles": "Coleccionables",
            "collectible": "Coleccionable",
            "event-items": "Objetos de evento",
            "gameplay": "Jugabilidad",
            "plates": "Placas",

            # Jugabilidad
            "apricorn-box": "Caja de Bayas",
            "data-cards": "Tarjetas datos",
            "jewels": "Joyas",
            "miracle-shooter": "Lanzador milagro",

            # Varios
            "pokeballs": "Poké Balls",
            "berries": "Bayas",
            "mail": "Cartas",
            "all-mail": "Todas las cartas",
            "battle": "Combate",
            "key": "Clave",
            "evolution": "Evolución",
            "spelunking": "Espeleología",
            "mulch": "Abono",
            "flutes": "Flautas",
            "unused": "No usado",
            "plot-advancement": "Avance de trama",
            "loot": "Botín",
            "other": "Otros",

            # Nuevos tipos (vistos en consola)
            "dynamax-crystals": "Cristales Dinamax",
            "curry-ingredients": "Ingredientes curry",
            "nature-mints": "Menta naturaleza",
            "sandwich-ingredients": "Ingredientes sándwich",
            "tm-materials": "Materiales MT",
            "tera-shard": "Fragmento Tera",
            "species-candies": "Caramelos especie",
            "catching-bonus": "Bonus captura",

            # ==================== FALLBACK ====================
            # Si no está en el diccionario, se capitaliza
        }

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
                    izena = api_item.name.replace("-", " ").title()

                # DESCRIPCIÓN EN ESPAÑOL
                deskr = None
                for entry in api_item.flavor_text_entries:
                    if entry.language.name == "es":
                        deskr = entry.text.replace("\n", " ").replace("\f", " ")
                        break

                if not deskr:
                    deskr = "Descripción no disponible en español"

                item_id = api_item.id
                argazkia = api_item.sprites.default

                # TIPO DEL ITEM EN ESPAÑOL - MEJORADO
                mota_api = api_item.category.name

                # 1. Primero buscar en las traducciones de la API
                mota = mota_api  # Por defecto
                for name in api_item.category.names:
                    if name.language.name == "es":
                        mota = name.name
                        break

                # 2. Si no encontró o la traducción es muy similar al inglés, usar nuestro diccionario
                if mota == mota_api or mota.lower() == mota_api.lower():
                    # Limpiar y buscar en nuestro diccionario
                    mota_limpia = mota_api.lower().strip()
                    if mota_limpia in traducciones:
                        mota = traducciones[mota_limpia]
                    else:
                        # Si no está en el diccionario, capitalizar apropiadamente
                        mota = mota_api.replace("-", " ").title()

                # 3. Asegurar que no sea None o vacío
                if not mota or mota.strip() == "":
                    mota = "Otros"

                # INSERTS
                self.db.insert(sql_mota, [mota])
                self.db.insert(sql_item, [
                    item_id,
                    izena,
                    deskr,
                    argazkia,
                    mota
                ])

            except Exception as e:
                print(f"Error cargando item {item['name']}: {e}")
                continue

        print("=== CARGA DE ITEMS COMPLETADA ===")
        print("Tipos únicos cargados:")
        tipos = self.db.select("SELECT DISTINCT ItemMotaIzena FROM MotaItem ORDER BY ItemMotaIzena")
        for tipo in tipos:
            print(f"  - {tipo[0]}")