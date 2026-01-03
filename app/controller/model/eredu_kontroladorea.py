import pokebase as pb
from .api_kontroladorea import APIKontroladorea
class EreduKontroladorea:
   #metodos
   def __init__(self, db):
      self.db = db
      self.api = APIKontroladorea()

   def pokedex_kargatu(self, JSON2):
      if not self.pokemonak_konprobatu():
         self.pokemonak_kargatu()
      if not self.motak_konprobatu():
         self.motak_kargatu()
      if not self.abileziak_konprobatu():
         self.abileziak_kargatu()
      if not self.mugimenduak_konprobatu():
         self.mugimenduak_kargatu()
      sql3 = "SELECT P.izena, P.irudia, P.pokeId FROM PokemonPokedex P"
      parametroak = []

      if JSON2['motak']:
         sql3 += " JOIN DaMotaPokemon DM ON P.pokeId = DM.pokemonID JOIN MotaPokemon M ON DM.motaIzena = M.pokemonMotaIzena"

      if JSON2['izena']:
         sql3 += " WHERE P.izena LIKE ?"
         parametroak.append(f"%{JSON2['izena']}%")

      if JSON2['generazioak']:
         signos = ','.join(['?'] * len(JSON2['generazioak']))
         operator = "AND" if "WHERE" in sql3 else "WHERE"
         sql3 += f" {operator} P.generazioa IN ({signos})"
         parametroak.extend(JSON2['generazioak'])

      if JSON2['motak']:
         signos_motak = ','.join(['?'] * len(JSON2['motak']))
         operador = "AND" if "WHERE" in sql3 else "WHERE"
         sql3 += f" {operador} M.pokemonMotaIzena IN ({signos_motak})"
         parametroak.extend(JSON2['motak'])

      errenkadak = self.db.select(sql3, parametroak)

      json1 = []

      for pokemon in errenkadak:
         datuak = {
            'izena': pokemon['izena'],
            'argazkia': pokemon['irudia'],
            'id': pokemon['pokeId']
         }
         json1.append(datuak)

      return json1

   def pokemonak_kargatu(self):
      sql2 = 'INSERT OR IGNORE INTO PokemonPokedex (pokeId, izena, altuera, pisua, generoa, deskripzioa, irudia, generazioa) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
      pokemon_izenak = self.api.pokemon_izenak_eskatu()
      for pokemon in pokemon_izenak:
         try:
            parametroak = self.api.pokemon_eskatu(pokemon['name'])
            self.db.insert(sql2, [parametroak["pokeId"], parametroak["izena"], parametroak["altuera"], parametroak["pisua"], parametroak["generoa"], parametroak["deskripzioa"], parametroak["irudia"], parametroak["generazioa"]])
         except Exception as e:
            print(f"Error {e}")

   def bistaratu_pokemon(self, id):
      sql = "SELECT P.izena, P.pokeId, P.irudia, P.deskripzioa, P.pisua, P.altuera FROM PokemonPokedex P WHERE P.pokeId = ?"
      errenkada = self.db.select(sql, [id])[0]

      if errenkada:
         json3 = {
            'izena': errenkada['izena'],
            'argazkia': errenkada['irudia'],
            'deskr': errenkada['deskripzioa'],
            'id': errenkada['pokeId'],
            'altuera': errenkada['altuera'],
            'pisua': errenkada['pisua']
         }
         abileziak = self.db.select("SELECT izena FROM IzanDezake WHERE pokemonPokedexID = ?", [errenkada['pokeId']])
         izenak = [abi['izena'] for abi in abileziak]
         json3['abileziak'] = izenak
         return json3

   def motak_kargatu(self):
      sql1 = "INSERT INTO MotaPokemon (pokemonMotaIzena) VALUES (?)"
      sql2 = "INSERT INTO DaMotaPokemon (motaIzena, pokemonID) VALUES (?, ?)"
      mota_izenak = self.api.mota_izenak_eskatu()
      for mota in mota_izenak:
         try:
            if mota['name'] in ['unknown', 'shadow']:
                  continue
            self.db.insert(sql1, [mota['name'].capitalize()])
            tipo = self.api.mota_eskatu(mota['name'])
            for pokemon in tipo["pokemonak"]:
               try:
                  pokemon_id = int(pokemon.pokemon.url.split('/')[-2])
                  self.db.insert(sql2, [mota['name'], pokemon_id])
               except Exception as e:
                  print(f"Error {e}")
         except Exception as e:
            print(f"Error {e}")

      sql3 = "INSERT INTO Multiplikatzailea(pokemonMotaJaso, pokemonMotaEraso, multiplikatzailea) VALUES (?, ?, ?)"
      for mota in mota_izenak:
         tipo = self.api.mota_eskatu(mota['name'])
         dobles = tipo["erlazioak"].double_damage_to
         mitades = tipo["erlazioak"].half_damage_to
         zeros = tipo["erlazioak"].no_damage_to
         for doble in dobles:
            parametroak = [doble.name.capitalize(), mota["name"].capitalize(), 2.0]
            self.db.insert(sql3, parametroak)
         for mitad in mitades:
            parametroak = [mitad.name.capitalize(), mota['name'], 0.5]
            self.db.insert(sql3, parametroak)
         for zero in zeros:
            parametroak = [zero.name.capitalize(), mota['name'], 0.0]
            self.db.insert(sql3, parametroak)
         #esta parte habra que ver como acortarla un poco
      pass

   def abileziak_kargatu(self):
      sql1 = "INSERT OR IGNORE INTO Abilezia (izena, deskripzioa) VALUES (?, ?)"
      sql2 = "INSERT OR IGNORE INTO IzanDezake (pokemonPokedexID, izena, ezkutua) VALUES (?, ?, ?)"
      abilezi_izenak = self.api.abilezi_izenak_eskatu()
      for abileziak in abilezi_izenak:
         abilezia = self.api.abilezia_eskatu(abileziak['name'])
         self.db.insert(sql1, [abilezia["izena"], abilezia["deskripzioa"]])
         for pokemon in abilezia["pokemonak"]:
            poke_id = int(pokemon.pokemon.url.split('/')[-2])
            self.db.insert(sql2, [poke_id, abilezia["izena"], pokemon.is_hidden])

   def mugimenduak_kargatu(self):
      sql1 = "INSERT INTO Mugimendua (izena, potentzia, zehaztazuna, PP, efektua, pokemonMotaIzena) VALUES (?, ?, ?, ?, ?, ?)"
      sql2 = "INSERT INTO IkasDezake (pokedexId, mugiIzena) VALUES (?, ?)"
      mugimendu_izenak = self.api.mugimendu_izenak_eskatu()
      for izena in mugimendu_izenak:
         mugimendua = self.api.mugimendua_eskatu(izena['name'])
         self.db.insert(sql1, [mugimendua["izena"], mugimendua["potentzia"], mugimendua["zehaztazuna"], mugimendua["PP"], mugimendua["efektua"], mugimendua["pokemonMotaIzena"]])
         for pokemon in mugimendua["pokemonak"]:
            pokemon_id = int(pokemon.url.split('/')[-2])
            self.db.insert(sql2, [pokemon_id, mugimendua["izena"]])

   def __lortu_deskripzioa(self, objektua):
      for sarrera in objektua.flavor_text_entries:
         if sarrera.language.name == 'es':
            return sarrera.flavor_text.replace('\n', ' ').replace('\f', ' ')
      return 'Ez dago deskripziorik gaztelaniaz'

   def __lortu_izena(self, objektua):
      for sarrera in objektua.names:
         if sarrera.language.name == 'es':
            return sarrera.name.replace('\n', ' ').replace('\f', ' ')
      return objektua.name

   def pokemonak_konprobatu(self):
      return len(self.db.select("SELECT * FROM PokemonPokedex"))>1

   def motak_konprobatu(self):
      return len(self.db.select("SELECT * FROM MotaPokemon"))>1 and len(self.db.select("SELECT * FROM DaMotaPokemon"))>1 and len(self.db.select("SELECT * FROM Multiplikatzailea"))

   def mugimenduak_konprobatu(self):
      return len(self.db.select("SELECT * FROM Mugimendua"))>0

   def abileziak_konprobatu(self):
      hay_defs = len(self.db.select("SELECT izena FROM Abilezia LIMIT 1")) > 0

      hay_relaciones = len(self.db.select("SELECT pokemonPokedexID FROM IzanDezake LIMIT 1")) > 0

      return hay_defs and hay_relaciones

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