# pytest app/test/test_itemdex.py -s -v
import re


def test_itemdex_menua(logged_in_client):
    """
    3.6.1: ITEMDEX botoia sakatu -> ItemDex pantaila irekitzen da
    """
    resp = logged_in_client.get('/itemdex', follow_redirects=True)
    assert resp.status_code == 200
    assert '/itemdex' in resp.request.path

    html = resp.data.decode('utf-8', errors='ignore').lower()
    assert 'buscar' in html
    print("✔ ItemDex orria kargatzen da")


def test_itemdex_iragazkia_bistaratzen_da(logged_in_client):
    """
    3.6.2: Iragazketa botoia sakatzean aukerak agertzen dira
    """
    resp = logged_in_client.get('/itemdex', follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()

    assert 'iragaz' in html or 'filtro' in html
    print("✔ Iragazketa aukerak bistaratzen dira")


def test_itemdex_home_botoia(logged_in_client):
    """
    3.6.3 / 3.6.19.1: Home botoia -> menu nagusira
    """
    with logged_in_client.session_transaction() as session:
        role = session.get('role', 'usuario')
        menu = 'menu_admin' if role.lower() == 'admin' else 'menu'

    resp_home = logged_in_client.get(f'/{menu}', follow_redirects=True)
    assert resp_home.status_code == 200
    assert menu in resp_home.request.path
    print("✔ Home botoiak menu nagusira eramaten du")


def test_item_bilaketa_existitzen_da(logged_in_client):
    """
    3.6.4: Item existitzen da bilaketa eginda agertzen da
    """
    resp = logged_in_client.post('/itemdex', data={'izena': 'poción'}, follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()
    assert 'poción' in html, "Ez da 'poción' itemik aurkitu bilaketan"
    print("✔ Item existitzen da bilaketan eta agertzen da")


def test_item_bilaketa_ez_da_existitzen(logged_in_client):
    """
    3.6.5: Item ez da existitzen
    """
    resp = logged_in_client.post('/itemdex', data={'izena': 'aaaaaaaaaaaa'}, follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()
    assert 'no se encontraron items' in html
    print("✔ Item ez da existitzen mezua agertzen da")


def test_item_bilaketa_hutsik(logged_in_client):
    """
    3.6.6: Bilaketa hutsik -> item guztiak agertzen dira
    """
    resp = logged_in_client.post('/itemdex', data={'izena': ''}, follow_redirects=True)
    assert resp.status_code == 200
    assert '/itemdex' in resp.request.path
    print("✔ Bilaketa hutsik -> itemdex berriro kargatzen da")


def test_item_bilaketa_zenbakiekin_mt01(logged_in_client):
    """
    3.6.7: Zenbakidun bilaketa (MT01)
    """
    resp = logged_in_client.post('/itemdex', data={'izena': 'mt01'}, follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()
    assert 'mt01' in html

    match = re.search(r'/itemdex/item/(\d+)', html)
    assert match
    print("✔ MT01 bilaketa eta xehetasunak funtzionatzen dute")


def test_item_bilaketa_karaktere_bereziak(logged_in_client):
    """
    3.6.8: Karaktere bereziak
    """
    resp = logged_in_client.post('/itemdex', data={'izena': '@@@###'}, follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()
    assert 'no se encontraron items' in html
    print("✔ Karaktere bereziekin errore mezua")


def test_item_bilaketa_hitz_partziala(logged_in_client):
    """
    3.6.9: Hitz partziala bilaketa
    """
    resp = logged_in_client.post('/itemdex', data={'izena': 'poc'}, follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()
    assert 'no se encontraron' not in html
    print("✔ Bilaketa partziala ondo funtzionatzen du")


def test_item_bilaketa_maiuskulak(logged_in_client):
    """
    3.6.10: Maiuskula/minuskula sentikorra ez
    """
    resp1 = logged_in_client.post('/itemdex', data={'izena': 'REVIVIR'}, follow_redirects=True)
    resp2 = logged_in_client.post('/itemdex', data={'izena': 'revivir'}, follow_redirects=True)
    assert resp1.data == resp2.data
    print("✔ Maiuskula/minuskula berdin tratatzen dira")


def test_item_bilaketa_espazioekin(logged_in_client):
    """
    3.6.11: Espazioekin
    Ohikoa da oraindik ez da strip egiten, backend-ean aplikatu beharko da.
    """
    # Espazioekin bidali bilaketa
    bilaketa_espazioekin = '   poción   '
    resp = logged_in_client.post(
        '/itemdex',
        data={'izena': bilaketa_espazioekin},
        follow_redirects=True
    )
    html = resp.data.decode('utf-8', errors='ignore').lower()

    # Egiaztatu itema agertzen den strip gabe
    assert 'poción' in html, (
        "Ez da 'poción' itema aurkitu bilaketa espazioekin. "
        "Seguruenik strip() falta da backend-ean."
    )

    print("✔ Bilaketa espazioekin funtzionatzen du (strip beharrezkoa backend-ean)")


def test_item_bilaketa_luzeegia(logged_in_client):
    """
    3.6.12: Bilaketa luzeegia (>100 karaktere)
    """
    resp = logged_in_client.post('/itemdex', data={'izena': 'a' * 150}, follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()
    assert 'no se encontraron items' in html
    print("✔ Bilaketa luzeegia -> ezer ez")


def test_item_iragazkia_motaz(logged_in_client):
    """
    3.6.13: Motaren arabera iragazketa aplikatzen da
    """
    resp_all = logged_in_client.get('/itemdex')
    resp_filtered = logged_in_client.post(
        '/itemdex',
        data={'motak': ['Medicina']},
        follow_redirects=True
    )
    assert resp_all.data != resp_filtered.data
    print("✔ Motaren arabera iragazketa aplikatzen da")


def test_item_ordenaketa_alfabetikoki(logged_in_client):
    """
    3.6.15: Ordenaketa alfabetikoa (asc/desc)
    Test hau robusta da: egiaztatzen du lehenengo item-a desberdina dela
    asc edo desc aplikatzean.
    """
    resp_default = logged_in_client.get('/itemdex')
    html_default = resp_default.data.decode('utf-8', errors='ignore').lower()
    names_default = re.findall(r'<span>(.*?)</span>', html_default)

    resp_sorted = logged_in_client.post(
        '/itemdex',
        data={'orden': 'desc'},
        follow_redirects=True
    )
    html_sorted = resp_sorted.data.decode('utf-8', errors='ignore').lower()
    names_sorted = re.findall(r'<span>(.*?)</span>', html_sorted)

    # Comprobamos que el primer item cambio de posición
    assert names_default[0] != names_sorted[0], "Orden alfabetikoa ez da aldatu (desc)"
    print("✔ Ordenaketa alfabetikoa aplikatzen da (desc)")


def test_item_bilaketa_bikoitza(logged_in_client):
    """
    3.6.18: Bilaketa bat eta gero beste bat
    """
    logged_in_client.post('/itemdex', data={'izena': 'poción'}, follow_redirects=True)
    resp = logged_in_client.post('/itemdex', data={'izena': 'revivir'}, follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()

    assert 'revivir' in html, "'revivir' itema ez da agertzen bigarren bilaketan"
    assert 'poción' not in html, "'poción' oraindik agertzen da, lehenengo bilaketa ez da ordezkatua"
    print("✔ Bigarren bilaketak lehenengoa ordezkatzen du")
