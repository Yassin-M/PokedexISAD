from datetime import datetime
from urllib.response import addinfo
from app.database.database import Connection
import json
import sqlite3
import os
import random
from .api_kontroladorea import APIKontroladorea
from app.database import db

class EreduKontroladorea:
  def __init__(self, db):
    self.db = db
    self.api = APIKontroladorea()

  # =====================================================
  # ERABILTZAILEA
  # =====================================================

  def saioHasi(self, erabiltzaile_izena, pasahitza):
      """Kredentzialak egiaztatu datu-basean"""
      query = "SELECT izena, pasahitza, rola FROM Erabiltzailea WHERE izena = ?"
      emaitza = self.db.select(query, (erabiltzaile_izena,))
      erabiltzailea = emaitza[0] if emaitza else None
      
      if not erabiltzailea:
         return json.dumps({
            'ondo': False,
            'erabiltzaile_izena': None,
            'rola': None,
            'mezua': "Erabiltzailea ez da existitzen"
         }, ensure_ascii=False)
      
      
      pasahitza_zuzena = erabiltzailea['pasahitza'] == pasahitza

      if pasahitza_zuzena:
         return json.dumps({
            'ondo': True,
            'erabiltzaile_izena': erabiltzailea['izena'],
            'rola': erabiltzailea['rola'],
            'mezua': "Saioa hasi da"
         }, ensure_ascii=False)
      else:
         return json.dumps({
            'ondo': False,
            'erabiltzaile_izena': None,
            'rola': None,
            'mezua': "Pasahitza okerra"
         }, ensure_ascii=False)
   
  def balioztatu_pasahitza(self, pasahitza, pasahitza_berretsi):
    """Pasahitzak balioztatu eta JSON itzuli"""
    karaktere_debekatuak = "|'¬£$^;#~=@"
    
    if pasahitza != pasahitza_berretsi:
      return json.dumps({
        'ondo': False,
        'mezua': "Pasahitzak ez datoz bat"
      }, ensure_ascii=False)
    
    for karakterea in pasahitza:
      if karakterea in karaktere_debekatuak:
        return json.dumps({
          'ondo': False,
          'mezua': f"Pasahitzak ezin du karaktere hau izan: {karakterea}"
        }, ensure_ascii=False)
    
    return json.dumps({
      'ondo': True,
      'mezua': "Pasahitza zuzena"
    }, ensure_ascii=False)

  def erregistratu(self, izena, email, jaiotze_data, pasahitza, pasahitza_berretsi):
    """Erabiltzaile berria datu-basean erregistratu"""
    query = "SELECT izena FROM Erabiltzailea WHERE izena = ?"
    dagoen_erabiltzaile = self.db.select(query, (izena,))
    if dagoen_erabiltzaile:
      return False, "Erabiltzailea jada existitzen da"
    
    baliozkotze_json = self.balioztatu_pasahitza(pasahitza, pasahitza_berretsi)
    baliozkotze = json.loads(baliozkotze_json or '{}')
    if not baliozkotze.get('ondo'):
      return False, baliozkotze.get('mezua', "Pasahitza ez da baliozkoa")
    
    query = "INSERT INTO Erabiltzailea (izena, pasahitza, email, jaiotze_data, rola) VALUES (?, ?, ?, ?, ?)"
    try:
      self.db.insert(query, (izena, pasahitza, email, jaiotze_data, 'usuario'))
      return True, "Erabiltzailea behar bezala erregistratu da"
    except sqlite3.IntegrityError:
      return False, "Erabiltzailea jada existitzen da"
    except Exception as e:
      return False, f"Errorea erabiltzailea erregistratzerakoan: {str(e)}"

  def eguneratu_erabiltzailea(self, izena_zaharra, izena_berria=None, email=None, jaiotze_data=None, pasahitza=None):
    """Erabiltzaile datuak eguneratu datu-basean (soilik aldatutako datuak)"""
    try:
      query = "SELECT izena, pasahitza, rola FROM Erabiltzailea WHERE izena = ?"
      emaitza = self.db.select(query, (izena_zaharra,))
      erabiltzailea_zaharra = emaitza[0] if emaitza else None
      if not erabiltzailea_zaharra:
        return json.dumps({
          'ondo': False,
          'mezua': "Erabiltzailea ez da existitzen"
        }, ensure_ascii=False)
      
      if not izena_berria or izena_berria == "":
        izena_berria = izena_zaharra
      if not email or email == "":
        query = "SELECT email FROM Erabiltzailea WHERE izena = ?"
        result = self.db.select(query, (izena_zaharra,))
        email = result[0]['email'] if result else None
      if not jaiotze_data or jaiotze_data == "":
        query = "SELECT jaiotze_data FROM Erabiltzailea WHERE izena = ?"
        result = self.db.select(query, (izena_zaharra,))
        jaiotze_data = result[0]['jaiotze_data'] if result else None
      
        if izena_berria != izena_zaharra:
          query = "SELECT izena FROM Erabiltzailea WHERE izena = ?"
          dagoen_berria = self.db.select(query, (izena_berria,))
          if dagoen_berria:
            return json.dumps({
              'ondo': False,
              'mezua': "Izen hori hartuta dago"
            }, ensure_ascii=False)
      
      if pasahitza and pasahitza != "":
        query = "UPDATE Erabiltzailea SET izena = ?, email = ?, jaiotze_data = ?, pasahitza = ? WHERE izena = ?"
        self.db.update(query, (izena_berria, email, jaiotze_data, pasahitza, izena_zaharra))
      else:
        query = "UPDATE Erabiltzailea SET izena = ?, email = ?, jaiotze_data = ? WHERE izena = ?"
        self.db.update(query, (izena_berria, email, jaiotze_data, izena_zaharra))
      
      return json.dumps({
        'ondo': True,
        'mezua': "Datuak behar bezala eguneratu dira"
      }, ensure_ascii=False)
    except Exception as e:
      return json.dumps({
        'ondo': False,
        'mezua': f"Errorea datuak eguneratzerakoan: {str(e)}"
      }, ensure_ascii=False)

  def erabiltzaileakKargatu(self):
    """Datu-baseko erabiltzaile guztiak lortu JSON formatuan"""
    query = "SELECT izena, email, rola, jaiotze_data FROM Erabiltzailea ORDER BY izena"
    try:
      erabiltzaileak = self.db.select(query)
      erabiltzaileak_lista = []
      for erabiltzaile in erabiltzaileak:
        erabiltzaileak_lista.append({
          'id': erabiltzaile['izena'],
          'izena': erabiltzaile['izena'],
          'email': erabiltzaile['email'],
          'admin': 1 if erabiltzaile['rola'] == 'admin' else 0,
          'jaiotze_data': erabiltzaile['jaiotze_data']
        })
      return json.dumps(erabiltzaileak_lista, ensure_ascii=False)
    except Exception as e:
      print(f"Errorea erabiltzaileak lortzerakoan: {str(e)}")
      return json.dumps([], ensure_ascii=False)

  def lortu_erabiltzaile_bat(self, erabiltzaile_izena):
    """Erabiltzaile bat lortu datu-basetik - KUDEATU ATALERAKO"""
    query = "SELECT izena, pasahitza, rola, email, jaiotze_data FROM Erabiltzailea WHERE izena = ?"
    try:
      emaitza = self.db.select(query, (erabiltzaile_izena,))
      return emaitza[0] if emaitza else None
    except Exception as e:
      print(f"Errorea erabiltzailea lortzerakoan: {str(e)}")
      return None

  def ezabatu(self, erabiltzaile_izena):
    """Erabiltzaile bat ezabatu datu-basetik"""
    query = "DELETE FROM Erabiltzailea WHERE izena = ?"
    try:
      self.db.delete(query, (erabiltzaile_izena,))
      return json.dumps({
        'ondo': True,
        'mezua': "Erabiltzailea behar bezala ezabatu da"
      }, ensure_ascii=False)
    except Exception as e:
      return json.dumps({
        'ondo': False,
        'mezua': f"Errorea erabiltzailea ezabatzerakoan: {str(e)}"
      }, ensure_ascii=False)

  def baimendu(self, erabiltzaile_izena, admin_egin):
    """Erabiltzaile bati admin rola eman edo kendu"""
    rola_berria = 'admin' if admin_egin else 'usuario'
    query = "UPDATE Erabiltzailea SET rola = ? WHERE izena = ?"
    try:
      self.db.update(query, (rola_berria, erabiltzaile_izena))
      mezua = "Erabiltzailea admin bihurtu da" if admin_egin else "Admin rola kendu da"
      return json.dumps({
        'ondo': True,
        'mezua': mezua
      }, ensure_ascii=False)
    except Exception as e:
      return json.dumps({
        'ondo': False,
        'mezua': f"Errorea rola aldatzerakoan: {str(e)}"
      }, ensure_ascii=False)

  def lagunakKargatu(self, erabiltzaile_izena):
    """Erabiltzaile batek jarraitzen dituen pertsonak lortu"""
    query = """
      SELECT JarraituIzena, Notifikatu
      FROM JarraitzenDu 
      WHERE JarraitzaileIzena = ?
      ORDER BY JarraituIzena
    """
    try:
      emaitza = self.db.select(query, (erabiltzaile_izena,))
      jarraitutakoak = []
      for jarraitua in emaitza:
        jarraitutakoak.append({
          'izena': jarraitua['JarraituIzena'],
          'notifikazioak': bool(jarraitua['Notifikatu'])
        })
      return json.dumps(jarraitutakoak, ensure_ascii=False)
    except Exception as e:
      print(f"Errorea jarraitutakoak lortzerakoan: {str(e)}")
      return json.dumps([], ensure_ascii=False)

  def utzi_jarraitzen(self, jarraitzailea, jarraitua):
    """Erabiltzaile bat jarraitzen uztea"""
    query = "DELETE FROM JarraitzenDu WHERE JarraitzaileIzena = ? AND JarraituIzena = ?"
    try:
      self.db.delete(query, (jarraitzailea, jarraitua))
      dataOrdua = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      self.notifikazioBerria(jarraitzailea, dataOrdua, f"{jarraitzailea} erabiltzaileak {jarraitua} jarraitzen uzti du.")
      self.notifikazioBerria(jarraitua, dataOrdua, f"{jarraitzailea} erabiltzaileak {jarraitua} jarraitzen utzi du.")
      return json.dumps({
        'ondo': True,
        'mezua': "Jarraitzea eten da"
      }, ensure_ascii=False)
    except Exception as e:
      return json.dumps({
        'ondo': False,
        'mezua': f"Errorea jarraitzea eteterakoan: {str(e)}"
      }, ensure_ascii=False)

  def gehituErabiltzailea(self, jarraitzailea, jarraitua):
    """Erabiltzaile bat jarraitzen hastea"""
    query = "SELECT * FROM JarraitzenDu WHERE JarraitzaileIzena = ? AND JarraituIzena = ?"
    emaitza = self.db.select(query, (jarraitzailea, jarraitua))
    
    if emaitza:
      return json.dumps({
        'ondo': False,
        'mezua': "Jada jarraitzen duzu erabiltzaile hau"
      }, ensure_ascii=False)
    
    if jarraitzailea == jarraitua:
      return json.dumps({
        'ondo': False,
        'mezua': "Ezin duzu zure burua jarraitu"
      }, ensure_ascii=False)
    
    query = "INSERT INTO JarraitzenDu (JarraitzaileIzena, JarraituIzena) VALUES (?, ?)"
    try:
      self.db.insert(query, (jarraitzailea, jarraitua))
      dataOrdua = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      self.notifikazioBerria(jarraitzailea, dataOrdua, f"{jarraitzailea} erabiltzaileak {jarraitua} jarraitzen hasi da.")
      self.notifikazioBerria(jarraitua, dataOrdua, f"{jarraitzailea} erabiltzaileak {jarraitua} jarraitzen hasi da.")
      return json.dumps({
        'ondo': True,
        'mezua': "Orain jarraitzen duzu erabiltzaile hau"
      }, ensure_ascii=False)
    except Exception as e:
      return json.dumps({
        'ondo': False,
        'mezua': f"Errorea jarraitzen hastean: {str(e)}"
      }, ensure_ascii=False)

  def bilatu_erabiltzaileak(self, bilaketa, current_user):
    """Erabiltzaileak bilatu izenaren arabera - LAGUNAK GEHITU ATALERAKO"""
    query = """SELECT E.Izena AS izena, E.Email AS email
          FROM Erabiltzailea E 
          WHERE E.Izena LIKE ? AND E.Izena != ?
          ORDER BY E.Izena"""
    try:
      bilaketa_pattern = f"%{bilaketa}%"
      emaitza = self.db.select(query, (bilaketa_pattern, current_user))
      erabiltzaileak = []
      for erabiltzaile in emaitza:
        query_jarraitzen = "SELECT * FROM JarraitzenDu WHERE JarraitzaileIzena = ? AND JarraituIzena = ?"
        jarraitzen_emaitza = self.db.select(query_jarraitzen, (current_user, erabiltzaile['izena']))
        
        erabiltzaileak.append({
          'izena': erabiltzaile['izena'],
          'email': erabiltzaile['email'],
          'jarraitzen': len(jarraitzen_emaitza) > 0
        })
      return json.dumps(erabiltzaileak, ensure_ascii=False)
    except Exception as e:
      print(f"Errorea erabiltzaileak bilatzerakoan: {str(e)}")
      return json.dumps([], ensure_ascii=False)

  def eguneratu_notifikazioak(self, jarraitzailea, jarraitua, notifikazioak):
    """Notifikazio baten egoera aldatu (aktibatu/desgaitu)"""
    query = "UPDATE JarraitzenDu SET Notifikatu = ? WHERE JarraitzaileIzena = ? AND JarraituIzena = ?"
    try:
      self.db.update(query, (notifikazioak, jarraitzailea, jarraitua))
      return json.dumps({
        'ondo': True,
        'mezua': "Notifikazioak eguneratuta daude"
      }, ensure_ascii=False)
    except Exception as e:
      return json.dumps({
        'ondo': False,
        'mezua': f"Errorea notifikazioak eguneratzerakoan: {str(e)}"
      }, ensure_ascii=False)

  # =====================================================
  # TALDEAK
  # =====================================================

  def taldeak_kargatu(self, erabiltzailea):
    # Erabiltzaileak dituen taldeak lortu
    sql_taldeak = "SELECT taldeIzena FROM Taldea WHERE erabiltzaileIzena = ?"
    taldeak = self.db.select(sql_taldeak, (erabiltzailea,))

    # Taldeen izena gorde eta bueltatu JSON formatuan
    json_izenak = [izena for taldea in taldeak for izena in [{'izena': taldea[0]}]]
    return json_izenak
  
  def sortu_taldea_hutsa(self, erabiltzailea):
    # Erabiltzaileak dituen taldeak lortu
    sql_taldeak = "SELECT taldeIzena FROM Taldea WHERE erabiltzaileIzena = ?"
    taldeKop = self.db.select(sql_taldeak, (erabiltzailea,))

    # Erabiltzaileak dituen taldeak kontatu eta izen egokia bilatu
    zenbakiak = set()
    for (izena,) in taldeKop:
      if izena.startswith("Talde "):
            try:
              zenb = int(izena.split(" ")[1])
              zenbakiak.add(zenb)
            except ValueError:
                pass

    # 10 talde baditu erabiltzaileak, errorea jaurtitu
    if len(zenbakiak) >= 10:      
      raise ValueError("Ezin dira 10 talde baino gehiago eduki.")
    # Bestela kontatu zenbat talde dituen, izen aproposa bilatzeko
    else:
      i = 1
      while i in zenbakiak:
        i += 1

      # Taldearen izena ezarri eta insert query-a prestatu
      taldeIzena = f"Talde {i}"
      sql_sortu = " INSERT INTO taldea (taldeIzena, erabiltzaileIzena) VALUES (?, ?)"
      self.db.insert(sql_sortu, (taldeIzena, erabiltzailea))
      # Taldearen izena bueltatu notifikazioa sortu aurretik
      return taldeIzena
    
  def get_taldea(self, taldeIzena, erabiltzailea):
    # Taldearen pokémon guztiak lortu
    sql_poketalde = "SELECT PT.harrapatuId, PP.irudia FROM Taldea T JOIN PokemonTaldean PT  ON T.taldeIzena = PT.taldeIzena JOIN PokemonTalde PKT ON PT.harrapatuId = PKT.harrapatuId JOIN PokemonPokedex PP ON PKT.PokemonPokedexID = PP.pokeId WHERE T.erabiltzaileIzena = ? AND T.taldeIzena = ?"
    taldea = self.db.select(sql_poketalde, (erabiltzailea, taldeIzena))

    # Pokémonen ID-ak eta irudiak gorde eta bueltatu JSON formatuan
    json_poketalde = [ {'pokeID': pokeID, 'argazkia': irudia} for (pokeID, irudia) in taldea ]
    return json_poketalde
  
  def sartu_taldera(self, taldeIzena, erabiltzailea, pokemonId):
    # Taldearen tamaina kontrolatu
    sql_tamaina = "SELECT COUNT(*) as count FROM PokemonTaldean PT JOIN Taldea T ON PT.taldeIzena = T.taldeIzena WHERE T.erabiltzaileIzena = ? AND T.taldeIzena = ?"
    count_result = self.db.select(sql_tamaina, (erabiltzailea, taldeIzena))
    # 6 pokemon baino gehiago badaude taldean, errorea jaurtitu
    if count_result and count_result[0]['count'] >= 6:
        raise ValueError("Ezin dira 6 pokémon baino gehiago sartu talde batean")

    try:
        # Pokemon-ak dituen estatistikak lortu API-tik
        stats = self.api.hartu_stats(pokemonId)

        # Izango dituen estatistikak kalkulatu
        hp = int(stats.get('hp', 40) * 2)
        atk = int(stats.get('attack', 40) * 1.5)
        spatk = int(stats.get('special-attack', 40) * 1.5)
        def_ = int(stats.get('defense', 40) * 1.5)
        spdef = int(stats.get('special-defense', 40) * 1.5)
        spe = int(stats.get('speed', 40) * 1.5)
        izena = self.api.pokemon_izena_lortu(pokemonId)
        
        # Harrapatutako pokemon-a izango duen generoa aukeratu
        sql_generoa = "SELECT generoa FROM PokemonPokedex WHERE pokeId = ?"
        aukerak = self.db.select(sql_generoa, (pokemonId,))
        generoak = aukerak[0]['generoa'].split('/')
        generoa = random.choice(generoak)

        # Pokemon-a PokemonTalde taulan sartu
        sql_harrapatu = """
              INSERT INTO PokemonTalde 
              (izena, maila, adiskidetasun_maila, generoa, HP, ATK, SPATK, DEF, SPDEF, SPE, PokemonPokedexID, ErabiltzaileIzena) 
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
          """
          # Defektuz maila 50 eta adiskidetasuna 0
        self.db.insert(sql_harrapatu, (izena, 50, 0, generoa, hp, atk, spatk, def_, spdef, spe, pokemonId, erabiltzailea))

    except Exception as e:
        print(f"Errorea API deian edo txertatzean: {e}")

    # Azken harrapatuId-a lortu behar dugu abileziak eta mugimenduak lortzeko
    sql_azkenharrapatu = "SELECT MAX(harrapatuId) as id FROM PokemonTalde WHERE ErabiltzaileIzena = ? AND PokemonPokedexID = ?"
    res_id = self.db.select(sql_azkenharrapatu, (erabiltzailea, pokemonId))
    harrapatu_id = res_id[0]['id'] if res_id and res_id[0]['id'] else None

    # Azken harrapatuId-a badago, abileziak eta mugimenduak gehitu
    if harrapatu_id:
        # Pokemon-ak izan ditzakeen abileziak lortu
        sql_abilezi = "SELECT izena FROM IzanDezake WHERE pokemonPokedexID = ?"
        posibleak = self.db.select(sql_abilezi, (pokemonId,))
        
        if posibleak:
            # Abilezi bat ausaz aukeratu
            aukeratua = random.choice(posibleak)
            if isinstance(aukeratua, dict): 
                aukeratua_izena = aukeratua['izena']
            else:
                aukeratua_izena = aukeratua[0]

            # Abilezia harrapatutako Pokemon-ari ezarri
            sql_dauka = "INSERT INTO Dauka (abileziIzena, harrapatuId) VALUES (?, ?)"
            self.db.insert(sql_dauka, (aukeratua_izena, harrapatu_id))

        # Pokemon-ak ikas ditzakeen mugimenduak lortu
        sql_mugi = "SELECT mugiIzena FROM IkasDezake WHERE pokedexId = ?"
        mugi_posibleak = self.db.select(sql_mugi, (pokemonId,))
        
        # Mugimendu izenak zerrenda batera pasatu
        mugi_zerrenda = []
        for m in mugi_posibleak:
              if isinstance(m, dict):
                  mugi_zerrenda.append(m['mugiIzena'])
              else:
                  mugi_zerrenda.append(m[0])

        # 4 mugimendu ausaz aukeratu (edo gutxiago badaude, denak)
        mugi_kop = min(len(mugi_zerrenda), 4)
        aukeratu_mugi = random.sample(mugi_zerrenda, mugi_kop)

        # Lortutako mugimenduak harrapatutako Pokemon-ari ezarri
        sql_mugimenduak = "INSERT INTO MugimenduIzanTalde (harrapatuId, mugimenduIzena) VALUES (?, ?)"
        for move in aukeratu_mugi:
            self.db.insert(sql_mugimenduak, (harrapatu_id, move))
    
    # Pokemon-a taldean sartu
    sql_taldera = "INSERT INTO PokemonTaldean (taldeIzena, harrapatuId, erabiltzaileIzena) VALUES (?, ?, ?)"
    self.db.insert(sql_taldera, (taldeIzena, harrapatu_id, erabiltzailea))

    # Pokemon-aren izena bueltatu, notifikazioan sartzeko
    sql_izena = "SELECT izena FROM PokemonTalde WHERE harrapatuId = ?"
    izena = self.db.select(sql_izena, (harrapatu_id,))
    return izena[0]['izena']

  def ezabatu_taldetik(self, taldeIzena, erabiltzailea, pokemonId):
      # Ezabatuko den Pokemon-aren izena lortu, notifikazioan sartzeko
      sql_ezabatuIzena = "SELECT izena FROM PokemonTalde WHERE harrapatuId = ?"
      izena = self.db.select(sql_ezabatuIzena, (pokemonId,))
      pokeIzena = izena[0]['izena']
      
      # Pokemon-aren datuak ezabatu hainbat taulatik
      # Mugimenduak ezabatu
      sql_mugiezabatu = "DELETE FROM MugimenduIzanTalde WHERE harrapatuId = ?"
      self.db.delete(sql_mugiezabatu, (pokemonId,))

      # Abilezia ezabatu
      sql_abilezabatu = "DELETE FROM Dauka WHERE harrapatuId = ?"
      self.db.delete(sql_abilezabatu, (pokemonId,))

      # Pokemon-a taldetik atera
      sql_taldekanpo = "DELETE FROM PokemonTaldean WHERE harrapatuId = ? AND taldeIzena = ? AND erabiltzaileIzena = ?"
      self.db.delete(sql_taldekanpo, (pokemonId, taldeIzena, erabiltzailea))

      # Pokemon-a ezabatu (askatu)
      sql_askatu = "DELETE FROM PokemonTalde WHERE harrapatuId = ?"
      self.db.delete(sql_askatu, (pokemonId,))

      return pokeIzena


  def ezabatu_taldea(self, taldeIzena, erabiltzailea):
      # Taldeko pokemon guztiak lortu
      sql_pokemonguztiak = "SELECT harrapatuId FROM PokemonTaldean WHERE taldeIzena = ? AND erabiltzaileIzena = ?"
      pokemon_ids = self.db.select(sql_pokemonguztiak, (taldeIzena, erabiltzailea))

      # Taldean dauden pokemon bakoitzarentzat, ezabatu taldetik
      for pokemon in pokemon_ids:
          pokemonId = pokemon['harrapatuId']
          self.ezabatu_taldetik(taldeIzena, erabiltzailea, pokemonId)

      # Taldea bera ezabatu
      sql_taldeaezabatu = "DELETE FROM Taldea WHERE taldeIzena = ? AND erabiltzaileIzena = ?"
      self.db.delete(sql_taldeaezabatu, (taldeIzena, erabiltzailea))

    
  def bistaratu_pokemon_taldea(self, pokeId):
    # Pokemon-aren informazioa lortu
    sql_pokeinfo = "SELECT P.harrapatuId, P.izena, P.HP, P.ATK, P.SPATK, P.DEF, P.SPDEF, P.SPE, PP.irudia, PP.pokeId, PP.pisua, PP.altuera FROM PokemonTalde P, PokemonPokedex PP WHERE P.harrapatuId = ? AND P.PokemonPokedexID = PP.pokeId"
    pokemon = self.db.select(sql_pokeinfo, (pokeId,))
      
    # Informazioa JSON formatuan prestatu
    for pokemons in pokemon:
      json_pokeinfo = {
          'harrapatuId': pokemons['harrapatuId'],
          'izena': pokemons['izena'],         
          'argazkia': pokemons['irudia'],
          'id': pokemons['pokeId'],
          'pisua': pokemons['altuera'],
          'altuera': pokemons['pisua']
      }

    # Pokemon-aren estatistikak prestatu
    stats = {
      'hp': pokemons['HP'],
      'atk': pokemons['ATK'],
      'spatk': pokemons['SPATK'],
      'def': pokemons['DEF'],
      'spdef': pokemons['SPDEF'],
      'spe': pokemons['SPE'],
    }

    # Abileziak eta mugimenduak lortu
    json_pokeinfo['stats'] = stats
    abilezia = self.db.select("SELECT abileziIzena FROM Dauka WHERE harrapatuId = ?", [json_pokeinfo['harrapatuId']])
    abIzena = [abi['abileziIzena'] for abi in abilezia]
    json_pokeinfo['abileziak'] = abIzena
    mugimenduak = self.db.select("SELECT mugimenduIzena FROM MugimenduIzanTalde WHERE harrapatuId = ?", [json_pokeinfo['harrapatuId']])
    mugiIzenak = [mugi['mugimenduIzena'] for mugi in mugimenduak]
    json_pokeinfo['mugimenduak'] = mugiIzenak
    return json_pokeinfo 

  # =====================================================
  # POKEDEX
  # =====================================================

  def pokedex_kargatu(self, JSON2):
    if not self.pokemonak_konprobatu():
        self.pokemonak_kargatu()
    if not self.motak_konprobatu():
        self.motak_kargatu()
    if not self.abileziak_konprobatu():
        self.abileziak_kargatu()
    if not self.mugimenduak_konprobatu():
        self.mugimenduak_kargatu()
    #if not self.eboluzioak_konprobatu():
        #self.eboluzioak_kargatu()

    sql3 = "SELECT P.izena, P.irudia, P.pokeId FROM PokemonPokedex P" # Hasierako kontsulta
    parametroak = []

    if JSON2['motak']: # Erabiltzaileak, mota(k) aukeratzen baditu
        sql3 += " JOIN DaMotaPokemon DM ON P.pokeId = DM.pokemonID JOIN MotaPokemon M ON DM.motaIzena = M.pokemonMotaIzena"

    if JSON2['izena']: # Erabiltzaileak, zerbait ipintzen badu bilatzailean
        sql3 += " WHERE P.izena LIKE ?"
        parametroak.append(f"%{JSON2['izena']}%")

    if JSON2['generazioak']: # Erabiltzaileak, generazioa(k) aukeratzen baditu
        signos = ','.join(['?'] * len(JSON2['generazioak']))
        operator = "AND" if "WHERE" in sql3 else "WHERE"
        sql3 += f" {operator} P.generazioa IN ({signos})"
        parametroak.extend(JSON2['generazioak'])

    if JSON2['motak']: # Erabiltzaileak, mota(k) aukeratzen baditu
        signos_motak = ','.join(['?'] * len(JSON2['motak']))
        operador = "AND" if "WHERE" in sql3 else "WHERE"
        sql3 += f" {operador} M.pokemonMotaIzena IN ({signos_motak})"
        parametroak.extend(JSON2['motak'])

    errenkadak = self.db.select(sql3, parametroak) # Kontsulta egin

    json1 = []
    # Pokemon bakoitzeko, JSON bat gehitu
    for pokemon in errenkadak:
        datuak = {
          'izena': pokemon['izena'],
          'argazkia': pokemon['irudia'],
          'id': pokemon['pokeId']
        }
        json1.append(datuak)

    return json1

  def pokemonak_kargatu(self):
    sql_pokeinfo = 'INSERT OR IGNORE INTO PokemonPokedex (pokeId, izena, altuera, pisua, generoa, deskripzioa, irudia, generazioa, preEboluzioId) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
    pokemon_izenak = self.api.pokemon_izenak_eskatu() # Pokemon-en izenak eskatu
    for pokemon in pokemon_izenak:
        try:
          parametroak = self.api.pokemon_eskatu(pokemon['name']) # Pokemon-aren JSON-a eskatu
          if parametroak:
            self.db.insert(sql_pokeinfo, [parametroak["pokeId"], parametroak["izena"], parametroak["altuera"], parametroak["pisua"], parametroak["generoa"], parametroak["deskripzioa"], parametroak["irudia"], parametroak["generazioa"], parametroak["pre_eboluzioa"]])
          else:
             print(f"Saltando {pokemon['name']}")
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
    sql1 = "INSERT OR IGNORE INTO MotaPokemon (pokemonMotaIzena, irudia) VALUES (?, ?)"
    sql_pokeinfo = "INSERT OR IGNORE INTO DaMotaPokemon (motaIzena, pokemonID) VALUES (?, ?)"
    mota_izenak = self.api.mota_izenak_eskatu() # Mota izenak eskatu
    for mota in mota_izenak:
        try:
          if mota['name'] in ['unknown', 'shadow']: # Balio ez duten motak
                continue
          self.db.insert(sql1, [mota['name'].capitalize(), f"/static/icons/{mota['name']}.svg" ]) # Mota-ren izena eta irudia txertatu datu basean
          tipo = self.api.mota_eskatu(mota['name'])
          for pokemon in tipo["pokemonak"]: # Mota hau duten pokemonak
              try:
                pokemon_id = int(pokemon["pokemon"]["url"].split('/')[-2])
                self.db.insert(sql_pokeinfo, [mota['name'].capitalize(), pokemon_id])
              except Exception as e:
                print(f"Error {e}")
        except Exception as e:
          print(f"Error {e}")

    # Mota bakoitzaren multiplikatzaileak
    sql3 = "INSERT OR IGNORE INTO Multiplikatzailea(pokemonMotaJaso, pokemonMotaEraso, multiplikatzailea) VALUES (?, ?, ?)"
    for mota in mota_izenak:
        tipo = self.api.mota_eskatu(mota['name'])
        # Mota bakoitzak ze nolako efektua duen beste motengan
        dobles = tipo["erlazioak"]["double_damage_to"]
        mitades = tipo["erlazioak"]["half_damage_to"]
        zeros = tipo["erlazioak"]["no_damage_to"]
        for doble in dobles:
          parametroak = [doble["name"].capitalize(), mota["name"].capitalize(), 2.0]
          self.db.insert(sql3, parametroak)
        for mitad in mitades:
          parametroak = [mitad["name"].capitalize(), mota['name'].capitalize(), 0.5]
          self.db.insert(sql3, parametroak)
        for zero in zeros:
          parametroak = [zero["name"].capitalize(), mota['name'].capitalize(), 0.0]
          self.db.insert(sql3, parametroak)

  def abileziak_kargatu(self):
    sql1 = "INSERT OR IGNORE INTO Abilezia (izena, deskripzioa) VALUES (?, ?)"
    sql_pokeinfo = "INSERT OR IGNORE INTO IzanDezake (pokemonPokedexID, izena, ezkutua) VALUES (?, ?, ?)"
    abilezi_izenak = self.api.abilezi_izenak_eskatu() # Abilezia izenak eskatu
    for abileziak in abilezi_izenak:
        try:
          abilezia = self.api.abilezia_eskatu(abileziak['name']) # Abileziaren JSON-a eskatu
          if abilezia is not None:
            self.db.insert(sql1, [abilezia["izena"], abilezia["deskripzioa"]])
            for pokemon in abilezia["pokemonak"]: # Abilezi hau izan dezaketen pokemonak
              try:
                poke_id = int(pokemon["pokemon"]["url"].split('/')[-2])
                self.db.insert(sql_pokeinfo, [poke_id, abilezia["izena"], pokemon["is_hidden"]])
              except Exception as e:
                print()
          else:
             print('Error en habilidad')            
        except Exception as e:
           print(f"Error procesando habilidad {addinfo['name']}: {e}")

  def mugimenduak_kargatu(self):
    sql1 = "INSERT OR IGNORE INTO Mugimendua (izena, potentzia, zehaztazuna, PP, efektua, pokemonMotaIzena) VALUES (?, ?, ?, ?, ?, ?)"
    sql_pokeinfo = "INSERT OR IGNORE INTO IkasDezake (pokedexId, mugiIzena) VALUES (?, ?)"
    mugimendu_izenak = self.api.mugimendu_izenak_eskatu() # Mugimendu izenak eskatu
    for izena in mugimendu_izenak:
        mugimendua = self.api.mugimendua_eskatu(izena['name']) # Mugimendu JSON-a eskatu
        self.db.insert(sql1, [mugimendua["izena"], mugimendua["potentzia"], mugimendua["zehaztazuna"], mugimendua["PP"], mugimendua["efektua"], mugimendua["pokemonMotaIzena"]])
        for pokemon in mugimendua["pokemonak"]: # Mugimendu hau ikasi dezaketenb JSON-ak
          pokemon_id = int(pokemon["url"].split('/')[-2])
          self.db.insert(sql_pokeinfo, [pokemon_id, mugimendua["izena"]])

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

  def eboluzioak_konprobatu(self):
    return len(self.db.select("SELECT * FROM Eboluzioa LIMIT 1")) > 0

  # =====================================================
  # ITEMDEX
  # =====================================================

  # Itemak DB-tik iragazkiekin lortu
  # Izena, mota eta ordena kontuan hartu
  def itemdex_kargatu(self, JSON2):
    if not self.itemak_konprobatu():
        self.itemak_kargatu()

    sql = """
          SELECT I.itemID as ID, I.izena, I.argazkia
          FROM Item I
          WHERE 1=1
    """
    params = []

    # Iragazketa izenaz
    if JSON2.get("izena"):
        sql += " AND I.izena LIKE ?"
        params.append(f"%{JSON2['izena']}%")

    # Iragazketa motaz
    if JSON2.get("motak") and len(JSON2["motak"]) > 0:
        signos = ",".join(["?"] * len(JSON2["motak"]))
        sql += f" AND I.MotaIzena IN ({signos})"
        params.extend(JSON2["motak"])

    # Alfabetikoki ordenatu
    orden = "DESC" if JSON2.get("alfabetikokiAlderantziz", False) else "ASC"
    sql += f" ORDER BY I.izena {orden}"

    return self.db.select(sql, params)

  # Item mota guztiak lortu
  # Alfabetikoki ordenatuta bueltatu
  def lortu_motak(self):
    sql = "SELECT ItemMotaIzena FROM MotaItem ORDER BY ItemMotaIzena ASC"
    return self.db.select(sql)

  # Item baten informazio osoa lortu
  # ID bidez bilatu eta bueltatu
  def bistaratu_item(self, id):
    sql = """
          SELECT itemID, izena, deskripzioa, argazkia, MotaIzena
          FROM Item
          WHERE itemID = ?
          LIMIT 1
    """
    resultado = self.db.select(sql, [id])
    return resultado[0] if resultado else None

  # DB-an itemak badauden egiaztatu
  # Gutxienez bat badago, True bueltatu
  def itemak_konprobatu(self):
    resultado = self.db.select("SELECT * FROM Item LIMIT 1")
    return len(resultado) > 0

  # PokeAPI-tik item guztiak kargatu
  # Motak eta itemak DB-an gorde
  # Errepikapenak saihestu
  def itemak_kargatu(self):
    sql_mota = "INSERT OR IGNORE INTO MotaItem (ItemMotaIzena) VALUES (?)"
    sql_item = "INSERT OR IGNORE INTO Item (itemID, izena, deskripzioa, argazkia, MotaIzena) VALUES (?, ?, ?, ?, ?)"

    for item in self.api.item_izenak_eskatu():
        try:
              # API datuak prozesatzeko
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

  # =====================================================
  # CHATBOT
  # =====================================================
  def getMugimenduIkasgarriak(self, pokeId):
      # Pokemon baten ikas daitezkeen mugimenduak lortzeko SQL kontsulta
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

      # Kontsulta exekutatu
      errenkadak = self.db.select(sql, [pokeId])

      # Ez badago emaitzarik
      if not errenkadak:
          return None

      # Mugimendu guztiak zerrenda batean gorde
      mugimenduak = []
      for unekoa in errenkadak:
          if unekoa["mugimendu_izena"]:
              mugimenduak.append({
                  "mugimenduIzena": unekoa["mugimendu_izena"],
                  "potentzia": unekoa["potentzia"],
                  "zehaztasuna": unekoa["zehaztazuna"]
              })

      # Pokemon informazioa eta mugimenduak gorde
      pokemon_info = {
          "izena": errenkadak[0]["pokemon_izena"],
          "irudia": errenkadak[0]["pokemon_irudia"],
          "mugimenduak": mugimenduak
      }
      return pokemon_info

  def getIndarrak(self, pokeId):
      # Pokemon baten motak, indarrak eta ahuleziak lortzeko SQL kontsulta
      sql = """
            SELECT p.izena, \
                   p.irudia, \
                   t.pokemonMotaIzena AS mota_izena, \
                   t.irudia           AS mota_irudia, \
                   m.pokemonMotaEraso, \
                   m.multiplikatzailea, \
                   t2.irudia          AS erasoko_mota_irudia
            FROM PokemonPokedex p
                     LEFT JOIN DaMotaPokemon d ON p.pokeId = d.pokemonID
                     LEFT JOIN MotaPokemon t ON d.MotaIzena = t.pokemonMotaIzena
                     LEFT JOIN Multiplikatzailea m ON t.pokemonMotaIzena = m.pokemonMotaJaso
                     LEFT JOIN MotaPokemon t2 ON m.pokemonMotaEraso = t2.pokemonMotaIzena
            WHERE p.pokeId = ? \
            """

      # Kontsulta exekutatu
      errenkadak = self.db.select(sql, [pokeId])

      # Ez badago emaitzarik
      if not errenkadak:
          return None

      # Set-ak erabili bikoizketak saihesteko
      mota_set = set()
      indarrak_set = set()
      ahuleziak_set = set()

      for row in errenkadak:
          # Pokemon motak gorde
          if row["mota_izena"]:
              mota_set.add((row["mota_izena"], row["mota_irudia"]))

          # Multiplikatzailearen arabera indarrak edo ahuleziak
          if row["pokemonMotaEraso"] and row["multiplikatzailea"]:
              efektu_key = (row["pokemonMotaEraso"], row["erasoko_mota_irudia"])
              if row["multiplikatzailea"] < 1:
                  indarrak_set.add(efektu_key)
              elif row["multiplikatzailea"] > 1:
                  ahuleziak_set.add(efektu_key)

      # Pokemonaren informazioa prestatu
      pokemon_info = {
          "izena": errenkadak[0]["izena"],
          "irudia": errenkadak[0]["irudia"],
          # mota_set bat hiztegi-zerrenda bihurtzen, bakoitza izena eta irudiarekin, eta gehitu pokemon_info barruan
          "pokemon_motak": [{"izena": izena, "irudia": irudia} for izena, irudia in mota_set],
          "indarrak": [{"izena": izena, "irudia": irudia} for izena, irudia in indarrak_set],
          "ahuleziak": [{"izena": izena, "irudia": irudia} for izena, irudia in ahuleziak_set]
      }

      return pokemon_info

  def getEboluzioa(self, poke_id):
      # Aurreko eta hurrengo eboluzioak lortu
      aurrekoak = self.bilatu_eboluzioak(poke_id, aurreko=True)
      hurrengoak = self.bilatu_eboluzioak(poke_id, aurreko=False)

      # Uneteko Pokemon-aren oinarrizko informazioa
      unekoa = self.db.select("SELECT izena, irudia FROM PokemonPokedex WHERE pokeId = ?", [poke_id])

      # Ez bada existitzen
      if not unekoa:
          return None

      # Eboluzioaren informazio osoa prestatu
      eboluzio_info = {
          "izena": unekoa[0]["izena"],
          "irudia": unekoa[0]["irudia"],
          "aurrekoak": aurrekoak,
          "hurrengoak": hurrengoak
      }

      return eboluzio_info

  def bilatu_eboluzioak(self, start_id, aurreko=True):
      # Aurkitutako eboluzioak gordetzeko zerrenda
      emaitza = []  # [{
                    #   "pokeId": int,
                    #   "izena": str,
                    #   "irudia": str
                    # }]
      # Jada bisitatutako Pokemon ID-ak, errepikapenak saihesteko
      bisitatuak = set()
      # BFS BFS egiteko hasierako zerrenda
      itzuli = [start_id]

      while itzuli:
          unekoa = itzuli.pop(0)

          # Jada bisitatuta bada, saltatu
          if unekoa in bisitatuak:
              continue

          # Bestela, bisitatu zerrendara gehitu
          bisitatuak.add(unekoa)

          # SQL kontsulta prestatu aurreko edo hurrengo eboluzioak lortzeko
          if aurreko:
              # Aurreko eboluzioa bilatu
              sql = """
                    SELECT P1.pokeId, P1.izena, P1.irudia
                    FROM PokemonPokedex P1
                      JOIN PokemonPokedex P2 ON P1.pokeId = P2.preEboluzioId
                    WHERE P2.pokeId = ? \
                    """
          else:
              # Hurrengo eboluzioa bilatu
              sql = """
                    SELECT P2.pokeId, P2.izena, P2.irudia
                    FROM PokemonPokedex P1
                      JOIN PokemonPokedex P2 ON P1.pokeId = P2.preEboluzioId
                    WHERE P1.pokeId = ? \
                    """

          # SQL exekutatu eta emaitzak prozesatu
          for unekoa_info in self.db.select(sql, [unekoa]):
              emaitza.append(unekoa_info)
              # Hurrengo bilaketarako gehitu ID berria
              if unekoa_info["pokeId"] not in bisitatuak:
                  itzuli.append(unekoa_info["pokeId"])

      return emaitza

  def getOnenak(self, talde_info):
    # Taldearen izena eta erabiltzailea lortu
    taldeIzena = talde_info.get("taldeIzena")
    erabiltzaileIzena = talde_info.get("erabiltzaileIzena")

    # Datuak falta badira
    if not taldeIzena or not erabiltzaileIzena:
        return None

    # SQL kontsulta taldeko pokemon guztiak lortzeko
    sql = """
          SELECT pt.PokemonPokedexID,
                 pt.izena,
                 pt.HP,
                 pt.ATK,
                 pt.DEF,
                 pt.SPATK,
                 pt.SPDEF,
                 pt.SPE,
                 pd.irudia
          FROM Taldea t
                  INNER JOIN PokemonTaldean pta
                        ON pta.taldeIzena = t.taldeIzena
                          AND pta.erabiltzaileIzena = t.erabiltzaileIzena
                  LEFT JOIN PokemonTalde pt
                        ON pt.harrapatuId = pta.harrapatuId
                          AND pt.erabiltzaileIzena = t.erabiltzaileIzena
                  LEFT JOIN PokemonPokedex pd
                        ON pt.PokemonPokedexID = pd.pokeId
          WHERE t.taldeIzena = ?
            AND t.erabiltzaileIzena = ?;
          """

    # Kontsulta exekutatu
    pokemon_zerrenda = self.db.select(sql, [taldeIzena, erabiltzaileIzena])

    # Ez badago Pokemonik
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
        # Orain arteko onena den egiaztatu
        if puntuazioa > puntuazio_maximoa:
          puntuazio_maximoa = puntuazioa
          onena = pokemon

    # Ez bada Pokemon onena aurkitu
    if not onena:
        return None

    # Pokemon onenaren informazioa prestatu
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
        "puntuazioa": puntuazio_maximoa,
        "taldeIzena": taldeIzena
    }

    return onena_info

  # =====================================================
  # NOTIFIKAZIOAK
  # =====================================================

  def notifikazioenInformazioaLortu(self, erabiltzaile_izena, bilatutako_izena):
    # SQL kontsulta prestatu
    query = "SELECT J.JarraituIzena, N.DataOrdua, N.deskripzioa FROM JarraitzenDu J JOIN Notifikatu N ON J.JarraituIzena = N.ErabiltzaileIzena WHERE J.JarraitzaileIzena = ? AND J.Notifikatu = 1 "

    # Bilaketa izena gehitu erabiltzailea zeozer idatzi baldin badu bestela zati hau salto egiten da
    if bilatutako_izena != None and bilatutako_izena != '':
        query += "AND J.JarraituIzena LIKE ? "
    
    # Ordenatu data eta orduaren arabera jaitsi egiten
    query += "ORDER BY N.DataOrdua DESC;"

    # Kontsulta exekutatu Query-an gehitu diren parametroekin (zeozer bilatu bada ala ez)
    if bilatutako_izena != None and bilatutako_izena != '':
        notifikazioZerrenda = self.db.select(query, (erabiltzaile_izena, f"%{bilatutako_izena}%"))
    else:
        notifikazioZerrenda = self.db.select(query, (erabiltzaile_izena,))

    # Notifikazioen JSON formatua prestatu eta metodotik itzuli
    notifikazioJSON = []
    for notifikazio in notifikazioZerrenda:
        notifikazioJSON.append({
          'JarraituIzena': notifikazio['JarraituIzena'], 
          'DataOrdua': notifikazio['DataOrdua'],
          'deskripzioa': notifikazio['deskripzioa']
        })

    return notifikazioJSON

  def notifikazioBerria(self, ErabiltzaileIzena, DataOrdua, deskripzioa):
      # Insert query prestatu eta exekutatu
      query = "INSERT OR IGNORE INTO Notifikatu (ErabiltzaileIzena, deskripzioa, DataOrdua) VALUES (?, ?, ?)"
      try:
          self.db.insert(query, (ErabiltzaileIzena, deskripzioa, DataOrdua))
      except Exception as e:
          print(f"Errorea notifikazioa sortzean: {e}")
      return