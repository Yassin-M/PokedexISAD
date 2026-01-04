from .api_kontroladorea import APIKontroladorea
from app.database import db
import os

class EreduKontroladorea:
   #metodos
   def __init__(self, db):
      self.db = db
      self.api = APIKontroladorea()

   def taldeak_kargatu(self, erabiltzailea):
      sql1 = "SELECT taldeIzena FROM Taldea WHERE erabiltzaileIzena = ?"
      taldeak = self.db.select(sql1, (erabiltzailea,))

      json4 = [izena for taldea in taldeak for izena in [{'izena': taldea[0]}]]
      return json4

   def pokedex_kargatu(self, JSON2):
      if not self.pokemonak_konprobatu():
         self.pokemonak_kargatu()
      if not self.motak_konprobatu():
         self.motak_kargatu()
      if not self.abileziak_konprobatu():
         self.abileziak_kargatu()
      if not self.mugimenduak_konprobatu():
         self.mugimenduak_kargatu()
      if not self.eboluzioak_konprobatu():
         self.eboluzioak_kargatu()
      self.delete_test_team()
      #self.create_simple_test_team()
      #motak_irudiak_eguneratu()

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
      sql1 = "INSERT INTO MotaPokemon (pokemonMotaIzena, irudia) VALUES (?, ?)"
      sql2 = "INSERT INTO DaMotaPokemon (motaIzena, pokemonID) VALUES (?, ?)"
      mota_izenak = self.api.mota_izenak_eskatu()
      for mota in mota_izenak:
         try:
            if mota['name'] in ['unknown', 'shadow']:
                  continue
            self.db.insert(sql1, [mota['name'].capitalize(), f"/static/icons/{mota['name']}.svg" ])
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

   def motak_irudiak_eguneratu(self):
      mota_irudiak = [
         ('normal', '/static/icons/normal.svg'),
         ('fire', '/static/icons/fire.svg'),
         ('water', '/static/icons/water.svg'),
         ('electric', '/static/icons/electric.svg'),
         ('grass', '/static/icons/grass.svg'),
         ('ice', '/static/icons/ice.svg'),
         ('fighting', '/static/icons/fighting.svg'),
         ('poison', '/static/icons/poison.svg'),
         ('ground', '/static/icons/ground.svg'),
         ('flying', '/static/icons/flying.svg'),
         ('psychic', '/static/icons/psychic.svg'),
         ('bug', '/static/icons/bug.svg'),
         ('rock', '/static/icons/rock.svg'),
         ('ghost', '/static/icons/ghost.svg'),
         ('dark', '/static/icons/dark.svg'),
         ('dragon', '/static/icons/dragon.svg'),
         ('steel', '/static/icons/steel.svg'),
         ('fairy', '/static/icons/fairy.svg')
      ]

      sql = "UPDATE MotaPokemon SET irudia = ? WHERE pokemonMotaIzena = ?"

      for mota_izena, irudia in mota_irudiak:
         try:
            self.db.insert(sql, [irudia, mota_izena])
         except Exception as e:
            print(f"UPDATE {mota_izena} error: {e}")

   def ikasdezake_mugimenduak(self):
      sql = """
            UPDATE IkasDezake
            SET mugiIzena = (SELECT izena \
                             FROM Mugimendua \
                             WHERE LOWER(Mugimendua.izena) = LOWER(IkasDezake.mugiIzena)
               LIMIT 1
               )
            WHERE EXISTS (
               SELECT 1
               FROM Mugimendua
               WHERE LOWER (Mugimendua.izena) = LOWER (IkasDezake.mugiIzena)
               ) \
            """
      try:
         self.db.insert(sql, [])
         print("IkasDezake 所有技能名已统一修正为 Mugimendua 标准名字")
      except Exception as e:
         print("批量更新 IkasDezake 错误:", e)

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
      sql1 = "INSERT OR IGNORE INTO Mugimendua (izena, potentzia, zehaztazuna, PP, efektua, pokemonMotaIzena) VALUES (?, ?, ?, ?, ?, ?)"
      sql2 = "INSERT OR IGNORE INTO IkasDezake (pokedexId, mugiIzena) VALUES (?, ?)"
      mugimendu_izenak = self.api.mugimendu_izenak_eskatu()
      for izena in mugimendu_izenak:
         mugimendua = self.api.mugimendua_eskatu(izena['name'])
         self.db.insert(sql1, [mugimendua["izena"], mugimendua["potentzia"], mugimendua["zehaztazuna"], mugimendua["PP"], mugimendua["efektua"], mugimendua["pokemonMotaIzena"]])
         for pokemon in mugimendua["pokemonak"]:
            pokemon_id = int(pokemon.url.split('/')[-2])
            self.db.insert(sql2, [pokemon_id, mugimendua["izena"]])

   def eboluzioak_kargatu(self):
      sql = """
            INSERT \
            OR IGNORE INTO Eboluzioa (pokemonPokedexID, eboluzioaPokeId)
      VALUES (?, ?) \
            """

      try:
         eboluzioKateak = self.api.eboluzioak_eskatu()

         for aurreko_id, uneko_id in eboluzioKateak:
            try:
               self.db.insert(sql, [aurreko_id, uneko_id])
            except Exception as e:
               print(f"Ezin izan da eboluzioa sartu: {aurreko_id} -> {uneko_id} | {e}")

      except Exception as e:
         print(f"Eboluzioak kargatzean errorea: {e}")

   def eboluzioak_konprobatu(self):
      return len(self.db.select("SELECT * FROM Eboluzioa LIMIT 1")) > 0

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
      print("Cargando Items...")
      sql_mota = "INSERT OR IGNORE INTO MotaItem (ItemMotaIzena) VALUES (?)"
      sql_item = "INSERT OR IGNORE INTO Item (itemID, izena, deskripzioa, argazkia, MotaIzena) VALUES (?, ?, ?, ?, ?)"

      for item in self.api.item_izenak_eskatu():
         try:
               # Usamos el API Controller para procesar datos
               datuak = self.api.itema_eskatu(item['name'])

               self.db.insert(sql_mota, [datuak["mota"]])
               self.db.insert(sql_item, [
                  datuak["id"],
                  datuak["izena"],
                  datuak["deskripzioa"],
                  datuak["argazkia"],
                  datuak["mota"]
               ])
         except Exception as e:
               print(f"Error item {item['name']}: {e}")

      print("=== CARGA DE ITEMS COMPLETADA ===")
      print("Tipos únicos cargados:")
      tipos = self.db.select("SELECT DISTINCT ItemMotaIzena FROM MotaItem ORDER BY ItemMotaIzena")
      for tipo in tipos:
         print(f"  - {tipo[0]}")

   # =====================================================
   # CHATBOT
   # =====================================================
   def getMugimenduIkasgarriak(self, pokeId):
      sql = """
            SELECT p.izena  AS pokemon_izena,
                   p.irudia AS pokemon_irudia,
                   m.izena  AS mugimendu_izena,
                   m.potentzia,
                   m.zehaztazuna
            FROM PokemonPokedex p
                    LEFT JOIN IkasDezake i ON p.pokeId = i.pokedexId
                    LEFT JOIN Mugimendua m ON i.mugiIzena = m.izena
            WHERE p.pokeId = ? \
            """

      errenkadak = self.db.select(sql, [pokeId])

      if not errenkadak:
         return None

      pokemon_info = {
         "izena": errenkadak[0]["pokemon_izena"],
         "irudia": errenkadak[0]["pokemon_irudia"]
      }

      mugimenduak = []
      for unekoa in errenkadak:
         if unekoa["mugimendu_izena"]:
            mugimenduak.append({
               "mugimenduIzena": unekoa["mugimendu_izena"],
               "potentzia": unekoa["potentzia"],
               "zehaztasuna": unekoa["zehaztazuna"]
            })

      pokemon_info["mugimenduak"] = mugimenduak
      return pokemon_info

   def getIndarrak(self, pokeId):
      # Lehenik eta behin Pokemon-aren berezko mota guztiak lortu
      sql_pokemon_motak = """
                          SELECT t.pokemonMotaIzena AS izena, \
                                 t.irudia           AS irudia
                          FROM DaMotaPokemon d
                                  JOIN MotaPokemon t ON d.MotaIzena = t.pokemonMotaIzena
                          WHERE d.pokemonID = ? \
                          """

      pokemon_motak = self.db.select(sql_pokemon_motak, [pokeId])

      if not pokemon_motak:
         return None

      # Pokemon-aren oinarrizko informazioa lortu
      sql_pokemon_info = """
                         SELECT izena, irudia
                         FROM PokemonPokedex
                         WHERE pokeId = ? \
                         """

      pokemon_row = self.db.select(sql_pokemon_info, [pokeId])

      if not pokemon_row:
         return None

      pokemon_info = {
         "izena": pokemon_row[0]["izena"],
         "irudia": pokemon_row[0]["irudia"],
         "pokemon_motak": pokemon_motak  # Pokemon-aren berezko motak gehitu
      }

      # Pokemon-aren mota guztien indarrak eta ahuleziak bildu
      indarrak_set = set()  # Set erabili bikoizketak saihesteko
      ahuleziak_set = set()

      for pokemon_mota in pokemon_motak:
         mota_izena = pokemon_mota["izena"]

         # Mota honek beste motak erasotzerakoan duen efektua kontsultatu
         sql_multiplikatzailea = """
                                 SELECT m.pokemonMotaEraso, \
                                        m.multiplikatzailea, \
                                        t.irudia AS erasoko_mota_irudia
                                 FROM Multiplikatzailea m
                                         JOIN MotaPokemon t ON m.pokemonMotaEraso = t.pokemonMotaIzena
                                 WHERE m.pokemonMotaJaso = ? \
                                 """

         efektuak = self.db.select(sql_multiplikatzailea, [mota_izena])

         for efektua in efektuak:
            efektu_item = {
               "izena": efektua["pokemonMotaEraso"],
               "irudia": efektua["erasoko_mota_irudia"]
            }

            if efektua["multiplikatzailea"] > 1:
               # Eraso-efektua >1 bada, hau Pokemon-aren indarra da (zein motarekiko abantaila duen)
               indarrak_set.add((efektu_item["izena"], efektu_item["irudia"]))
            elif efektua["multiplikatzailea"] < 1:
               # Eraso-efektua <1 bada, hau Pokemon-aren ahulezia da (zein motarekiko desabantaila duen)
               ahuleziak_set.add((efektu_item["izena"], efektu_item["irudia"]))

      # Set-a listara bihurtu
      pokemon_info["indarrak"] = [{"izena": izena, "irudia": irudia}
                                  for izena, irudia in indarrak_set]
      pokemon_info["ahuleziak"] = [{"izena": izena, "irudia": irudia}
                                   for izena, irudia in ahuleziak_set]

      return pokemon_info

   def getEboluzioa(self, poke_id):

      aurrekoak, hurrengoak = [], []  # Aurreko eta hurrengo eboluzioak gordetzeko

      def bilatu_evoluzioak(start_id, aurreko=True):
         emaitza = []
         bisitatuak = set()  # Errepikapenak saihesteko, jadanik bisitatu ditugun ID-ak
         itzuli = [start_id]  # Oraindik bisitatu beharreko ID-ak (BFS algoritmoa)

         while itzuli:  # BFS bilaketa
            unekoa = itzuli.pop(0)
            if unekoa in bisitatuak:  # Jadanik bisitatutakoa bada, jarraitu
               continue
            bisitatuak.add(unekoa)  # Markatu bisitatu bezala

            # SQL kontsulta prestatu aurreko edo hurrengo eboluzioak lortzeko
            if aurreko:
               sql = """
                     SELECT P.pokeId, P.izena, P.irudia
                     FROM Eboluzioa E
                             JOIN PokemonPokedex P ON E.pokemonPokedexID = P.pokeId
                     WHERE E.eboluzioaPokeId = ? \
                     """
            else:
               sql = """
                     SELECT P.pokeId, P.izena, P.irudia
                     FROM Eboluzioa E
                             JOIN PokemonPokedex P ON E.eboluzioaPokeId = P.pokeId
                     WHERE E.pokemonPokedexID = ? \
                     """

            # SQL exekutatu eta emaitzak prozesatu
            for unekoa_info in self.db.select(sql, [unekoa]):
               emaitza.append(unekoa_info)
               # Hurrengo bilaketarako gehitu ID-a
               if unekoa_info["pokeId"] not in bisitatuak:
                  itzuli.append(unekoa_info["pokeId"])

         return emaitza

      aurrekoak = bilatu_evoluzioak(poke_id, aurreko=True)
      hurrengoak = bilatu_evoluzioak(poke_id, aurreko=False)
      unekoa = self.db.select("SELECT izena, irudia FROM PokemonPokedex WHERE pokeId = ?", [poke_id])

      if not unekoa:
         return None

      eboluzio_info = {
         "izena": unekoa[0]["izena"],
         "irudia": unekoa[0]["irudia"],
         "aurrekoak": aurrekoak,
         "hurrengoak": hurrengoak
      }

      return eboluzio_info

   def getOnenak(self, talde_info):
      taldeIzena = talde_info.get("taldeIzena")
      erabiltzaileIzena = talde_info.get("erabiltzaileIzena")

      if not taldeIzena or not erabiltzaileIzena:
         return None

      # SQL kontsulta taldeko pokemon guztiak lortzeko
      sql = """
            SELECT pt.PokemonPokedexID, \
                   pt.izena, \
                   pt.HP, \
                   pt.ATK, \
                   pt.DEF, \
                   pt.SPATK, \
                   pt.SPDEF, \
                   pt.SPE, \
                   pd.irudia
            FROM Taldea t
                    JOIN PokemonTaldean pta
                         ON pta.taldeIzena = t.taldeIzena
                    JOIN PokemonPokedex pd
                         ON pd.pokeId = pta.pokeId
                    JOIN PokemonTalde pt
                         ON pt.PokemonPokedexID = pd.pokeId
            WHERE t.taldeIzena = ?
              AND t.erabiltzaileIzena = ?; \
            """

      pokemon_zerrenda = self.db.select(sql, [taldeIzena, erabiltzaileIzena])

      if not pokemon_zerrenda:
         return None

      # Bilatu puntuazio altuena duen pokemona
      onena = None
      puntuazio_maximoa = -1

      for row in pokemon_zerrenda:
         pokemon = dict(row)
         # Puntuazioa kalkulatu (estatistika guztien batura)
         puntuazioa = (
                 pokemon["HP"] +
                 pokemon["ATK"] +
                 pokemon["DEF"] +
                 pokemon["SPATK"] +
                 pokemon["SPDEF"] +
                 pokemon["SPE"]
         )

         # Puntuazioa gehitu pokemonaren datuei
         pokemon["puntuazioa"] = puntuazioa

         # Egiaztatu puntuazio maximoa den
         if puntuazioa > puntuazio_maximoa:
            puntuazio_maximoa = puntuazioa
            onena = pokemon

      if not onena:
         return None

      onena_info = {
         "PokemonPokedexID": onena["PokemonPokedexID"],
         "izena": onena["izena"],
         "irudia": onena["irudia"],
         "HP": onena["HP"],
         "ATK": onena["ATK"],
         "DEF": onena["DEF"],
         "SPATK": onena["SPATK"],
         "SPDEF": onena["SPDEF"],
         "SPE": onena["SPE"],
         "puntuazioa": onena["puntuazioa"],
         "taldeIzena": taldeIzena,
         "erabiltzaileIzena": erabiltzaileIzena
      }
      print("\n=== onena_info ===")
      print(f"Hiztegia: {onena_info}")
      for key, value in onena_info.items():
         print(f"  {key}: {value}")
      print("=== 结束 ===")
      return onena_info

   def create_simple_test_team(self):

      try:
         taldeIzena = "MY_TEST_TEAM"
         erabiltzaileIzena = "test_user"
         print(f"[INFO] Creating test team '{taldeIzena}' for user '{erabiltzaileIzena}'")

         # 1. 检查用户是否存在，如果不存在则创建
         sql_check_user = "INSERT OR IGNORE INTO Erabiltzailea (izena) VALUES (?)"
         self.db.insert(sql_check_user, [erabiltzaileIzena])
         print(f"✓ User '{erabiltzaileIzena}' created/verified")

         # 2. 删除已存在的测试队伍（避免重复）
         sql_delete_team = "DELETE FROM Taldea WHERE taldeIzena = ?"
         self.db.delete(sql_delete_team, [taldeIzena])
         print(f"✓ Deleted existing team '{taldeIzena}' if it existed")

         # 3. 创建队伍
         sql_team = "INSERT INTO Taldea (taldeIzena, erabiltzaileIzena) VALUES (?, ?)"
         self.db.insert(sql_team, [taldeIzena, erabiltzaileIzena])
         print(f"✓ Created team '{taldeIzena}'")

         # 4. 获取5个宝可梦
         sql_get_pokemon = "SELECT pokeId, izena FROM PokemonPokedex ORDER BY pokeId LIMIT 5"
         pokemons = self.db.select(sql_get_pokemon, [])

         if not pokemons:
            print("[ERROR] No pokemons in PokemonPokedex!")
            return False

         print(f"✓ Found {len(pokemons)} pokemons in Pokedex")

         # 5. 为每个宝可梦插入数据
         stat_sets = [
            (50, 50, 50, 50, 50, 50),  # 总分300
            (60, 60, 60, 60, 60, 60),  # 总分360
            (70, 70, 70, 70, 70, 70),  # 总分420
            (80, 80, 80, 80, 80, 80),  # 总分480
            (100, 100, 100, 100, 100, 100)  # 总分600
         ]

         for i, pokemon in enumerate(pokemons):
            poke_id = pokemon['pokeId']
            izena = f"{pokemon['izena']}_test_{i + 1}"  # 避免名称冲突

            if i < len(stat_sets):
               hp, atk, spatk, defense, spdef, spe = stat_sets[i]
            else:
               hp, atk, spatk, defense, spdef, spe = stat_sets[-1]

            # 添加其他必需字段
            maila = 50  # 默认级别
            adiskidetasun_maila = 70  # 默认亲密度
            generoa = ['Ar', 'Eme', 'Neutroa'][i % 3]  # 轮流分配性别

            # 5.1 插入统计数据到 PokemonTalde 表
            sql_stats = """
                        INSERT INTO PokemonTalde
                        (izena, maila, adiskidetasun_maila, generoa, HP, ATK, SPATK, DEF, SPDEF, SPE, PokemonPokedexID, \
                         ErabiltzaileIzena)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) \
                        """
            params = [
               izena,  # izena
               maila,  # maila
               adiskidetasun_maila,  # adiskidetasun_maila
               generoa,  # generoa
               hp,  # HP
               atk,  # ATK
               spatk,  # SPATK
               defense,  # DEF
               spdef,  # SPDEF
               spe,  # SPE
               poke_id,  # PokemonPokedexID
               erabiltzaileIzena  # ErabiltzaileIzena
            ]

            self.db.insert(sql_stats, params)

            # 5.2 添加到 PokemonTaldean 表（根据表结构，只有两个字段）
            sql_add_to_team = """
                              INSERT INTO PokemonTaldean (taldeIzena, pokeId)
                              VALUES (?, ?) \
                              """
            self.db.insert(sql_add_to_team, [taldeIzena, poke_id])

            total = hp + atk + spatk + defense + spdef + spe
            print(f"✓ Added {izena} (ID: {poke_id}) - Gender: {generoa} - Score: {total}")

         print(f"[SUCCESS] Team '{taldeIzena}' created successfully")
         return True

      except Exception as e:
         print(f"[ERROR] create_simple_test_team failed: {e}")
         import traceback
         traceback.print_exc()
         return False

   def delete_test_team(self):

      try:
         taldeIzena = "MY_TEST_TEAM"
         erabiltzaileIzena = "test_user"
         print(f"[INFO] Deleting test team '{taldeIzena}' for user '{erabiltzaileIzena}'")

         # 1. 首先获取队伍中的所有宝可梦ID
         sql_get_pokemon_ids = """
                               SELECT pt.pokeId \
                               FROM PokemonTaldean pt
                               WHERE pt.taldeIzena = ? \
                               """
         pokemon_ids = self.db.select(sql_get_pokemon_ids, [taldeIzena])

         # 2. 删除 PokemonTalde 表中的数据
         sql_delete_pokemon_stats = """
                                    DELETE \
                                    FROM PokemonTalde
                                    WHERE ErabiltzaileIzena = ?
                                      AND izena IN (SELECT izena \
                                                    FROM PokemonTalde \
                                                    WHERE izena LIKE '%_test_%' \
                                                       OR izena LIKE 'MY_TEST_TEAM%') \
                                    """
         stats_deleted = self.db.delete(sql_delete_pokemon_stats, [erabiltzaileIzena])
         print(f"✓ Deleted {stats_deleted} pokemon stats from PokemonTalde")

         # 3. 删除 PokemonTaldean 表中的关联数据
         sql_delete_team_assoc = """
                                 DELETE \
                                 FROM PokemonTaldean
                                 WHERE taldeIzena = ? \
                                 """
         assoc_deleted = self.db.delete(sql_delete_team_assoc, [taldeIzena])
         print(f"✓ Deleted {assoc_deleted} associations from PokemonTaldean")

         # 4. 删除 Taldea 表中的队伍
         sql_delete_team = """
                           DELETE \
                           FROM Taldea
                           WHERE taldeIzena = ? \
                             AND erabiltzaileIzena = ? \
                           """
         team_deleted = self.db.delete(sql_delete_team, [taldeIzena, erabiltzaileIzena])
         print(f"✓ Deleted {team_deleted} team from Taldea")

         # 5. 如果这是该用户的唯一队伍，也可以删除用户（可选）
         sql_check_other_teams = """
                                 SELECT COUNT(*) as count \
                                 FROM Taldea
                                 WHERE erabiltzaileIzena = ? \
                                 """
         result = self.db.select(sql_check_other_teams, [erabiltzaileIzena])
         if result and result[0]['count'] == 0:
            sql_delete_user = """
                              DELETE \
                              FROM Erabiltzailea
                              WHERE izena = ? \
                              """
            user_deleted = self.db.delete(sql_delete_user, [erabiltzaileIzena])
            print(f"✓ Deleted user '{erabiltzaileIzena}' (no other teams found)")

         print(f"[SUCCESS] Test team '{taldeIzena}' deleted successfully")
         return True

      except Exception as e:
         print(f"[ERROR] delete_test_team failed: {e}")
         import traceback
         traceback.print_exc()
         return False

# =====================================================
# NOTIFIKAZIOAK
# =====================================================
from app.database import db
# metodos
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