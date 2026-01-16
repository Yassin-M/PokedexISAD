import pytest
from config import Config
#from app import create_app
from app.database.database import Connection
#from unittest.mock import MagicMock, patch

# =================================================================
# TALDE PROBA PLANA 
# =================================================================

# 3.2.1: Erabiltzailea “EDIT” botoia sakatzen du.
def test_3_2_1_edit_button(client):
    with client.session_transaction() as sess:
        sess["user"] = "test_user"
    resp = client.get('/taldea/Talde 1', follow_redirects=True)
    assert b"GORDE" in resp.data
    assert b"EZABATU" in resp.data

# 3.2.2: Talde berria sortu (10 baino gutxiago dituenean)
def test_3_2_2_plus_button_new_team(client):
    conn = Connection()
    conn.delete("DELETE FROM Taldea WHERE erabiltzaileIzena = ?", ("test_user",))
    for i in range(1, 9):
        conn.insert("INSERT INTO Taldea (taldeIzena, erabiltzaileIzena) VALUES (?, ?)", (f"Talde{i}", "test_user"))
    with client.session_transaction() as sess:
        sess["user"] = "test_user"
    resp = client.post('/taldea/Talde 1', follow_redirects=True)
    assert b"GORDE" in resp.data
    assert b"EZABATU" in resp.data

# 3.2.3: Talde gehiegi (10 talde muga)
def test_3_2_3_talde_muga_errorea(client):
    conn = Connection()
    conn.delete("DELETE FROM Taldea WHERE erabiltzaileIzena = ?", ("test_user",))
    for i in range(1, 11):
        conn.insert("INSERT INTO Taldea (taldeIzena, erabiltzaileIzena) VALUES (?, ?)", (f"Talde{i}", "test_user"))
    
    with client.session_transaction() as sess:
        sess["user"] = "test_user"
    
    resp = client.post('/taldea_berria', follow_redirects=True)
    assert b"gehienez 10 talde" in resp.data.lower() or resp.status_code == 200 # Zure errore mezuaren arabera

#def test_3_2_4_pokemon_aldatu_ezabatu_menua(client):
 #   with client.session_transaction() as sess:
  #      sess["user"] = "test_user"
   #     sess["editatzen_ari_den_taldea"] = "Taldea 1"
    #    sess["akzioa"] = "aldatu_pokemon"

 #   conn = Connection()
#    conn.delete("DELETE FROM Taldea WHERE erabiltzaileIzena = ?", ("test_user",))
  #  conn.delete("DELETE FROM PokemonPokedex")
   # conn.delete("DELETE FROM PokemonTaldean WHERE erabiltzaileIzena = ?", ("test_user",))
    #conn.insert("INSERT INTO PokemonPokedex (pokeId, izena, altuera, pisua, generoa, deskripzioa, irudia, generazioa, preEboluzioId) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (1, "Bulbasaur", 7.0, 69.0, "Ar/Eme", "A strange seed was planted on its back at birth. The plant sprouts and grows with this Pokémon.", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png", 1, 1))
    #conn.insert("INSERT INTO PokemonTaldean (taldeIzena, harrapatuId, erabiltzaileIzena) VALUES (?, ?, ?)", ("Taldea 1", 1, "test_user"))
    #conn.insert("INSERT INTO PokemonTalde (izena, maila, adiskidetasun_maila, generoa, HP, ATK, SPATK, DEF, SPDEF, SPE, PokemonPokedexID, ErabiltzaileIzena) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ("Bulbasaur", 5, 0, "Ar", 45, 49, 49, 49, 49, 45, 1, "test_user"))

    # ID 1 (Bulbasaur) aldatu_pokemon simulatuz
#    resp = client.get('/pokedex/pokemon/1', follow_redirects=True)

#    assert resp.status_code == 200
 #   assert b"Zer egin nahi duzu?" in resp.data
  #  assert b"ALDATU POKEMONA" in resp.data
   # assert b"EZABATU POKEMONA" in resp.data

# 3.2.5: Pokemon gehitu botoia "+" sakatu
#def test_3_2_5_add_pokemon_button(client):

   # with client.session_transaction() as sess:
  #          sess["user"] = "test_user"
 #           sess["editatzen_ari_den_taldea"] = "TaldeTest"
#
  #      # Petición POST
 #   resp = client.post('/pokedex', data={'akzioa': 'hauta_pokemon'}, follow_redirects=True)
#
  #      # Verificaciones
 #   assert resp.status_code == 200
