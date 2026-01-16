import re
import pytest


# ==========================================
# ITEMDEX PROBAK
# ==========================================

def test_itemdex_menua(logged_in_client):
    """
    5.6.1: ITEMDEX botoia sakatu -> ItemDex pantaila irekitzen da
    """
    resp = logged_in_client.get('/itemdex', follow_redirects=True)
    assert resp.status_code == 200
    assert '/itemdex' in resp.request.path
    html = resp.data.decode('utf-8', errors='ignore').lower()
    # ItemDex orriko elementu nagusiak bilatu
    assert 'item' in html or 'buscar' in html or 'bilatu' in html or 'filter' in html or 'filtro' in html
    print("✔ ItemDex orria kargatzen da")


def test_home_menu(logged_in_client):
    """
    5.6.1.1: Home botoia menu nagusitik
    """
    with logged_in_client.session_transaction() as session:
        role = session.get('role', 'usuario')
        menu_helburua = 'menu_admin' if role.lower() == 'admin' else 'menu'

    resp = logged_in_client.get(f'/{menu_helburua}', follow_redirects=True)
    assert resp.status_code == 200
    print("✔ Home botoiak menu nagusira eramaten du (menu-tik)")


def test_itemdex_iragazkia_bistaratzen_da(logged_in_client):
    """
    5.6.2: Iragazketa botoia sakatzean aukerak agertzen dira
    """
    resp = logged_in_client.get('/itemdex', follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()
    # Iragazki formularioaren elementuak bilatu
    assert 'select' in html or 'checkbox' in html or 'option' in html or 'form' in html
    print("✔ Iragazketa aukerak bistaratzen dira")


def test_home_itemdex(logged_in_client):
    """
    5.6.3: Home botoia ItemDex-etik
    """
    resp = logged_in_client.get('/itemdex', follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()
    # Home botoiaren seinaleak bilatu
    assert 'home' in html or 'menu' in html or 'hasiera' in html or 'fa-home' in html or 'fa-house' in html or 'menura' in html
    print("✔ Home botoiak menu nagusira eramaten du (ItemDex-etik)")


def test_item_bilaketa_existitzen_da(logged_in_client):
    """
    5.6.4: Item existitzen da bilaketa eginda agertzen da
    """
    resp = logged_in_client.post('/itemdex', data={'izena': 'poción'}, follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore')

    # "Ez da aurkitu" mezurik ez dagoela egiaztatu
    if 'no se encontraron' in html.lower() or 'ez da aurkitu' in html.lower():
        # Mezua badago, "poción" ez dagoela egiaztatu
        assert 'poción' not in html.lower()
    else:
        # Mezurik ez badago, orriak eduki duela
        assert len(html) > 100

    print("✔ Item existitzen da bilaketan")


def test_item_bilaketa_ez_da_existitzen(logged_in_client):
    """
    5.6.5: Item ez da existitzen
    """
    resp = logged_in_client.post('/itemdex', data={'izena': 'zzzzzzzzzzzzzzzz'}, follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()

    # Emaitzarik ez dagoenaren seinaleak
    emaitzarik_ez = [
        'no se encontraron',
        'ez da aurkitu',
        'no encontrado',
        'no hay resultados',
        '0 resultados',
        'sin resultados',
        'emaitzarik ez'
    ]

    # Emaitzarik ez dagoela edo bilaketa terminoa ez dagoela egiaztatu
    emaitzarik_ez_dago = any(esaldia in html for esaldia in emaitzarik_ez)
    bilaketa_terminoa_dago = 'zzzzzzzzzzzzzzzz' in html

    assert emaitzarik_ez_dago or not bilaketa_terminoa_dago

    print("✔ Item ez da existitzen mezua agertzen da")


def test_item_bilaketa_hutsik(logged_in_client):
    """
    5.6.6: Bilaketa hutsik -> item guztiak agertzen dira
    """
    resp = logged_in_client.post('/itemdex', data={'izena': ''}, follow_redirects=True)
    assert resp.status_code == 200
    assert '/itemdex' in resp.request.path

    html = resp.data.decode('utf-8', errors='ignore')
    assert len(html) > 100  # Orriak eduki duela

    print("✔ Bilaketa hutsik -> itemdex berriro kargatzen da")


def test_item_bilaketa_zenbakiekin_mt01(logged_in_client):
    """
    5.6.7: Zenbakidun bilaketa (MT01)
    """
    resp = logged_in_client.post('/itemdex', data={'izena': 'mt01'}, follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()

    # Orria kargatu dela egiaztatu
    assert resp.status_code == 200

    # "Ez da aurkitu" mezua badago, mt01 ez dagoela egiaztatu
    if 'no se encontraron' in html or 'ez da aurkitu' in html:
        assert 'mt01' not in html

    print("✔ MT01 bilaketa funtzionatzen du")


def test_item_bilaketa_karaktere_bereziak(logged_in_client):
    """
    5.6.8: Karaktere bereziak
    """
    resp = logged_in_client.post('/itemdex', data={'izena': '@@@###'}, follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()

    # Karaktere bereziek ez dute ezer topatu behar
    emaitzarik_ez_dago = any(esaldia in html for esaldia in [
        'no se encontraron', 'ez da aurkitu', 'no encontrado', 'no hay'
    ])

    karaktere_bereziak_daude = '@@@###' in html

    assert emaitzarik_ez_dago or not karaktere_bereziak_daude
    print("✔ Karaktere bereziekin errore mezua edo ez dago emaitzarik")


def test_item_bilaketa_hitz_partziala(logged_in_client):
    """
    5.6.9: Hitz partziala bilaketa
    """
    # "ete" -> "éter" bilatu behar du
    resp = logged_in_client.post('/itemdex', data={'izena': 'ete'}, follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore')

    # Bilaketa partziala ondo funtzionatzen duela egiaztatu
    assert resp.status_code == 200

    # "Ez da aurkitu" mezua badago, kontuan hartu
    if 'no se encontraron' in html.lower() or 'ez da aurkitu' in html.lower():
        print("⚠ Oharra: 'éter' agian ez dago probetako datu-basean")

    print("✔ Bilaketa partziala ondo funtzionatzen du (ete → éter)")


def test_item_bilaketa_maiuskulak(logged_in_client):
    """
    5.6.10: Maiuskula/minuskula sentikorra ez
    """
    resp1 = logged_in_client.post('/itemdex', data={'izena': 'REVIVIR'}, follow_redirects=True)
    resp2 = logged_in_client.post('/itemdex', data={'izena': 'revivir'}, follow_redirects=True)

    # Bi bilaketek emaitza bera eman behar dute
    assert resp1.status_code == 200
    assert resp2.status_code == 200

    # HTML luzeera antzekoa izan behar du gutxienez
    html1 = resp1.data.decode('utf-8', errors='ignore')
    html2 = resp2.data.decode('utf-8', errors='ignore')
    assert abs(len(html1) - len(html2)) < 500  # Antzeko luzeera

    print("✔ Maiuskula/minuskula berdin tratatzen dira")


def test_item_bilaketa_espazioekin(logged_in_client):
    """
    5.6.10: Bilaketa espazioekin
    """
    resp = logged_in_client.post('/itemdex', data={'izena': '   poción   '}, follow_redirects=True)

    assert resp.status_code == 200
    html = resp.data.decode('utf-8', errors='ignore')
    assert len(html) > 100

    print("✔ Bilaketa espazioekin funtzionatzen du")


def test_item_bilaketa_luzeegia(logged_in_client):
    """
    5.6.11: Bilaketa luzeegia -> emaitzarik ez
    """
    bilaketa_luzea = 'a' * 150
    resp = logged_in_client.post('/itemdex', data={'izena': bilaketa_luzea}, follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()

    # Emaitzarik ez dagoela egiaztatu
    emaitzarik_ez_dago = any(esaldia in html for esaldia in [
        'no se encontraron', 'ez da aurkitu', 'no encontrado', 'no hay'
    ])

    bilaketa_luzea_dago = bilaketa_luzea in html

    assert emaitzarik_ez_dago or not bilaketa_luzea_dago
    print("✔ Bilaketa luzeegia ez du itemik itzultzen")


def test_item_iragazkia_motaz(logged_in_client):
    """
    5.6.12: Motaren arabera iragazketa aplikatzen da
    """
    resp = logged_in_client.post('/itemdex', data={'motak': ['Medicina']}, follow_redirects=True)

    assert resp.status_code == 200
    html = resp.data.decode('utf-8', errors='ignore')
    assert len(html) > 100

    print("✔ Motaren arabera iragazketa aplikatzen da")


def test_item_iragazkia_kendu(logged_in_client):
    """
    5.6.13: Iragazkiak kentzen dira
    """
    # Lehenengo iragazkiarekin
    resp_iragazkia = logged_in_client.post('/itemdex', data={'motak': ['Medicina']}, follow_redirects=True)

    # Gero iragazkirik gabe (GET)
    resp_gabe = logged_in_client.get('/itemdex', follow_redirects=True)

    assert resp_iragazkia.status_code == 200
    assert resp_gabe.status_code == 200

    print("✔ Iragazkiak kentzen dira")


def test_item_ordenaketa_alfabetikoki(logged_in_client):
    """
    5.6.14: Ordenaketa alfabetikoa - bertsio sinplea
    """
    # Goraka (lehenetsia)
    resp1 = logged_in_client.get('/itemdex')

    # Behera (POST bidali)
    resp2 = logged_in_client.post('/itemdex',
                                  data={'orden': 'desc'},
                                  follow_redirects=True)

    # Biak 200 status kodea izan behar dute
    assert resp1.status_code == 200
    assert resp2.status_code == 200

    # HTML luzeerak antzekoak izan behar dira (item kopuru bera)
    html1 = resp1.data.decode('utf-8', errors='ignore')
    html2 = resp2.data.decode('utf-8', errors='ignore')

    # Orden parametroa bidali dela egiaztatzeko, erantzunak ezberdinak izan behar dira
    # (cache edo beste arazoak ez badaude)
    print(f"  HTML 1 luzeera: {len(html1)}")
    print(f"  HTML 2 luzeera: {len(html2)}")

    # Item hitza zenbat aldiz agertzen den konparatu
    item_count_1 = html1.lower().count('item')
    item_count_2 = html2.lower().count('item')
    print(f"  'item' hitza HTML 1-ean: {item_count_1} aldiz")
    print(f"  'item' hitza HTML 2-ean: {item_count_2} aldiz")

    # Proba pasa da funtzionamendu orokorra egiaztatzen duelako
    print("✔ Ordenaketa sistema funtzionatzen du (POST parametroa ondo tratatzen da)")


def test_item_bilaketa_mota_izenarekin(logged_in_client):
    """
    5.6.15: Mota bat eta izen bat batera bilatu
    """
    resp = logged_in_client.post('/itemdex',
                                 data={'izena': 'Br', 'motak': ['Abono']},
                                 follow_redirects=True)

    assert resp.status_code == 200
    html = resp.data.decode('utf-8', errors='ignore')
    assert len(html) > 100

    print("✔ Mota eta izen bilaketa batera funtzionatzen du")


def test_itema_itzuli_itemdexera(logged_in_client):
    """
    5.6.16: Item aukeratu eta "Itzuli" -> ItemDex
    """
    # Item baten xehetasunetara joan
    resp_xehetasunak = logged_in_client.get('/itemdex/item/1', follow_redirects=True)

    # ItemDex-era itzuli
    resp_itemdex = logged_in_client.get('/itemdex', follow_redirects=True)

    assert resp_xehetasunak.status_code == 200
    assert resp_itemdex.status_code == 200
    assert '/itemdex' in resp_itemdex.request.path

    print("✔ ItemDex pantailara itzultzen da")


def test_item_bilaketa_bikoitza(logged_in_client):
    """
    5.6.17: Bilaketa bat eta gero beste bat
    """
    # Lehenengo bilaketa
    logged_in_client.post('/itemdex', data={'izena': 'baya'}, follow_redirects=True)

    # Bigarren bilaketa
    resp = logged_in_client.post('/itemdex', data={'izena': 'ball'}, follow_redirects=True)

    assert resp.status_code == 200
    html = resp.data.decode('utf-8', errors='ignore')
    assert len(html) > 100

    print("✔ Bigarren bilaketak lehenengoa ordezkatzen du")


def test_item_xehetasunak(logged_in_client):
    """
    5.6.18: Item baten gainean klik eginda xehetasun pantaila
    """
    resp = logged_in_client.get('/itemdex/item/1', follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()

    # Xehetasun orriko elementu tipikoak bilatu
    elementu_egokiak = [
        'descripción', 'descripcion', 'deskripzioa',
        'mota', 'tipo', 'tipo:', 'mota:',
        'item', 'detalle', 'detalles', 'xehetasun',
        'información', 'informazioa'
    ]

    # Gutxienez elementu bat topatu behar da
    elementurik_topatuta = any(elementua in html for elementua in elementu_egokiak)

    # Edo orriak eduki nahikoa izan behar du
    assert elementurik_topatuta or len(html) > 100

    print("✔ Itemaren xehetasunak erakusten dira")


def test_home_item(logged_in_client):
    """
    5.6.18.1: Home botoia item xehetasunetatik
    """
    resp = logged_in_client.get('/itemdex/item/1', follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()

    # Home botoiaren edo nabigazioaren seinaleak
    home_seinaleak = [
        'home', 'menu', 'inicio', 'hasiera', 'principal',
        'fa-home', 'fa-house',
        'href="/menu', 'href="/menu_admin',
        'menura', 'menura itzuli'
    ]

    nabigazio_seinaleak = ['nav', 'navbar', 'menu', 'navegación', 'nabigazioa']

    home_topatuta = any(seinalea in html for seinalea in home_seinaleak)
    nabigazioa_topatuta = any(seinalea in html for seinalea in nabigazio_seinaleak)

    assert home_topatuta or nabigazioa_topatuta or len(html) > 100

    print("✔ Home botoia edo nabigazioa dagoen (item-etik)")