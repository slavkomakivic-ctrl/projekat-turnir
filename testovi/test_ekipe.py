def test_prikaz_ekipa_prazna_baza(client):
    odgovor = client.get("/prikazi_ekipe")
    assert odgovor.status_code == 200
    assert odgovor.json() == {"ekipe": []}

def test_prijava_ekipe(client):
    podaci = {
        "naziv": "Ekipa Test",
        "grad": "Test Grad",
        "kontakt": "065123456",
        "clanovi": [
            {"ime": "Clan 1"},
            {"ime": "Clan 2"},
            {"ime": "Clan 3"},
            {"ime": "Clan 4"},
            {"ime": "Clan 5"}
        ]}
    odgovor = client.post("/prijava_ekipe", json=podaci)
    assert odgovor.status_code == 200

def test_duplo_ime_ekipe_ne_kvari_bazu(client):
    podaci = {
        "naziv": "Ekipa Test", "grad": "Test Grad", "kontakt": "065123456",
        "clanovi": [{"ime": f"Clan {i}"} for i in range(1, 4)],
    }
    assert client.post("/prijava_ekipe", json=podaci).status_code == 200

    odgovor = client.post("/prijava_ekipe", json=podaci)
    assert odgovor.status_code == 400

    odgovor = client.get("/prikazi_ekipe")
    assert odgovor.status_code == 200
    assert len(odgovor.json()["ekipe"]) == 1