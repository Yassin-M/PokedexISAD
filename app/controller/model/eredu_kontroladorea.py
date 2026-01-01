import pokebase as pb
import json

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
      icon_path = "static/icons"
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


   def eboluzioak(self):
      """检查并加载进化数据"""
      if not self.eboluzioak_konprobatu():
         self.eboluzioak_kargatu()

   def eboluzioak_kargatu(self):
      """
      直接遍历进化链 ID，从 URL 解析 ID，避免重复和多余的 API 请求。
      """
      insert_sql = """
                   INSERT \
                   OR IGNORE INTO Eboluzioa (pokemonPokedexID, eboluzioaPokeId)
           VALUES (?, ?) \
                   """

      # 辅助函数：从 URL 字符串中提取 ID
      def get_id_from_url(url):
         if not url:
            return None
         # split 之后倒数第二个元素通常是 ID (因为末尾有个 /)
         return int(url.rstrip('/').split('/')[-1])

      # 递归处理函数
      def process_chain_node(node):
         """递归处理进化链节点"""
         # 调试：打印当前节点
         # print(f"Processing node: {node.get('species', {}).get('name', 'unknown')}")

         # 1. 获取当前节点（进化前）的 ID
         if isinstance(node, dict):
            current_species_url = node.get("species", {}).get("url")
         else:
            # 如果是对象
            current_species_url = getattr(node.species, 'url', None) if hasattr(node, 'species') else None

         if not current_species_url:
            return

         current_id = get_id_from_url(current_species_url)

         # 2. 获取 evolves_to 列表
         if isinstance(node, dict):
            evolves_to_list = node.get("evolves_to", [])
         else:
            evolves_to_list = getattr(node, 'evolves_to', [])

         # 3. 遍历进化的分支
         for evolution in evolves_to_list:
            if isinstance(evolution, dict):
               next_species_url = evolution.get("species", {}).get("url")
            else:
               next_species_url = getattr(evolution.species, 'url', None) if hasattr(evolution, 'species') else None

            if not next_species_url:
               continue

            next_id = get_id_from_url(next_species_url)

            # 4. 插入数据库 (当前 -> 下一阶)
            if current_id and next_id:
               print(f"插入: {current_id} -> {next_id}")  # 调试输出
               self.db.insert(insert_sql, [current_id, next_id])

            # 5. 递归处理下一阶 (例如处理 妙蛙草 -> 妙蛙花)
            process_chain_node(evolution)

      # 主循环：遍历所有进化链
      print("开始加载进化链...")
      success_count = 0
      failed_count = 0
      total_evolutions = 0

      for i in range(1, 560):
         try:
            # 请求进化链数据
            chain_response = pb.evolution_chain(i)

            # 调试：打印返回数据类型
            if i == 1:
               print(f"chain_response 类型: {type(chain_response)}")
               if hasattr(chain_response, '__dict__'):
                  print(f"chain_response 属性: {chain_response.__dict__.keys()}")

            # 兼容不同的返回格式
            chain_data = None
            if hasattr(chain_response, 'chain'):
               # 如果是对象封装
               chain_data = chain_response.chain
            elif isinstance(chain_response, dict) and 'chain' in chain_response:
               # 如果是字典
               chain_data = chain_response['chain']
            else:
               # 尝试直接使用
               chain_data = chain_response

            if not chain_data:
               failed_count += 1
               continue

            # 开始递归处理
            process_chain_node(chain_data)
            success_count += 1

            # 每处理10条显示进度（改为10方便调试）
            if success_count % 10 == 0:
               print(f"已处理 {success_count} 条进化链...")

         except Exception as e:
            # 某些 ID 可能跳过了或者是空的
            failed_count += 1
            print(f"Chain {i} 失败: {e}")  # 显示错误信息
            continue

      # 统计总数
      result = self.db.select("SELECT COUNT(*) FROM Eboluzioa")
      if result:
         total_evolutions = result[0][0]

      print(f"进化链加载完成。成功: {success_count}, 失败: {failed_count}")
      print(f"数据库中共有 {total_evolutions} 条进化记录")
      self.db.commit()  # 确保提交所有更改

   def eboluzioak_konprobatu(self):
      """检查进化表是否已有数据"""
      return len(self.db.select("SELECT * FROM Eboluzioa LIMIT 2")) > 0


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
      sql = """
            SELECT p.izena   AS pokemon_izena,
                   p.irudia  AS pokemon_irudia,
                   t.irudia  AS pokemon_mota_irudia,
                   m.pokemonMotaEraso,
                   m.multiplikatzailea,
                   tm.irudia AS erasoko_mota_irudia
            FROM PokemonPokedex p
                    LEFT JOIN DaMotaPokemon d ON p.pokeId = d.pokemonID
                    LEFT JOIN MotaPokemon t ON d.MotaIzena = t.pokemonMotaIzena
                    LEFT JOIN Multiplikatzailea m ON d.MotaIzena = m.PokemonMotaJaso
                    LEFT JOIN MotaPokemon tm ON tm.pokemonMotaIzena = m.PokemonMotaEraso
            WHERE p.pokeId = ? \
            """
      errenkadak = self.db.select(sql, [pokeId])

      if not errenkadak:
         return None

      # Pokemon-en oinarrizko informazioa
      pokemon_info = {
         "izena": errenkadak[0]["pokemon_izena"],
         "irudia": errenkadak[0]["pokemon_irudia"],
         "mota_irudia": errenkadak[0]["pokemon_mota_irudia"]
      }

      indarrak = []
      ahuleziak = []

      for unekoa in errenkadak:
         if unekoa["multiplikatzailea"] is not None:
            if unekoa["multiplikatzailea"] > 1:
               indarrak.append({
                  "izena": unekoa["pokemonMotaEraso"],
                  "irudia": unekoa["erasoko_mota_irudia"]
               })
            elif unekoa["multiplikatzailea"] < 1:
               ahuleziak.append({
                  "izena": unekoa["pokemonMotaEraso"],
                  "irudia": unekoa["erasoko_mota_irudia"]
               })

      pokemon_info["indarrak"] = indarrak
      pokemon_info["ahuleziak"] = ahuleziak

      return json.dumps(pokemon_info, ensure_ascii=False)

   def getEboluzioa(self, pokemon_id):
      # 初始化列表
      aurrekoak = []
      hurrengoak = []

      visited = set()  # 已访问宝可梦ID，防止重复
      to_visit_aurreko = [pokemon_id]  # 待访问前置进化队列
      to_visit_hurrengo = [pokemon_id]  # 待访问后续进化队列

      # 迭代获取所有前置进化
      while to_visit_aurreko:
         current_id = to_visit_aurreko.pop(0)
         if current_id in visited:
            continue
         visited.add(current_id)

         sql = """
               SELECT P.pokeId, P.izena, P.irudia
               FROM Eboluzioa E
                       JOIN PokemonPokedex P ON E.pokemonPokedexID = P.pokeId
               WHERE E.eboluzioaPokeID = ? \
               """
         rows = self.db.select(sql, [current_id])
         for row in rows:
            aurrekoak.append({
               "id": row["pokeId"],
               "izena": row["izena"],
               "irudia": row["irudia"]
            })
            if row["pokeId"] not in visited:
               to_visit_aurreko.append(row["pokeId"])

      visited.clear()  # 重置已访问，用于后续进化
      # 迭代获取所有后续进化
      while to_visit_hurrengo:
         current_id = to_visit_hurrengo.pop(0)
         if current_id in visited:
            continue
         visited.add(current_id)

         sql = """
               SELECT P.pokeId, P.izena, P.irudia
               FROM Eboluzioa E
                       JOIN PokemonPokedex P ON E.eboluzioaPokeID = P.pokeId
               WHERE E.pokemonPokedexID = ? \
               """
         rows = self.db.select(sql, [current_id])
         for row in rows:
            hurrengoak.append({
               "id": row["pokeId"],
               "izena": row["izena"],
               "irudia": row["irudia"]
            })
            if row["pokeId"] not in visited:
               to_visit_hurrengo.append(row["pokeId"])

      # 获取当前宝可梦信息
      sql_current = "SELECT izena, irudia FROM PokemonPokedex WHERE pokeId = ?"
      current_row = self.db.select(sql_current, [pokemon_id])
      if not current_row:
         return None

      pokemon_info = {
         "izena": current_row[0]["izena"],
         "irudia": current_row[0]["irudia"],
         "aurrekoak": aurrekoak,
         "hurrengoak": hurrengoak
      }

      return pokemon_info

   def eboluzioa_kargatu(self):
      """
      加载所有宝可梦进化数据到 Eboluzioa 表
      """
      sql = "INSERT OR IGNORE INTO Eboluzioa (pokemonPokedexID, eboluzioaPokeId) VALUES (?, ?)"

      import time

      try:
         print("开始获取进化链列表...")
         evolution_chains_list = pb.APIResourceList('evolution-chain', limit=1000)
         print(f"成功获取 {len(evolution_chains_list)} 条进化链")

         total_inserted = 0

         for i, chain_resource in enumerate(evolution_chains_list):
            try:
               if i % 20 == 0:
                  print(f"处理进度: {i}/{len(evolution_chains_list)}")

               chain_url = chain_resource['url']
               chain_id = chain_url.rstrip('/').split('/')[-1]
               if not chain_id.isdigit():
                  print(f"警告: 无法从 URL 提取有效 ID: {chain_url}")
                  continue

               # 延迟避免 API 限制
               if i > 0:
                  time.sleep(0.1)

               evolution_chain_data = pb.evolution_chain(int(chain_id))

               # 用栈迭代遍历进化链
               stack = [(evolution_chain_data.chain, None)]
               while stack:
                  current_node, parent_id = stack.pop()

                  species_name = current_node.species.name
                  try:
                     pokemon_info = pb.pokemon(species_name)
                     current_id = pokemon_info.id

                     if parent_id is not None:
                        # 打印调试信息
                        print(f"插入进化关系: {parent_id} -> {current_id}")
                        self.db.insert(sql, [parent_id, current_id])
                        total_inserted += 1

                  except Exception as e:
                     print(f"获取宝可梦 {species_name} 信息失败: {e}")
                     continue

                  # 将子节点加入栈中
                  for child_node in current_node.evolves_to:
                     stack.append((child_node, current_id))

            except Exception as e:
               print(f"进化链 {chain_id} 处理失败: {e}")
               continue

         print(f"进化数据加载完成！共插入 {total_inserted} 条进化关系")

      except Exception as e:
         print(f"加载进化链列表失败: {e}")
         import traceback
         traceback.print_exc()







