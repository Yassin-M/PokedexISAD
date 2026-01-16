import pytest

from config import Config
from app import create_app
from app.database.database import Connection


@pytest.fixture()
def login_client(tmp_path, monkeypatch):
    """Login probetarako app eta DB isolatua sortu."""
    monkeypatch.setattr(Config, "DB_PATH", str(tmp_path / "login_test.db"))
    app = create_app()
    app.config["TESTING"] = True

    # Erabiltzaile arrunta sortu login probetarako
    Connection().insert(
        "INSERT INTO Erabiltzailea (izena, pasahitza, email, jaiotze_data, rola) VALUES (?,?,?,?,?)",
        ("Jon", "Jon123", "jon@adibidea.com", None, "usuario"),
    )

    return app.test_client()


# 3.1.1: Baliozko kredentzialak eta menu nagusira sartzen da
def test_login_ondo_menu_nagusira(login_client):
    response = login_client.post(
        "/login",
        data={"erabiltzailea": "Jon", "password": "Jon123"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert response.request.path == "/menu"
    assert "TALDEAK" in response.data.decode("utf-8")


# 3.1.2: Izen zuzena baina pasahitza okerra
def test_pasahitza_okerra_hutsegin(login_client):
    response = login_client.post(
        "/login",
        data={"erabiltzailea": "Jon", "password": "Okerra123"},
        follow_redirects=True,
    )

    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert response.request.path == "/login"
    assert "Pasahitza okerra" in html


# 3.1.3: Existitzen ez diren kredentzialak
def test_erabiltzaile_ez_dago_hutsegin(login_client):
    response = login_client.post(
        "/login",
        data={"erabiltzailea": "Ander", "password": "Pass123"},
        follow_redirects=True,
    )

    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert response.request.path == "/login"
    assert "Erabiltzailea ez da existitzen" in html


# 3.1.4: Eremu bat hutsik
def test_hutsuneak_ez_du_saioa_hasi(login_client):
    response = login_client.post(
        "/login",
        data={"erabiltzailea": "Jon", "password": ""},
        follow_redirects=True,
    )

    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert response.request.path == "/login"
    assert "Mesedez, bete eremu guztiak" in html


# 3.1.5: Erregistratu botoia sakatzen du
def test_erregistratu_botoia_orrira(login_client):
    response = login_client.get("/register")

    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert response.request.path == "/register"
    assert "ERREGISTRATU" in html
