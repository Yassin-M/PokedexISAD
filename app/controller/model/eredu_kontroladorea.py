import pokebase as pb
import json
import os


class EreduKontroladorea:
   #metodos
   def __init__(self, db):
      self.db = db

   def taldeak_kargatu(self, erabiltzailea):
      sql1 = "SELECT taldeIzena FROM Taldea WHERE erabiltzaileIzena = ?"
      taldeak = self.db.select(sql1, (erabiltzailea,))

      json4 = [izena for taldea in taldeak for izena in [{'izena': taldea[0]}]]
      print("=== taldeak_kargatu 输出 ===")
      print(f"用户 '{erabiltzailea}' 的队伍列表:")
      print(f"JSON4: {json4}")
      print("=== 结束 ===")
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
      self.create_simple_test_team()

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
      i = 0
      erromatarrak = {'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7, 'viii': 8, 'ix': 9} # para conseguir el numero de la generacion (la api lo devuelve como "generation-xx")
      for pokemon in pb.APIResourceList('pokemon'):
         try:
            uneko_pokemon = pb.pokemon(pokemon['name'])
            izen_erreala = uneko_pokemon.species.name
            espeziea = pb.pokemon_species(izen_erreala)
            generoa_rate = espeziea.gender_rate
            generoa = 'Neutroa' if generoa_rate == -1 else 'Ar' if generoa_rate == 0 else 'Eme' if generoa_rate == 8 else 'Ar/Eme'
            irudia = uneko_pokemon.sprites.other.official_artwork.front_default
            if not irudia:
               irudia = uneko_pokemon.sprites.front_default
            base_parametroak = [uneko_pokemon.id, 
                                uneko_pokemon.name.capitalize(), 
                                uneko_pokemon.height, 
                                uneko_pokemon.weight, 
                                generoa, 
                                self.__lortu_deskripzioa(espeziea), 
                                irudia, 
                                erromatarrak.get(espeziea.generation.name.split('-')[1], 0)]
            self.db.insert(sql2, base_parametroak)
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
      icon_path = os.path.join(os.getcwd(), "app", "static", "icons")
      for mota in pb.APIResourceList('type'):
         try:
            if mota['name'] in ['unknown', 'shadow']:
                  continue
            irudia = f"{icon_path}/{mota['name']}.svg"

            self.db.insert(sql1, [mota['name'],irudia])
            tipo = pb.type_(mota['name'])
            for pokemon in tipo.pokemon:
               try:
                  pokemon_id = pb.pokemon(pokemon.pokemon.name).id
                  self.db.insert(sql2, [mota['name'], pokemon_id])
               except Exception as e:
                  print(f"Error {e}")
         except Exception as e:
            print(f"Error {e}")

      sql3 = "INSERT INTO Multiplikatzailea(pokemonMotaJaso, pokemonMotaEraso, multiplikatzailea) VALUES (?, ?, ?)"
      for mota in pb.APIResourceList('type'):
         tipo = pb.type_(mota['name'])
         dobles = tipo.damage_relations.double_damage_to
         mitades = tipo.damage_relations.half_damage_to
         zeros = tipo.damage_relations.no_damage_to
         for doble in dobles:
            parametroak = [doble.name, mota['name'], 2.0]
            self.db.insert(sql3, parametroak)
         for mitad in mitades:
            parametroak = [mitad.name, mota['name'], 0.5]
            self.db.insert(sql3, parametroak)
         for zero in zeros:
            parametroak = [zero.name, mota['name'], 0.0]
            self.db.insert(sql3, parametroak)
         #esta parte habra que ver como acortarla un poco

   def motak_irudiak_eguneratu_simple(self):
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

   def ikasdezake_mugimenduak_fix_all(self):
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
      sql2 = "INSERT OR IGNORE INTO IzanDezake (pokemonPokedexID, izena) VALUES (?, ?)"
      for abileziak in pb.APIResourceList('ability'):
         abilezia = pb.ability(abileziak['name'])
         abilezi_izena = abilezia.name
         for izena in abilezia.names:
            if izena.language.name == "es":
               abilezi_izena = izena.name
         deskripzioa = self.__lortu_deskripzioa(abilezia)
         self.db.insert(sql1, [abilezi_izena, deskripzioa])
         for pokemon in abilezia.pokemon:
            poke_id = pb.pokemon(pokemon.pokemon.name).id
            self.db.insert(sql2, [poke_id, abilezi_izena])
   
   def mugimenduak_kargatu(self):
      sql1 = "INSERT INTO Mugimendua (izena, potentzia, zehaztazuna, PP, efektua, pokemonMotaIzena) VALUES (?, ?, ?, ?, ?, ?)"
      sql2 = "INSERT INTO IkasDezake (pokedexId, mugiIzena) VALUES (?, ?)"
      for izena in pb.APIResourceList('move'):
         mugimendua = pb.move(izena['name'])
         mugimendu_izena = self.__lortu_izena(mugimendua)
         mugimendu_efektua = self.__lortu_deskripzioa(mugimendua)
         parametroak = [mugimendu_izena.capitalize(), mugimendua.power, mugimendua.accuracy, mugimendua.pp, mugimendu_efektua, mugimendua.type.name]
         self.db.insert(sql1, parametroak)
         for pokemon in mugimendua.learned_by_pokemon:
            pokemon_id = pb.pokemon(pokemon.name).id
            self.db.insert(sql2, [pokemon_id, mugimendu_izena])

   def eboluzioak_kargatu(self):
      """
      Eboluzio-kate guztiak kargatzeko
      """
      sql = "INSERT OR IGNORE INTO Eboluzioa (pokemonPokedexID, eboluzioaPokeId) VALUES (?, ?)"

      # Laguntza-funtzioa: URL-tik Pokémon ID atera
      def get_id_from_url(url):
         if not url:
            return None
         return int(url.rstrip('/').split('/')[-1])

      # Nodoa errekurtsiboki prozesatu
      def prozesatu_nodoa(nodoa, aurreko_id):
         if isinstance(nodoa, dict):
            species_url = nodoa.get("species", {}).get("url")
            evolves_to_list = nodoa.get("evolves_to", [])
         else:
            species_url = getattr(nodoa.species, 'url', None) if hasattr(nodoa, 'species') else None
            evolves_to_list = getattr(nodoa, 'evolves_to', [])

         if not species_url:
            return

         uneko_id = get_id_from_url(species_url)

         if aurreko_id is not None:
            # Eboluzio erlazioa datu-basera sartu
            self.db.insert(sql, [aurreko_id, uneko_id])

         for eboluzioa in evolves_to_list:
            prozesatu_nodoa(eboluzioa, uneko_id)

      # Evolution chain ID guztiak iteratu
      for i in range(1, 560):
         try:
            katea = pb.evolution_chain(i)
            if hasattr(katea, 'chain'):
               prozesatu_nodoa(katea.chain, None)
            elif isinstance(katea, dict) and 'chain' in katea:
               prozesatu_nodoa(katea['chain'], None)
         except:
            continue

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
      # 简单打印结果
      print("=== pokemon_zerrenda 查询结果 ===")
      print(f"查询参数: taldeIzena={taldeIzena}, erabiltzaileIzena={erabiltzaileIzena}")
      print(f"结果数量: {len(pokemon_zerrenda) if pokemon_zerrenda else 0}")
      if pokemon_zerrenda:
         for i, pokemon in enumerate(pokemon_zerrenda):
            print(f"宝可梦 {i + 1}: {pokemon}")
      else:
         print("没有找到任何宝可梦")
      print("=== 结束 ===")

      if pokemon_zerrenda:
         for i, row in enumerate(pokemon_zerrenda):
            # 将 Row 对象转换为字典
            pokemon_dict = dict(row)
            print(f"\n宝可梦 {i + 1}:")
            print(f"  ID: {pokemon_dict.get('PokemonPokedexID')}")
            print(f"  名称: {pokemon_dict.get('izena')}")
            print(f"  HP: {pokemon_dict.get('HP')}")
            print(f"  ATK: {pokemon_dict.get('ATK')}")
            print(f"  DEF: {pokemon_dict.get('DEF')}")
            print(f"  SPATK: {pokemon_dict.get('SPATK')}")
            print(f"  SPDEF: {pokemon_dict.get('SPDEF')}")
            print(f"  SPE: {pokemon_dict.get('SPE')}")
            print(f"  图片: {pokemon_dict.get('irudia')}")
      else:
         print("没有找到任何宝可梦")
      print("=== 结束 ===")

      if not pokemon_zerrenda:
         return None

      # Bilatu puntuazio altuena duen pokemona
      onena = None
      puntuazio_maximoa = -1

      for row in pokemon_zerrenda:
         # 将 Row 对象转换为字典
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
      print(f"\n最终选择的 onena:")
      if onena:
         print(f"  宝可梦名称: {onena['izena']}")
         print(f"  宝可梦ID: {onena['PokemonPokedexID']}")
         print(f"  总分: {onena['puntuazioa']}")
         print(f"  详细数据:")
         print(f"    HP: {onena['HP']}")
         print(f"    ATK: {onena['ATK']}")
         print(f"    DEF: {onena['DEF']}")
         print(f"    SPATK: {onena['SPATK']}")
         print(f"    SPDEF: {onena['SPDEF']}")
         print(f"    SPE: {onena['SPE']}")
      else:
         print("  没有找到最强宝可梦 (onena is None)")

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
      print("\n=== onena_info 字典 ===")
      print(f"完整字典: {onena_info}")
      print("\n键值对详情:")
      for key, value in onena_info.items():
         print(f"  {key}: {value}")
      print("=== 结束 ===")
      return onena_info

   def create_simple_test_team(self):
      """
      直接创建测试队伍，不检查，直接插入
      """
      try:
         taldeIzena = "MY_TEST_TEAM"
         erabiltzaileIzena = "test_user"
         print(f"[INFO] Creating test team '{taldeIzena}' for user '{erabiltzaileIzena}'")

         # 1. 检查用户是否存在，如果不存在则创建
         sql_check_user = "INSERT OR IGNORE INTO Erabiltzailea (izena) VALUES (?)"
         self.db.insert(sql_check_user, [erabiltzaileIzena])
         print(f"✓ User '{erabiltzaileIzena}' created/verified")

         # 2. 删除已存在的测试队伍（避免重复）

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