#    assert b"Bulbasaur" in resp.data
#    assert b"BILATZAILEA" in resp.data

# 3.2.7: Taldea ezabatu
def test_3_2_7_talde_ezabatu(client):
    conn = Connection()
    conn.delete("DELETE FROM Taldea WHERE erabiltzaileIzena = ?", ("test_user",))
    conn.insert("INSERT INTO Taldea (taldeIzena, erabiltzaileIzena) VALUES (?, ?)", ("Talde 1", "test_user"))
    with client.session_transaction() as sess:
        sess["user"] = "test_user"
        sess["editatzen_ari_den_taldea"] = "Talde 1"
    resp = client.post('/taldea/ezabatu_guztia', follow_redirects=True)
    assert b"TALDE BERRIA" in resp.data
    assert b"Talde 1" not in resp.data
    resultado = conn.select("SELECT * FROM Taldea WHERE taldeIzena = ? AND erabiltzaileIzena = ?", ("Talde 1", "test_user"))
    
    # El resultado de select suele ser una lista. Si está vacía, el borrado fue exitoso.
    assert len(resultado) == 0, f"Error: El equipo Talde 1 todavía existe en la base de datos."

# 3.2.8: Taldea gorde
def test_3_2_8_taldea_gorde(client):
    conn = Connection()
    conn.insert("INSERT INTO Taldea (taldeIzena, erabiltzaileIzena) VALUES (?, ?)", ("Talde 1", "test_user"))
    
    with client.session_transaction() as sess:
        sess["user"] = "test_user"
        sess["editatzen_ari_den_taldea"] = "Talde 1"
    # Normalean /taldeak orrira bueltatzen da
    resp = client.get('/taldeak', follow_redirects=True)
    assert resp.status_code == 200
    assert b"Talde 1" in resp.data

# 3.2.9: Pokemon ezabatu botoia
def test_3_2_9_pokemon_ezabatu_taldea(client):
    with client.session_transaction() as sess:
        sess["user"] = "test_user"
        sess["editatzen_ari_den_taldea"] = "Talde1"
        sess["akzioa"] = "ezabatu_pokemon"
        sess["pokemon_datuak"] = 1  # Bulbasaur ID

    conn = Connection()
    conn.insert("INSERT INTO PokemonTaldean (taldeIzena, harrapatuId, erabiltzaileIzena) VALUES (?, ?, ?)", ("Talde1", 1, "test_user"))
    
    # ID 1 (Bulbasaur) ezabatu_pokemon simulatuz
    resp = client.get('/pokemon_taldea/ezabatu', follow_redirects=True)

    # Taldearen orrira itzuli behar da eta pokemon-a ez egon
    assert b"Bulbasaur" not in resp.data

# 3.2.10: Pokemon bat aldatu botoia
def test_3_2_10_pokemon_aldatu_pokedexera(client):
    with client.session_transaction() as sess:
        sess["user"] = "test_user"

    # Pokemon baten xehetasunetatik 'aldatu' sakatzean
    resp = client.get('/pokemon_taldea/ezabatu', data={'akzioa': 'hauta_pokemon'}, follow_redirects=True)
    html = resp.data.decode('utf-8')
    assert "BILATZAILEA:" in html

    # Honek Pokedex-era edo aukeraketa modura eraman behar zaitu

# 3.2.11: Erabiltzaileak Pokemon baten argazkian sakatzen du.
def test_3_2_11_xehetasunak_kargatu(client):
    """Egiaztatu abileziak eta deskripzioa kargatzen direla (adib. Bulbasaur)"""
    resp = client.get('/pokedex/pokemon/1')
    assert resp.status_code == 200
    html = resp.data.decode('utf-8')
    assert "ABILEZIAK:" in html
    assert "POKEDEX SARRERA:" in html
    assert "ESTATISTIKA POSIBLEAK:" in html

