import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
os.environ["DATABASE_URL"] = (
    f"postgresql://postgres:{os.getenv('SIFRA')}@localhost:5432/turnir_test"
)

import pytest
from fastapi.testclient import TestClient

from main import app
from database import konekcija, kursor, konekcija1

TABELE = [
    "korisnici", "turnir", "grupe", "ekipa",
    "imena_ucesnika", "mecevi", "setovi", "raspored",
]


@pytest.fixture(autouse=True)
def cista_baza():
    assert konekcija.info.dbname == "turnir_test", "Testovi nisu na test bazi!"
    konekcija.rollback()
    konekcija1.rollback()
    kursor.execute(f"TRUNCATE {', '.join(TABELE)} RESTART IDENTITY CASCADE")
    konekcija.commit()
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    korisnik = {"korisnicko_ime": "sudija1", "lozinka": "tajna123",}
    registrovan = client.post("/registracija", json=korisnik)
    assert registrovan.status_code == 200, registrovan.text
    
    odgovor = client.post("/login", data={"username": "sudija1", "password": "tajna123"})
    assert odgovor.status_code == 200, odgovor.text
    
    token = odgovor.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def db_kursor():
    return kursor