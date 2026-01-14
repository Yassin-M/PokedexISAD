import os
import sys
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import Config
from app import create_app
from app.database.database import Connection

#Probak egiteko ingurunearen sortzea
@pytest.fixture()
def ingurumenaSortu(tmp_path, monkeypatch):
    # Datu base bat sortu probak egiteko (programa amaitzean ezabatzen dena)
    monkeypatch.setattr(Config, "DB_PATH", str(tmp_path / "test.db"))

    app = create_app()
    app.config["TESTING"] = True

    conn = Connection()
    # Probetarako behar den erabiltzaileak datu basera sartu
    erabiltzaileak = [
        ("viewer", "pwd", "viewer@example.com", None, "usuario"),
        ("jon", "pwd", "jon@example.com", None, "usuario"),
        ("ane", "pwd", "ane@example.com", None, "usuario"),
        ("june", "pwd", "junez13@example.com", None, "usuario"),
        ("aner", "pwd", "anertxu@example.com", None, "usuario"),
        ("jone", "pwd", "jone2@example.com", None, "usuario"),
    ]
    for erabiltzailea in erabiltzaileak:
        conn.insert(
            "INSERT INTO Erabiltzailea (izena, pasahitza, email, jaiotze_data, rola) VALUES (?,?,?,?,?)",
            erabiltzailea,
        )
    # Gauza bera jarraipenekin
    jarraipenak = [
        ("viewer", "jon", True),
        ("viewer", "ane", True),
        ("viewer", "june", True),
        ("viewer", "aner", True),
    ]
    for jarraitzaileIzena, jarraituIzena, notifikatu in jarraipenak:
        conn.insert(
            "INSERT INTO JarraitzenDu (JarraitzaileIzena, JarraituIzena, Notifikatu) VALUES (?,?,?)",
            (jarraitzaileIzena, jarraituIzena, notifikatu),
        )
    # Notifikazioak ere bai sortu behar dira
    notifikazioak = [
        ("2025-02-10 10:00:00", "jon", "Jon-ek gimnasio berri bat gainditu du"),
        ("2025-01-15 12:00:00", "june", "June-ek Pikachu harrapatu du"),
        ("2025-01-05 08:30:00", "ane", "Ane-ek domina berri bat lortu du"),
        ("2025-02-12 14:45:00", "jone", "Jone-ek Bulbasaur harrapatu du"),
        ("2025-02-20 09:15:00", "aner", "Aner-ek gimnasio berri bat gainditu du"),
        ("2025-03-01 11:20:00", "aner", "Aner-ek Charizard harrapatu du"),
    ]
    for data, erabiltzailea, deskribapena in notifikazioak:
        conn.insert(
            "INSERT INTO Notifikatu (DataOrdua, ErabiltzaileIzena, deskripzioa) VALUES (?,?,?)",
            (data, erabiltzailea, deskribapena),
        )
    # Hemen saioa hasten da "viewer" erabiltzailearekin
    with app.test_client() as client:
        with client.session_transaction() as session:
            session["user"] = "viewer"
            session["role"] = "usuario"
        yield client

#3.3.1 Proba: Menutik Changelog-era joatea notifikazioak botoia sakatuz

    # Lehenik eta behin, konprobatu ea menu orrialdean changelog-era joateko botoia dagoen ala ez
def test_badago_botoia(ingurumenaSortu):
    respuesta = ingurumenaSortu.get("/menu")

    assert respuesta.status_code == 200
    html = respuesta.data.decode("utf-8").lower()

    assert "/changelog" in html

    # Botoia badagoela egiaztatu ondoren, sakatuz changelog orrialdera joaten dela egiaztatu
def test_botoia_klikatzerakoan_ondo_doa(ingurumenaSortu):
    respuesta = ingurumenaSortu.get("/changelog")

    assert respuesta.status_code == 200
    html = respuesta.data.decode("utf-8")

    assert "changelog" in html.lower()

    # Notifikazioak ondo kargatzen direla egiaztatu
def test_changelog_erantzuna_eta_edukia(ingurumenaSortu):
    erantzuna = ingurumenaSortu.get("/changelog")

    assert erantzuna.status_code == 200
    edukia = erantzuna.data.decode("utf-8").lower()

    assert "jon" in edukia
    assert "june" in edukia
    assert "aner" in edukia
    assert "ane" in edukia
    assert "jone" not in edukia
    assert "gimnasio berri" in edukia
    assert "domina berri" in edukia
    assert edukia.count("aner") >= 2

