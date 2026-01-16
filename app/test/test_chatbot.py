# pytest app/test/test_chatbot.py -s -v
def test_chatbotMenua(logged_in_client):
    """
    3.5.1: Chatbot botoia sakatu eta pantaila irekitzen da
    """
    # Chatbot orrira sartu
    chat_resp = logged_in_client.get('/chatbot', follow_redirects=True)

    # HTTP erantzuna
    assert chat_resp.status_code == 200
    print("✔ Chatbot orria kargatzen da")

    # URL egiaztatu
    assert '/chatbot' in chat_resp.request.path
    print("✔ URL zuzena: /chatbot")


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
        ('onenak', '/chatbot/taldeZerrenda')  # URL desberdinak
    ]

    for modua, url in moduak:
        # Orrira sartu
        resp = logged_in_client.get(url, follow_redirects=True)

        # Egiaztapen orokorrak
        assert resp.status_code == 200
        print(f"✔ {modua}: orria kargatzen da")

        # URLaren egiaztapenak
        if modua == 'onenak':
            # Onenak: /chatbot/taldeZerrenda orrian egon behar
            assert '/chatbot/taldeZerrenda' in resp.request.path
            print("✔ Onenak: taldeZerrenda orria")

        else:
            # Beste moduak: /pokedex orrian egon behar
            assert resp.request.path == '/pokedex'
            print(f"✓ {modua}: /pokedex orrian")

            assert resp.request.args.get('mode') == modua
            print(f"✓ mode={modua} parametroa zuzena")

