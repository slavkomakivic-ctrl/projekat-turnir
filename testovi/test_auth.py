def test_registracija_login_i_zasticena_ruta(client):
    # 1. Registracija: obični JSON, kao svaki POST koji već znaš
    odgovor = client.post("/registracija", json={
        "korisnicko_ime": "sudija1",
        "lozinka": "tajna123",
    })
    assert odgovor.status_code == 200

    # 2. Login: OAuth2 forma šalje FORMU, pa ide data=, a ne json=
    #    Polja se uvijek zovu username i password, bez obzira na tvoja imena
    odgovor = client.post("/login", data={
        "username": "sudija1",
        "password": "tajna123",
    })
    assert odgovor.status_code == 200
    token = odgovor.json()["access_token"]

    # 3. Zaštićena ruta: token šalješ u zaglavlju
    odgovor = client.get(
        "/provjeri_prijavu",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert odgovor.status_code == 200

def test_duplo_korisnicko_ime_ne_kvari_login(client):
    podaci = {"korisnicko_ime": "sudija1", "lozinka": "tajna123"}
    assert client.post("/registracija", json=podaci).status_code == 200

    odgovor = client.post("/registracija", json=podaci)
    assert odgovor.status_code == 409

    odgovor = client.post("/login", data={
        "username": "sudija1", "password": "tajna123",
    })
    assert odgovor.status_code == 200