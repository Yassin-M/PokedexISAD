import pytest

# =================================================================
# POKEDEX PROBA PLANA 
# =================================================================

# 3.4.1: Erabiltzaileak Pokemon baten argazkian sakatzen du.
def test_3_4_1_xehetasunak_kargatu(client):
    """Egiaztatu abileziak eta deskripzioa kargatzen direla (adib. Bulbasaur)"""
    resp = client.get('/pokedex/pokemon/1')
    assert resp.status_code == 200
    html = resp.data.decode('utf-8')
    assert "ABILEZIAK:" in html
    assert "POKEDEX SARRERA:" in html
    assert "ESTATISTIKA POSIBLEAK:" in html

# 3.4.2: Bilatzailean izen osoa eta existitzen dena (Charmander).
def test_3_4_2_izen_osoa_existitzen_da(client):
    resp = client.post('/pokedex/bilatu', data={'izena': 'Charmander'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Charmander" in resp.data
    assert b"Bulbasaur" not in resp.data

# 3.4.3: Bilatzailean existitzen ez den izena.
def test_3_4_3_izena_ez_da_existitzen(client):
    resp = client.post('/pokedex/bilatu', data={'izena': 'Digimon'}, follow_redirects=True)
    assert b"Ez da pokemonik aurkitu." in resp.data
    assert b"Digimon" in resp.data
    # Bilatzailean "Digimon" egongo da, baina ez da emaitzarik egon behar
    assert b"class=\"pokemon-card\"" not in resp.data

# 3.4.4: Bilatzailea hutsik utzi (Enter sakatu).
def test_3_4_4_bilatzailea_hutsik(client):
    resp = client.post('/pokedex/bilatu', data={'izena': ''}, follow_redirects=True)
    # Zerrenda osoa erakutsi behar du 
    assert resp.data.count(b"class=\"pokemon-card\"") > 1

# 3.4.5: Bilatzailea hutsuneekin (espazioak).
def test_3_4_5_bilatzailea_hutsuneak(client):
    """Planak dio: Errore mezua eta lista osoa erakutsiko da."""
    resp = client.post('/pokedex/bilatu', data={'izena': '   '}, follow_redirects=True)
    # Ez badu aurkitzen, no-results mezua agertuko da.
    assert b"Ez da pokemonik aurkitu." in resp.data

# 3.4.6: Hitz partziala sartu (Char).
def test_3_4_6_hitz_partziala(client):
    resp = client.post('/pokedex/bilatu', data={'izena': 'Char'}, follow_redirects=True)
    assert b"Charmander" in resp.data
    assert b"Charmeleon" in resp.data
    assert b"Chimchar" in resp.data
    assert b"Squirtle" not in resp.data

# 3.4.7: Letra larriz edo xehez idatzi (CHARMANDER).
def test_3_4_7_letra_larri_xehe_berdin(client):
    resp = client.post('/pokedex/bilatu', data={'izena': 'CHARMANDER'}, follow_redirects=True)
    assert b"Charmander" in resp.data

# 3.4.8: Iragazki botoian sakatu.
def test_3_4_8_iragazki_botoia_existentzia(client):
    resp = client.get('/pokedex')
    # Ziurtatu HTML-an filter-toggle id-a duen botoia dagoela
    assert b"id=\"filter-toggle\"" in resp.data

# 3.4.9: Motaren arabera iragazi (Adibidez: Fire).
def test_3_4_9_mota_iragazkia(client):
    resp = client.post('/pokedex/bilatu', data={'motak': ['Fire']}, follow_redirects=True)
    assert b"Charmander" in resp.data
    assert b"Infernape" in resp.data
    assert b"Squirtle" not in resp.data

# 3.4.10: Generazioaren arabera iragazi (Adibidez: 1).
def test_3_4_10_generazio_iragazkia(client):
    resp = client.post('/pokedex/bilatu', data={'generazioak': ['1']}, follow_redirects=True)
    assert b"Bulbasaur" in resp.data
    assert b"Chikorita" not in resp.data

# 3.4.11: Generazioa ETA Mota aldi berean.
def test_3_4_11_generazioa_eta_mota(client):
    data = {'motak': ['Water'], 'generazioak': ['1']}
    resp = client.post('/pokedex/bilatu', data=data, follow_redirects=True)
    assert b"Squirtle" in resp.data
    assert b"Cyndaquil" not in resp.data

# 3.4.12: Iragazkia eta Pokemon izena (Existitzen bada).
def test_3_4_12_iragazkia_eta_izena_existitzen_da(client):
    data = {'motak': ['Fire'], 'izena': 'Charmander'}
    resp = client.post('/pokedex/bilatu', data=data, follow_redirects=True)
    assert b"Charmander" in resp.data

# 3.4.13: Iragazkia eta Pokemon izena (Existitzen ez bada edo iragazkia betetzen ez badu).
def test_3_4_13_iragazkia_eta_izena_ez_betetzea(client):
    # Charmander ez da Water motakoa
    data = {'motak': ['Water'], 'izena': 'Charmander'}
    resp = client.post('/pokedex/bilatu', data=data, follow_redirects=True)
    assert b"Ez da pokemonik aurkitu." in resp.data

# 3.4.14: Iragazkia eta hitz partziala.
def test_3_4_14_iragazkia_eta_hitz_partziala(client):
    data = {'motak': ['Grass'], 'izena': 'Bulba'}
    resp = client.post('/pokedex/bilatu', data=data, follow_redirects=True)
    assert b"Bulbasaur" in resp.data

# 3.4.15: Motaren arabera (beste kasu bat).
def test_3_4_15_motaren_arabera_berretsi(client):
    resp = client.post('/pokedex/bilatu', data={'motak': ['Electric']}, follow_redirects=True)
    assert b"Pikachu" in resp.data

# 3.4.16: Edozein momentutan "Home" botoian sakatu.
def test_3_4_16_home_botoia_nabigazioa(logged_in_client):
    """Logged_in_client erabiltzen dugu menu_endpoint-a egiaztatzeko (Admin edo Usuario)"""
    # Xehetasun orritik probatu
    resp = logged_in_client.get('/pokedex/pokemon/1')
    assert b"fa-solid fa-house" in resp.data
    # Egiaztatu href-ak menu nagusira daramala 
    assert b'href="/menu' in resp.data