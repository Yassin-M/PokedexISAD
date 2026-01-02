import pokebase as pb
import json
import os


class EreduKontroladorea:
   #metodos
   def __init__(self, db):
      self.db = db

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
      Eboluzio-kate guztiak kargatzeko（优化版，无进度显示）
      """
      sql = "INSERT OR IGNORE INTO Eboluzioa (pokemonPokedexID, eboluzioaPokeId) VALUES (?, ?)"

      # 辅助函数：从 URL 中提取 Pokémon ID
      def get_id_from_url(url):
         if not url:
            return None
         return int(url.rstrip('/').split('/')[-1])

      # 递归处理节点
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
            self.db.insert(sql, [aurreko_id, uneko_id])

         for eboluzioa in evolves_to_list:
            prozesatu_nodoa(eboluzioa, uneko_id)

      # 遍历 evolution chain ID
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
      # 首先获取Pokemon自身的所有属性
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

      # 获取Pokemon基本信息
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
         "pokemon_motak": pokemon_motak  # 添加Pokemon自身的属性
      }

      # 收集Pokemon所有属性的强弱点
      indarrak_set = set()  # 使用set避免重复
      ahuleziak_set = set()

      for pokemon_mota in pokemon_motak:
         mota_izena = pokemon_mota["izena"]

         # 查询这个属性攻击其他属性时的效果
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
               # 如果攻击效果>1，是这个Pokemon的强点（对什么属性有优势）
               indarrak_set.add((efektu_item["izena"], efektu_item["irudia"]))
            elif efektua["multiplikatzailea"] < 1:
               # 如果攻击效果<1，是这个Pokemon的弱点（对什么属性劣势）
               ahuleziak_set.add((efektu_item["izena"], efektu_item["irudia"]))

      # 转换set到list
      pokemon_info["indarrak"] = [{"izena": izena, "irudia": irudia}
                                  for izena, irudia in indarrak_set]
      pokemon_info["ahuleziak"] = [{"izena": izena, "irudia": irudia}
                                   for izena, irudia in ahuleziak_set]

      return pokemon_info

   def getEboluzioa(self, poke_id):
      """
      Jasotzen du pokemon baten aurreko eta hurrengo evoluzioak.
      pokemon_id : bilatu nahi den pokemona
      Bueltatzen du dict bat: izena, irudia, aurrekoak, hurrengoak
      """
      aurrekoak, hurrengoak = [], []

      def bilatu_evoluzioak(start_id, aurreko=True):
         """
         Iteratiboki jasotzen ditu evoluzioak.
         start_id : Pokemonaren ID hasierakoa
         aurreko : True → aurreko evoluzioak, False → hurrengo evoluzioak
         """
         emaitza = []  # Bilatutako evoluzioak gordetzeko lista
         bisitatuak = set()  # Errepikapenak saihesteko ID multzoa
         itzuli = [start_id]  # Bisitatu beharreko ID zerrenda

         while itzuli:
            unekoa = itzuli.pop(0)  # Uneko pokemona
            if unekoa in bisitatuak:
               continue
            bisitatuak.add(unekoa)  # Markatu bisitatu bezala

            # SQL, aurreko edo hurrengo evoluzioak lortzeko
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

            # Emaitzak gehitu eta hurrengo bisitak prestatu
            for unekoa_info in self.db.select(sql, [unekoa]):
               emaitza.append(unekoa_info)
               if unekoa_info["pokeId"] not in bisitatuak:
                  itzuli.append(unekoa_info["pokeId"])

         return emaitza

      # Aurreko eta hurrengo evoluzioak lortu
      aurrekoak = bilatu_evoluzioak(poke_id, aurreko=True)
      hurrengoak = bilatu_evoluzioak(poke_id, aurreko=False)

      # Oraingo pokemona lortu
      unekoa = self.db.select("SELECT izena, irudia FROM PokemonPokedex WHERE pokeId = ?", [poke_id])
      if not unekoa:
         return None

      # Bueltatu pokemona info osoa
      return {
         "izena": unekoa[0]["izena"],
         "irudia": unekoa[0]["irudia"],
         "aurrekoak": aurrekoak,
         "hurrengoak": hurrengoak
      }





