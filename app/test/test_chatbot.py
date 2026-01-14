# pytest app/test/test_chatbot.py -s -v
def test_chatbotMenua(logged_in_client):
    """
    3.5.1: Chatbot botoia sakatu eta pantaila irekitzen da
    """
    chat_resp = logged_in_client.get('/chatbot', follow_redirects=True)

    # Egiaztapenak
    assert chat_resp.status_code == 200
    assert '/chatbot' in chat_resp.request.path

def test_botoiakSakatu(logged_in_client):
    """
    Pokedex moduak
    3.5.2: mugimenduak
    3.5.3: onenak
    3.5.4: eboluzioa
    3.5.5: indarrak
    """
    moduak = [
        ('mugimenduak', '/pokedex?mode=mugimenduak'),
        ('eboluzioa', '/pokedex?mode=eboluzioa'),
        ('indarrak', '/pokedex?mode=indarrak'),
        ('onenak', '/chatbot/taldeZerrenda')  # URL desberdina!
    ]

    for modua, url in moduak:
        # Botoia sakatzen da
        resp = logged_in_client.get(url, follow_redirects=True)

        # Egiaztapen orokorrak
        assert resp.status_code == 200

        # URLaren egiaztapenak
        if modua == 'onenak':
            # Onenak: /chatbot/taldeZerrenda orrian egon behar
            assert '/chatbot/taldeZerrenda' in resp.request.path, \
                f"{modua}: /chatbot/taldeZerrenda bidean izan behar"
        else:
            # Beste moduak: /pokedex orrian egon behar
            assert resp.request.path == '/pokedex'
            assert resp.request.args.get('mode') == modua

def test_homeBotoia(logged_in_client):
    """
    Home botoia -> benetako menu orrira
    """
    test_orriak = [
        '/chatbot',
        '/chatbot/mugimenduak/25',
        '/chatbot/eboluzioa/25',
        '/chatbot/indarrak/25',
        '/chatbot/taldeZerrenda',
        '/pokedex?mode=mugimenduak',
        '/pokedex?mode=eboluzioa',
        '/pokedex?mode=indarrak',
    ]

    with logged_in_client.session_transaction() as session:
        user_role = session.get('role', 'usuario')
        target_menu = 'menu_admin' if user_role.lower() == 'admin' else 'menu'

    for orria in test_orriak:
        # Orrira joan
        resp_unekoa=logged_in_client.get(orria,follow_redirects=True)
        assert resp_unekoa.status_code == 200

        # Home botoia sakatu
        resp_home = logged_in_client.get(f'/{target_menu}',follow_redirects=True)

        # 1. HTTP erantzuna
        assert resp_home.status_code == 200

        # 2. URL bidea
        assert target_menu in resp_home.request.path

        # 3. Orriaren edukia egiaztatu
        edukia = resp_home.data.decode('utf-8', errors='ignore').lower()

        # Menu orriak izan behar duen eduki batzuk
        menu_elementuak = ['notif', 'chatbot', 'pokedex', 'lagunak', 'hasiera']

        # Printzipioz, denak agertu behar dira
        aurkitutakoak = [elem for elem in menu_elementuak if elem in edukia]
        assert len(aurkitutakoak) == 5

def test_mugimenduak(logged_in_client):
    """
    3.5.2.17: Pokemon ikonoa sakatu -> izena, mugimenduak, argazkia
    """
    import re

    resp = logged_in_client.get('/chatbot/mugimenduak/25')

    # Egiaztapenak
    assert resp.status_code == 200
    htmlEdukia = resp.data.decode('utf-8', errors='ignore').lower()

    # 1. Oinarrizkoak
    assert 'pikachu' in htmlEdukia
    assert 'mugimenduak:' in htmlEdukia

    # 2. Mugimendu izenak (25)
    pikachu_mugimenduak = [
        'agilidad', 'ataque rápido', 'atizar', 'contraataque',
        'derribo', 'doble filo', 'doble patada', 'día de pago',
        'excavar', 'fuerza', 'golpe cabeza', 'golpe cuerpo',
        'gruñido', 'impactrueno', 'látigo', 'megapatada',
        'megapuño', 'onda trueno', 'puño trueno', 'rayo',
        'sumisión', 'surf', 'sísmico', 'trueno', 'tóxico'
    ]

    aurkitutakoak = [m for m in pikachu_mugimenduak if m in htmlEdukia]
    assert len(aurkitutakoak) == 25

    # 3. Mugimendu lerroak
    pattern = r'<strong>([^<]+)</strong>\s*-\s*Potentzia:\s*([^,]+)\s*,\s*Zehaztasuna:\s*([^<]+)'
    mugimenduak = re.findall(pattern, resp.data.decode('utf-8'), re.IGNORECASE)

    assert len(mugimenduak) == 25

    # 4. Balio zehatzak
    probatzeko_mugimenduak = [
        ('ataque rápido', '40', '100'),
        ('rayo', '90', '100'),
        ('impactrueno', '40', '100'),
        ('puño trueno', '75', '100'),
    ]

    egiaztatuak = 0
    for izena_espero, potentzia_espero, zehaztasuna_espero in probatzeko_mugimenduak:
        for izena, potentzia, zehaztasuna in mugimenduak:
            if izena_espero.lower() in izena.lower():
                if (potentzia_espero.lower() in potentzia.lower() and
                        zehaztasuna_espero.lower() in zehaztasuna.lower()):
                    egiaztatuak += 1
                    break

    assert egiaztatuak == 4

    # 5. Argazkia
    assert '<img' in htmlEdukia and 'src="' in htmlEdukia