def test_homeBotoia(logged_in_client):
    """
    Home botoia -> menu nagusira bueltatu
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

    # Erabiltzailearen menua (admin edo arrunta)
    with logged_in_client.session_transaction() as session:
        user_role = session.get('role', 'usuario')
        target_menu = 'menu_admin' if user_role.lower() == 'admin' else 'menu'

    for orria in test_orriak:
        # Orrira sartu
        resp_unekoa=logged_in_client.get(orria,follow_redirects=True)
        assert resp_unekoa.status_code == 200
        print(f"✔ Orria kargatua: {orria}")

        # Home botoia sakatu
        resp_home = logged_in_client.get(f'/{target_menu}',follow_redirects=True)

        # 1. HTTP erantzuna
        assert resp_home.status_code == 200
        print("✓ Home botoia: menu orria kargatu da")

        # 2. URL bidea
        assert target_menu in resp_home.request.path
        print("✔ Menu zuzenera doa")

        # 3. Orriaren edukia egiaztatu
        edukia = resp_home.data.decode('utf-8', errors='ignore').lower()

        # Menu orriak izan behar duen eduki batzuk
        menu_elementuak = ['notif', 'chatbot', 'pokedex', 'lagunak', 'hasiera']

        # Printzipioz, denak agertu behar dira
        aurkitutakoak = [elem for elem in menu_elementuak if elem in edukia]
        assert len(aurkitutakoak) == 5
        print("✔ Menu uneko elementu guztiak agertzen dira")

def test_mugimenduak(logged_in_client):
    """
    3.5.2.17: Pokemon ikonoa sakatu -> izena, mugimenduak, argazkia
    """
    import re

    resp = logged_in_client.get('/chatbot/mugimenduak/25')

    # Egiaztapenak
    assert resp.status_code == 200
    print("✔ Mugimenduak orria kargatua")

    htmlEdukia = resp.data.decode('utf-8', errors='ignore').lower()

    # 1. Oinarrizkoak
    assert 'pikachu' in htmlEdukia
    print("✔ Pokemon izena agertzen da")

    assert 'mugimenduak:' in htmlEdukia
    print("✔ Mugimendu atala agertzen da")

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
    assert len(aurkitutakoak) >= 20
    print("✓ Mugimendu izen nagusiak aurkitu dira")

    # 3. Mugimendu lerroak
    pattern = r'<strong>([^<]+)</strong>\s*-\s*Potentzia:\s*([^,]+)\s*,\s*Zehaztasuna:\s*([^<]+)'
    mugimenduak = re.findall(pattern, resp.data.decode('utf-8'), re.IGNORECASE)

    assert len(mugimenduak) >= 20
    print("✓ Mugimendu kopuru nahikoa")

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

    assert egiaztatuak >= 3
    print("✓ Gutxienez 3 mugimenduaren balioak zuzenak dira")

    # 5. Argazkia
    assert '<img' in htmlEdukia and 'src="' in htmlEdukia
    print("✓ Pokemonaren irudia agertzen da")

def test_indarrak_general(logged_in_client):
    """3.5.5: Pokemon guztien indarrak eta ahuleziak"""
    test_cases = [
        (25, 'pikachu', ['electric'], ['electric', 'flying', 'steel'], ['ground']),
        (1, 'bulbasaur', ['grass', 'poison'], ['fighting','bug', 'water','poison','electric','fairy','grass','ground'],
         ['bug','ice','poison','psychic','fire','flying','ground' ])
    ]

    for pokemon_id, izena, motak, indarrak, ahuleziak in test_cases:
        html = logged_in_client.get(f'/chatbot/indarrak/{pokemon_id}').data.decode('utf-8', errors='ignore').lower()

        # Pokemon izena eta atal nagusiak
        assert izena in html
        print(f"✓ {izena}: izena agertzen da")

        assert all(x in html for x in ['indarrak:', 'ahuleziak:', 'motak:'])
        print(f"✓ {izena}: atal nagusiak agertzen dira")

        # Indarrak eta ahuleziak isolatu
        ind_start = html.find('indarrak:')
        ahu_start = html.find('ahuleziak:')

        ind_section = html[ind_start:ahu_start] if ind_start != -1 and ahu_start != -1 else html
        ahu_section = html[ahu_start:] if ahu_start != -1 else html

        # Motak egiaztatu
        mota_section = html[html.find('motak:'):html.find('motak:') + 1000] if 'motak:' in html else html
        for mota in motak:
            assert mota in mota_section

        # Indarrak egiaztatu
        ind_found = [i for i in indarrak if i in ind_section]
        assert len(ind_found) == len(indarrak)
        print(f"✓ {izena}: indarrak zuzena -> {ind_found}")

        # Ahuleziak egiaztatu
        ahu_found = [a for a in ahuleziak if a in ahu_section]
        assert len(ahu_found) == len(ahuleziak)
        print(f"✓ {izena}: ahuleziak zuzena -> {ahu_found}")

        # Argazkia
        assert '<img' in html and 'src="' in html
        print(f"✓ {izena}: irudia agertzen da")

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
        # Orrira joan
        resp = logged_in_client.get(f'/chatbot/eboluzioa/{pokemon_id}')
        assert resp.status_code == 200
        print(f"✓ {izena}: orria kargatu da (200)")

        html = resp.data.decode('utf-8', errors='ignore').lower()

        # Oinarrizko testak: Pokemon izena eta atalak
        assert all(x in html for x in [izena, 'aurreko forma:', 'hurrengo forma:'])
        print(f"✓ {izena}: izena eta aurreko/hurrengo forma atalak agertzen dira")

        # Atalak isolatu
        a_atala = html[html.find('aurreko forma:'):html.find('hurrengo forma:')]
        h_atala = html[html.find('hurrengo forma:'):]

        # Aurreko forma izenak egiaztatu
        if aurreko_izenak:
            a_aurkitutakoak = [a for a in aurreko_izenak if a in a_atala]
            assert len(a_aurkitutakoak) == len(aurreko_izenak)
            print(f"✓ {izena}: aurreko forma izenak zuzena -> {a_aurkitutakoak}")

        else:
            assert 'ez dago' in a_atala
            print(f"✓ {izena}: aurreko forma ez dagoela egiaztatu")

        # Hurrengo forma izenak egiaztatu
        if hurrengo_izenak:
            h_aurkitutakoak = [h for h in hurrengo_izenak if h in h_atala]
            assert len(h_aurkitutakoak) == len(hurrengo_izenak)
            print(f"✓ {izena}: hurrengo forma izenak zuzena -> {h_aurkitutakoak}")
        else:
            assert 'ez dago' in h_atala
            print(f"✓ {izena}: hurrengo forma ez dagoela egiaztatu")

        # Pokemon irudia egiaztatu
        assert '<img' in html and 'src="' in html
        print(f"✓ {izena}: irudia agertzen da")

def test_get_onenak(logged_in_client, onenak_test_data):
    """
    Erabiltzailearen fluxua probatzeko:
    1. Taldeen zerrenda ireki
    2. Talde bat aukeratu
    3. Aukeratutako taldeko Pokemon onenak (Onenak) ikusi
    """
    taldeIzena = "MY_TEST_TEAM"

    # Talde zerrenda orria
    resp_list = logged_in_client.get('/chatbot/taldeZerrenda')
    assert resp_list.status_code == 200
    print(f"✓ Talde zerrenda orria kargatu da (200)")

    html_list = resp_list.data.decode('utf-8', errors='ignore').lower()
    # Talde izena agertzen dela egiaztatu
    assert taldeIzena.lower() in html_list
    print(f"✓ Talde izena aurkitu da zerrendan -> {taldeIzena}")

    # Taldearen onenak orrira esteka zuzena
    assert f'/chatbot/onenak/{taldeIzena.lower()}' in html_list
    print(f"✓ Onenak esteka zuzena aurkitu da -> /chatbot/onenak/{taldeIzena.lower()}")

    # Taldearen Onenak orria
    resp_detail = logged_in_client.get(f'/chatbot/onenak/{taldeIzena}')
    assert resp_detail.status_code == 200
    print(f"✓ Onenak orria kargatu da (200) -> {taldeIzena}")

    html_detail = resp_detail.data.decode('utf-8', errors='ignore').lower()
    # Talde izena erakusten dela egiaztatu
    assert taldeIzena.lower() in html_detail
    print(f"✓ Talde izena agertzen da Onenak orrian -> {taldeIzena}")

    # Pokemon estatistikak erakusten direla egiaztatu
    for stat in ['hp', 'atk', 'def', 'spatk', 'spdef', 'spe']:
        assert stat in html_detail
        print(f"✓ Estatistika aurkitu da -> {stat}")

    # Gutxienez Pokemon bat proba izenarekin
    assert '_test_' in html_detail
    print(f"✓ Test Pokemon bat aurkitu da Onenak orrian (_test_)")

    # Max puntuazioa duen Pokemon-aren puntuazioa (600) egiaztatu
    assert '600' in html_detail
    print(f"✓ Max puntuazioa aurkitu da -> 600")

def test_get_onenak_talde_hutsa(logged_in_client, onenak_empty_team_test_data):
    """
    Talde huts baten Onenak orria probatzeko.
    Talde honek Pokemon-ik ez duela erakutsi behar du.
    """
    taldeIzena = "EMPTY_TEST_TEAM"

    # Taldearen Onenak orrira zuzenean sartu
    resp = logged_in_client.get(f'/chatbot/onenak/{taldeIzena}')
    assert resp.status_code == 200
    print(f"✓ Onenak orria kargatu da (200) -> {taldeIzena}")

    html = resp.data.decode('utf-8', errors='ignore').lower()

    # Mezua egiaztatu: "talde honek ez du pokemonik"
    assert "talde honek ez du pokemonik" in html
    print(f"✓ Mezua aurkitu da: talde honek ez du pokemonik")


def test_get_onenak_ez_dago_talderik(logged_in_client):
    """
    Onenak sakatzen du, baina ez dago talderik sortua
    """
    # Talde zerrenda orrira zuzenean sartu
    resp_list = logged_in_client.get('/chatbot/taldeZerrenda')
    assert resp_list.status_code == 200
    print(f"✓ Talde zerrenda orria kargatu da (200)")

    html = resp_list.data.decode('utf-8', errors='ignore').lower()

    # Mezua egiaztatu: "ez duzu talderik sortu"
    assert "ez duzu talderik sortu" in html
    print(f"✓ Mezua aurkitu da: ez duzu talderik sortu")


