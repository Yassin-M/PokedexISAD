import pytest

from config import Config
from app import create_app
from app.database.database import Connection


@pytest.fixture()
def register_client(tmp_path, monkeypatch):
    """Erregistro probetarako app eta DB isolatua sortu."""
    monkeypatch.setattr(Config, "DB_PATH", str(tmp_path / "register_test.db"))
    app = create_app()
    app.config["TESTING"] = True

    return app.test_client()


# 3.1.6: Pasahitza karaktere espezialak ditu
def test_pasahitza_karaktere_espezialak(register_client):
    response = register_client.post(
        "/register",
        data={
            "erabiltzailea": "Jon",
            "email": "jon@adibidea.com",
            "jaiotze_data": "2000-01-01",
            "pasahitza": "Jon|123",
            "pasahitza_berretsi": "Jon|123",
        },
        follow_redirects=True,
    )

    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert response.request.path == "/register"
    assert "Pasahitzak ezin du karaktere hau izan:" in html


# 3.1.7: Pasahitzak ez datoz bat
def test_pasahitzak_ez_datoz_bat(register_client):
    response = register_client.post(
        "/register",
        data={
            "erabiltzailea": "Jon",
            "email": "jon@adibidea.com",
            "jaiotze_data": "2000-01-01",
            "pasahitza": "Jon123",
            "pasahitza_berretsi": "Jon456",
        },
        follow_redirects=True,
    )

    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert response.request.path == "/register"
    assert "Pasahitzak ez datoz bat" in html


# 3.1.8: Posta elektroniko baliogabea
def test_posta_baliogabea(register_client):
    response = register_client.post(
        "/register",
        data={
            "erabiltzailea": "Jon",
            "email": "emailbaliogabea",
            "jaiotze_data": "2000-01-01",
            "pasahitza": "Jon123",
            "pasahitza_berretsi": "Jon123",
        },
        follow_redirects=True,
    )

    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert response.request.path == "/register"


# 3.1.9: Jaiotze data baliogabea
def test_jaiotze_data_baliogabea(register_client):
    response = register_client.post(
        "/register",
        data={
            "erabiltzailea": "Jon",
            "email": "jon@adibidea.com",
            "jaiotze_data": "ez-data-egokia",
            "pasahitza": "Jon123",
            "pasahitza_berretsi": "Jon123",
        },
        follow_redirects=True,
    )

    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert response.request.path == "/register"


# 3.1.10: Eremu bat hutsik
def test_eremu_bat_hutsik(register_client):
    response = register_client.post(
        "/register",
        data={
            "erabiltzailea": "",
            "email": "jon@adibidea.com",
            "jaiotze_data": "2000-01-01",
            "pasahitza": "Jon123",
            "pasahitza_berretsi": "Jon123",
        },
        follow_redirects=True,
    )

    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert response.request.path == "/register"
    assert "Mesedez, bete eremu guztiak" in html


# 3.1.11: Erregistro egokia
def test_erregistro_egokia(register_client):
    response = register_client.post(
        "/register",
        data={
            "erabiltzailea": "Jon",
            "email": "jon@example.com",
            "jaiotze_data": "2000-01-01",
            "pasahitza": "Jon123",
            "pasahitza_berretsi": "Jon123",
        },
        follow_redirects=True,
    )

    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert response.request.path == "/login"
    assert "Erabiltzailea behar bezala erregistratu da" in html
    assert "Saioa hasi dezakezu orain" in html
