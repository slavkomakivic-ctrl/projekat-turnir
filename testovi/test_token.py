import pytest

@pytest.mark.parametrize("metoda, ruta", [
    ("POST", "/config"),
    ("POST", "/napravi_grupe"),
    ("POST", "/napravi_meceve_grupa"),
    ("POST", "/napravi_nokaut_iz_grupa"),
    ("POST", "/generisi_raspored"),
    ("POST", "/azuriraj_raspored"),
    ("POST", "/zrijeb"),
    ("POST", "/sledeci_krug"),
    ("PUT", "/mecevi/1/pocni"),
    ("PUT", "/setovi/1"),
    ("GET", "/provjeri_prijavu")
])

def test_zasticene_rute(client, metoda, ruta):
    odgovor = client.request(metoda, ruta)
    assert odgovor.status_code == 401, odgovor.text