# 3.3.2 Proba: Izen bat bilatu eta notifikazioak filtratzen dira (datu base osoan izen bakarra dago eta notifikazio bakarra ere bai)
    # Bilaketa filtroa ondo doazela konprobatu
def test_changelog_filtratua_izenez(ingurumenaSortu):
    erantzuna = ingurumenaSortu.get("/changelog?bilatutako_erabiltzaile_izena=jon")

    assert erantzuna.status_code == 200
    edukia = erantzuna.data.decode("utf-8").lower()

    assert "jon" in edukia
    assert "june" not in edukia
    assert "aner" not in edukia
    assert "ane" not in edukia
    assert "jone" not in edukia
    assert "gimnasio berri" in edukia
    assert "domina berri" not in edukia
    assert edukia.count("jon") >= 2

# 3.3.3 Proba: Izen bat bilatu eta notifikazioak filtratu (datu basean izen bera edo partzialarekin erabiltzaile bat baino gehiago daude)
    # Bilaketa filtroa ondo doazela konprobatu
def test_changelog_filtratua_existitzen_diren_izenezkin(ingurumenaSortu):
    erantzuna = ingurumenaSortu.get("/changelog?bilatutako_erabiltzaile_izena=ane")

    assert erantzuna.status_code == 200
    edukia = erantzuna.data.decode("utf-8").lower()

    assert "jon" not in edukia
    assert "june" not in edukia
    assert "aner" in edukia
    assert "ane" in edukia
    assert "jone" not in edukia
    assert "gimnasio berri" in edukia
    assert "domina berri" in edukia

# 3.3.4: Existitzen ez den izen bat bilatu (ez da ezer agertuko)
    # Bilaketa filtroa ondo doazela konprobatu
def test_changelog_filtratua_existitzen_ez_den_izenez(ingurumenaSortu):
    erantzuna = ingurumenaSortu.get("/changelog?bilatutako_erabiltzaile_izena=agapito")

    assert erantzuna.status_code == 200
    edukia = erantzuna.data.decode("utf-8").lower()

    assert "jon" not in edukia
    assert "june" not in edukia
    assert "aner" not in edukia
    assert "ane" not in edukia
    assert "jone" not in edukia
    assert "gimnasio berri" not in edukia
    assert "domina berri" not in edukia

# 3.3.5: Izen partizal bat bilatu (osoa ez den izen bat)
    # Bilaketa filtroa ondo doazela konprobatu
def test_changelog_filtratua_izen_partzialez(ingurumenaSortu):
    erantzuna = ingurumenaSortu.get("/changelog?bilatutako_erabiltzaile_izena=an")

    assert erantzuna.status_code == 200
    edukia = erantzuna.data.decode("utf-8").lower()

    assert "jon" not in edukia
    assert "june" not in edukia
    assert "aner" in edukia
    assert "ane" in edukia
    assert "jone" not in edukia
    assert "gimnasio berri" in edukia
    assert "domina berri" in edukia

# 3.3.6: Nahiz eta ezer idatzi bilatu botoia sakatu (hasieran bezala agertuko da)
    # Bilaketa filtroa ondo doazela konprobatu
def test_changelog_filtratua_existitzen_ez_den_izenez(ingurumenaSortu):
    erantzuna = ingurumenaSortu.get("/changelog?bilatutako_erabiltzaile_izena=")

    assert erantzuna.status_code == 200
    edukia = erantzuna.data.decode("utf-8").lower()

    assert "jon" in edukia
    assert "june" in edukia
    assert "aner" in edukia
    assert "ane" in edukia
    assert "jone" not in edukia
    assert "gimnasio berri" in edukia
    assert "domina berri" in edukia
    assert edukia.count("aner") >= 2

# 3.3.7 Proba: Erabiltzailea home botoia sakatzen badu ondo doa eta menu nagusira bidaliko du
    # Lehenik eta behin konprobatu botoi hori existitzen dela
def test_changelog_home_botoia_badauka(ingurumenaSortu):
    respuesta = ingurumenaSortu.get("/changelog")

    assert respuesta.status_code == 200
    html = respuesta.data.decode("utf-8").lower()

    assert "/menu" in html

    # Konprobatu existitzen dela ostean frogatu ondo funtzionatzen den
def test_home_botoia_ondo_doa(ingurumenaSortu):
    respuesta = ingurumenaSortu.get("/menu")

    assert respuesta.status_code == 200
    html = respuesta.data.decode("utf-8").lower()

    assert "menu" in html 

