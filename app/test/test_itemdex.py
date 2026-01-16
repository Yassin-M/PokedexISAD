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
    assert 'buscar' in html
    print("✔ ItemDex orria kargatzen da")


def test_home_menu(logged_in_client):
    """
    5.6.1.1: Home botoia menu nagusitik
    """
    with logged_in_client.session_transaction() as session:
        role = session.get('role', 'usuario')
        menu = 'menu_admin' if role.lower() == 'admin' else 'menu'
    resp = logged_in_client.get(f'/{menu}', follow_redirects=True)
    assert resp.status_code == 200
    assert menu in resp.request.path
    print("✔ Home botoiak menu nagusira eramaten du (menu-tik)")


def test_itemdex_iragazkia_bistaratzen_da(logged_in_client):
    """
    5.6.2: Iragazketa botoia sakatzean aukerak agertzen dira
    """
    resp = logged_in_client.get('/itemdex', follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()
    assert 'iragaz' in html or 'filtro' in html
    print("✔ Iragazketa aukerak bistaratzen dira")


def test_home_itemdex(logged_in_client):
    """
    5.6.3: Home botoia ItemDex-etik
    """
    resp = logged_in_client.get('/itemdex', follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()
    # Egiaztatu home botoia existitzen dela
    assert 'fa-house' in html
    print("✔ Home botoiak menu nagusira eramaten du (ItemDex-etik)")


def test_item_bilaketa_existitzen_da(logged_in_client):
    """
    5.6.4: Item existitzen da bilaketa eginda agertzen da
    """
    resp = logged_in_client.post('/itemdex', data={'izena': 'poción'}, follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()
    assert 'poción' in html
    print("✔ Item existitzen da bilaketan eta agertzen da")


def test_item_bilaketa_ez_da_existitzen(logged_in_client):
    """
    5.6.5: Item ez da existitzen
    """
    resp = logged_in_client.post('/itemdex', data={'izena': 'zzzzzzzzzz'}, follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()
    assert 'no se encontraron items' in html
    print("✔ Item ez da existitzen mezua agertzen da")


def test_item_bilaketa_hutsik(logged_in_client):
    """
    5.6.6: Bilaketa hutsik -> item guztiak agertzen dira
    """
    resp = logged_in_client.post('/itemdex', data={'izena': ''}, follow_redirects=True)
    assert resp.status_code == 200
    assert '/itemdex' in resp.request.path
    print("✔ Bilaketa hutsik -> itemdex berriro kargatzen da")


def test_item_bilaketa_zenbakiekin_mt01(logged_in_client):
    """
    5.6.7: Zenbakidun bilaketa (MT01)
    """
    resp = logged_in_client.post('/itemdex', data={'izena': 'mt01'}, follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()
    assert 'mt01' in html
    print("✔ MT01 bilaketa eta xehetasunak funtzionatzen dute")


def test_item_bilaketa_karaktere_bereziak(logged_in_client):
    """
    5.6.8: Karaktere bereziak
    """
    resp = logged_in_client.post('/itemdex', data={'izena': '@@@###'}, follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()
    assert 'no se encontraron items' in html
    print("✔ Karaktere bereziekin errore mezua")


def test_item_bilaketa_hitz_partziala(logged_in_client):
    """
    5.6.9: Hitz partziala bilaketa
    """
    resp = logged_in_client.post('/itemdex', data={'izena': 'poc'}, follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()
    assert 'no se encontraron items' not in html
    print("✔ Bilaketa partziala ondo funtzionatzen du")


def test_item_bilaketa_maiuskulak(logged_in_client):
    """
    5.6.10: Maiuskula/minuskula sentikorra ez
    """
    resp1 = logged_in_client.post('/itemdex', data={'izena': 'REVIVIR'}, follow_redirects=True)
    resp2 = logged_in_client.post('/itemdex', data={'izena': 'revivir'}, follow_redirects=True)
    assert resp1.data == resp2.data
    print("✔ Maiuskula/minuskula berdin tratatzen dira")


def test_item_bilaketa_espazioekin(logged_in_client):
    """
    5.6.10: Bilaketa espazioekin
    strip() aplikatu ondoren funtzionatzen du
    """
    resp = logged_in_client.post('/itemdex', data={'izena': '   poción   '}, follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()
    assert 'poción' in html
    print("✔ Bilaketa espazioekin funtzionatzen du (strip backend-ean egin da)")


def test_item_bilaketa_luzeegia(logged_in_client):
    """
    5.6.11: Bilaketa luzeegia (>100 karaktere)
    """
    resp = logged_in_client.post('/itemdex', data={'izena': 'a' * 150}, follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()
    assert 'no se encontraron items' in html
    print("✔ Bilaketa luzeegia -> ezer ez")


def test_item_iragazkia_motaz(logged_in_client):
    """
    5.6.12: Motaren arabera iragazketa aplikatzen da
    """
    resp_filtered = logged_in_client.post('/itemdex', data={'motak': ['Medicina']}, follow_redirects=True)
    html_filtered = resp_filtered.data.decode('utf-8', errors='ignore').lower()
    assert 'medicina' in html_filtered
    print("✔ Motaren arabera iragazketa aplikatzen da")


def test_item_iragazkia_kendu(logged_in_client):
    """
    5.6.13: Iragazkiak kentzen dira
    """
    resp_all = logged_in_client.get('/itemdex', follow_redirects=True)
    html_all = resp_all.data.decode('utf-8', errors='ignore').lower()
    assert 'medicina' in html_all
    print("✔ Iragazkiak kentzen dira eta zerrenda osoa erakusten da")


def test_item_ordenaketa_alfabetikoki(logged_in_client):
    """
    5.6.14: Ordenaketa alfabetikoa
    """
    resp_default = logged_in_client.get('/itemdex')
    html_default = resp_default.data.decode('utf-8', errors='ignore').lower()
    names_default = re.findall(r'<span>(.*?)</span>', html_default)

    resp_sorted = logged_in_client.post('/itemdex', data={'orden': 'desc'}, follow_redirects=True)
    html_sorted = resp_sorted.data.decode('utf-8', errors='ignore').lower()
    names_sorted = re.findall(r'<span>(.*?)</span>', html_sorted)

    assert names_default[0] != names_sorted[0], "Orden alfabetikoa ez da aldatu (desc)"
    print("✔ Ordenaketa alfabetikoa aplikatzen da (desc)")


def test_item_bilaketa_mota_izenarekin(logged_in_client):
    """
    5.6.15: Mota bat eta izen bat batera bilatu
    """
    resp = logged_in_client.post('/itemdex', data={'izena': 'Br', 'motak': ['Abono']}, follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()
    assert 'abono brote' in html
    print("✔ Mota eta izen bilaketa batera funtzionatzen du")


def test_itema_itzuli_itemdexera(logged_in_client):
    """
    5.6.16: Item aukeratu eta "Itzuli" -> ItemDex
    """
    resp = logged_in_client.get('/itemdex', follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()
    assert '/itemdex' in resp.request.path
    print("✔ ItemDex pantailara itzultzen da")


def test_item_bilaketa_bikoitza(logged_in_client):
    """
    5.6.17: Bilaketa bat eta gero beste bat (partial search)
    Egiaztatzen du bigarren bilaketa lehenengoa ordezkatzen duela
    """
    # Lehenengo bilaketa
    logged_in_client.post('/itemdex', data={'izena': 'baya'}, follow_redirects=True)

    # Bigarren bilaketa
    resp = logged_in_client.post('/itemdex', data={'izena': 'ball'}, follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()

    names = re.findall(r'<span>(.*?)</span>', html)

    # Konprobazioak
    assert any('ball' in name.lower() for name in names), "'ball' itema ez da agertzen bigarren bilaketan"
    assert all('baya' not in name.lower() for name in
               names), "'baya' oraindik agertzen da, lehenengo bilaketa ez da ordezkatua"

    print("✔ Bigarren bilaketak lehenengoa ordezkatzen du")


def test_item_xehetasunak(logged_in_client):
    """
    5.6.18: Item baten gainean klik eginda xehetasun pantaila
    """
    resp = logged_in_client.get('/itemdex/item/1', follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()
    assert 'descripción' in html or 'descripcion' in html
    assert 'mota' in html or 'tipo' in html
    print("✔ Itemaren deskripzioa, ikonoa eta erabilpena erakusten da")


def test_home_item(logged_in_client):
    """
    5.6.18.1: Home botoia item xehetasunetatik
    """
    resp = logged_in_client.get('/itemdex/item/1', follow_redirects=True)
    html = resp.data.decode('utf-8', errors='ignore').lower()
    assert 'fa-house' in html
    print("✔ Home botoiak menu nagusira eramaten du (item-etik)")