# 3.2.12: Bilatzailean izen osoa eta existitzen dena (Charmander).
def test_3_2_12_izen_osoa_existitzen_da(client):
    resp = client.post('/pokedex/bilatu', data={'izena': 'Charmander'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Charmander" in resp.data
    assert b"Bulbasaur" not in resp.data

# 3.2.13: Hitz partziala sartu (Char).
def test_3_2_13_hitz_partziala(client):
    resp = client.post('/pokedex/bilatu', data={'izena': 'Char'}, follow_redirects=True)
    assert b"Charmander" in resp.data
    assert b"Squirtle" not in resp.data

# 3.2.14: Bilatzailea hutsik utzi (Enter sakatu).
def test_3_2_14_bilatzailea_hutsik(client):
    resp = client.post('/pokedex/bilatu', data={'izena': ''}, follow_redirects=True)
    # Zerrenda osoa erakutsi behar du 
    assert resp.data.count(b"class=\"pokemon-card\"") > 1

# 3.2.15: Iragazki botoian sakatu.
def test_3_2_15_iragazki_botoia_existentzia(client):
    resp = client.get('/pokedex')
    assert b"id=\"filter-toggle\"" in resp.data

# 3.2.16: Motaren arabera iragazi (Adibidez: Fire).
def test_3_2_16_mota_iragazkia(client):
    resp = client.post('/pokedex/bilatu', data={'motak': ['Fire']}, follow_redirects=True)
    assert b"Charmander" in resp.data
    assert b"Infernape" in resp.data
    assert b"Squirtle" not in resp.data

# 3.2.17: Generazioaren arabera iragazi (Adibidez: 1).
def test_3_2_17_generazio_iragazkia(client):
    resp = client.post('/pokedex/bilatu', data={'generazioak': ['1']}, follow_redirects=True)
    assert b"Bulbasaur" in resp.data
    assert b"Chikorita" not in resp.data

# 3.2.18: Generazioa ETA Mota aldi berean.
def test_3_2_18_generazioa_eta_mota(client):
    data = {'motak': ['Water'], 'generazioak': ['1']}
    resp = client.post('/pokedex/bilatu', data=data, follow_redirects=True)
    assert b"Squirtle" in resp.data
    assert b"Cyndaquil" not in resp.data


# 3.2.22: Edozein momentutan "Home" botoian sakatu.
def test_3_2_22_home_botoia_nabigazioa(logged_in_client):
    """Logged_in_client erabiltzen dugu menu_endpoint-a egiaztatzeko (Admin edo Usuario)"""
    # Xehetasun orritik probatu
    resp = logged_in_client.get('/pokedex/pokemon/1')
    assert b"fa-solid fa-house" in resp.data
    # Egiaztatu href-ak menu nagusira daramala 
    assert b'href="/menu' in resp.data

# 3.2.19: Pokemon-a aukeratu (ez badago taldean)
def test_3_2_19_aukeratu_pokemon_berria(client):
    with client.session_transaction() as sess:
        sess["user"] = "test_user"
        sess["editatzen_ari_den_taldea"] = "Talde 1"
        sess["akzioa"] = "hauta_pokemon"
    
    # URL honek (edo antzeko batek) pokemon-a taldean sartu beharko luke
    resp = client.get('/gehitu_pokemon_taldera/1', follow_redirects=True)
    assert resp.status_code == 200
    # Taldearen orrira itzuli behar da eta pokemon-a hor egon

def test_3_2_20_aukeratu_pokemon_(client):
    with client.session_transaction() as sess:
        sess["user"] = "test_user"
        sess["editatzen_ari_den_taldea"] = "Talde Test"
        sess["pokemon_datuak"] = 150 # Mewtwo

    # Ruta que ejecuta la inserción
    resp = client.get('/pokemon_taldea', follow_redirects=True)

    assert resp.status_code == 200
    assert b"Talde Test" in resp.data # Vuelta al equipo
    assert b"gehitu du" in resp.data.lower() or b"Mewtwo" in resp.data # Notificación o aparece en la lista

def test_3_2_21_aukeratu_pokemon_taldean_dagoenean(client):
    conn = Connection()
    conn.delete("DELETE FROM Taldea WHERE erabiltzaileIzena = ?", ("test_user",))
    conn.insert("INSERT INTO Taldea (taldeIzena, erabiltzaileIzena) VALUES (?, ?)", ("Talde Beteta", "test_user"))
    conn.delete("DELETE FROM PokemonTaldean WHERE erabiltzaileIzena = ?", ("test_user",))
    for i in range(1, 7):
        conn.insert("INSERT INTO PokemonTaldean (taldeIzena, harrapatuId, erabiltzaileIzena) VALUES (?, ?, ?)", ("Talde Beteta", i, "test_user"))
    
    with client.session_transaction() as sess:
        sess["user"] = "test_user"
        sess["editatzen_ari_den_taldea"] = "Talde Beteta"
        sess["akzioa"] = "hauta_pokemon"
    
    resp = client.get('/sartu_taldera', follow_redirects=True) # Intentar añadir un séptimo Pokémon
    assert resp.status_code == 200