def test_indarrak_general(logged_in_client):
    """3.5.5: Pokemon guztien indarrak eta ahuleziak"""
    test_cases = [
        (25, 'pikachu', ['electric'], ['electric', 'flying', 'steel'], ['ground']),
        (1, 'bulbasaur', ['grass', 'poison'], ['fighting','bug', 'water','poison','electric','fairy','grass','ground'],
         ['bug','ice','poison','psychic','fire','flying','ground' ])
    ]

    for pokemon_id, izena, motak, indarrak, ahuleziak in test_cases:
        html = logged_in_client.get(f'/chatbot/indarrak/{pokemon_id}').data.decode('utf-8', errors='ignore').lower()

        # Oinarrizkoak
        assert izena in html
        assert all(x in html for x in ['indarrak:', 'ahuleziak:', 'motak:'])

        # Atalak isolatu
        ind_start = html.find('indarrak:')
        ahu_start = html.find('ahuleziak:')

        ind_section = html[ind_start:ahu_start] if ind_start != -1 and ahu_start != -1 else html
        ahu_section = html[ahu_start:] if ahu_start != -1 else html

        # Motak
        mota_section = html[html.find('motak:'):html.find('motak:') + 1000] if 'motak:' in html else html
        for mota in motak:
            assert mota in mota_section

        # Indarrak
        ind_found = [i for i in indarrak if i in ind_section]
        assert len(ind_found) == len(indarrak)

        # Ahuleziak
        ahu_found = [a for a in ahuleziak if a in ahu_section]
        assert len(ahu_found) == len(ahuleziak)

        # Argazkia
        assert '<img' in html and 'src="' in html


def test_eboluzioa_general(logged_in_client):
    """
    3.5.4: Eboluzio kateak - kasu desberdinak
    """
    test_cases = [
        (44, 'gloom', ['oddish'], ['vileplume', 'bellossom']),
        (781, 'dhelmise', [], []),
        (25, 'pikachu', ['pichu'], ['raichu']),
        (1, 'bulbasaur', [], ['ivysaur', 'venusaur']),
    ]

    for pokemon_id, izena, aurreko_izenak, hurrengo_izenak in test_cases:
        resp = logged_in_client.get(f'/chatbot/eboluzioa/{pokemon_id}')
        assert resp.status_code == 200

        html = resp.data.decode('utf-8', errors='ignore').lower()

        # Oinarrizkoak
        assert all(x in html for x in [izena, 'aurreko forma:', 'hurrengo forma:'])

        # Atalak isolatu
        a_atala = html[html.find('aurreko forma:'):html.find('hurrengo forma:')]
        h_atala = html[html.find('hurrengo forma:'):]

        # Izenak egiaztatu
        if aurreko_izenak:
            a_aurkitutakoak = [a for a in aurreko_izenak if a in a_atala]
            assert len(a_aurkitutakoak) == len(aurreko_izenak)
        else:
            assert 'ez dago' in a_atala
        if hurrengo_izenak:
            h_aurkitutakoak = [h for h in hurrengo_izenak if h in h_atala]
            assert len(h_aurkitutakoak) == len(hurrengo_izenak)
        else:
            assert 'ez dago' in h_atala

        assert '<img' in html and 'src="' in html


def test_3_5_3_onenak_mocked(logged_in_client, mocker):
    """
    3.5.3: Mock datuekin probatu (taldea sortu gabe)
    """
    # 1. Mock talde zerrenda
    mock_taldeak = [
        {'izena': 'TEST_TALDEA_1'},
        {'izena': 'TEST_TALDEA_2'}
    ]

    # Zure controller-a mock egin
    from app.controller.model.eredu_kontroladorea import EreduKontroladorea

    # Mock egin taldeak_kargatu metodoa
    mocker.patch.object(EreduKontroladorea, 'taldeak_kargatu',
                        return_value=mock_taldeak)

    # 2. Talde zerrenda ikusi
    resp1 = logged_in_client.get('/chatbot/taldeZerrenda')
    assert resp1.status_code == 200

    html1 = resp1.data.decode('utf-8')
    assert 'TEST_TALDEA_1' in html1
    assert 'TEST_TALDEA_2' in html1

    # 3. Mock onena informazioa
    mock_onena = {
        "PokemonPokedexID": 25,
        "izena": "Pikachu",
        "irudia": "https://example.com/pikachu.png",
        "HP": 35,
        "ATK": 55,
        "DEF": 40,
        "SPATK": 50,
        "SPDEF": 50,
        "SPE": 90,
        "puntuazioa": 320,  # HP+ATK+DEF+SPATK+SPDEF+SPE
        "taldeIzena": "TEST_TALDEA_1"
    }

    # Mock egin onena lortzeko metodoa
    mocker.patch.object(EreduKontroladorea, 'getOnenak',
                        return_value=mock_onena)

    # 4. Onena ikusi
    resp2 = logged_in_client.get('/chatbot/onenak/TEST_TALDEA_1')
    assert resp2.status_code == 200

    html2 = resp2.data.decode('utf-8')

    # Egiaztatu datuak
    assert 'Pikachu' in html2
    assert 'TEST_TALDEA_1' in html2.upper()
    assert '35' in html2  # HP
    assert '320' in html2 or 'PUNTUAZIO TOTALA' in html2

