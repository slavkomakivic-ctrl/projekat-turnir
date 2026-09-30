def test_provjera_seta(client, auth_headers, db_kursor):
    # 1. Registracija ekipe
    podaci_ekipa1 = {
        "naziv": "Ekipa Test1",
        "grad": "Test Grad1",
        "kontakt": "065123456",
        "clanovi": [
            {"ime": "Clan 1"},
            {"ime": "Clan 2"},
            {"ime": "Clan 3"},
            {"ime": "Clan 4"},
            {"ime": "Clan 5"}
        ]
    }
    odgovor = client.post("/prijava_ekipe", json=podaci_ekipa1)
    assert odgovor.status_code == 200
    podaci_ekipa2 = {
            "naziv": "Ekipa Test2",
            "grad": "Test Grad2",
            "kontakt": "065654321",
            "clanovi": [
                {"ime": "Clan 1"},
                {"ime": "Clan 2"},
                {"ime": "Clan 3"},
                {"ime": "Clan 4"},
                {"ime": "Clan 5"}
            ]
        }
    odgovor = client.post("/prijava_ekipe", json=podaci_ekipa2)
    assert odgovor.status_code == 200

    #Kreiranje meca
    odgovor = client.post("/zrijeb", headers=auth_headers)
    assert odgovor.status_code == 200

    # 2. Dodavanje seta
    podaci_seta = {
        "mec_id": 1,
        "broj_seta": 1,
        "poeni_ekipa1": 15,
        "poeni_ekipa2": 10,
        "zavrsen_set": True,
        "poen_ekipa": 1,
        "servirajuca_ekipa": 1
    }
    setovi = client.put("/setovi/1", headers=auth_headers, json=podaci_seta)
    assert setovi.status_code == 200
    
    #3. Provjera statusa meca nakon zavrsetka seta
    db_kursor.execute("SELECT status, pobjednik FROM mecevi WHERE id = 1")
    status, pobjednik = db_kursor.fetchone()
    assert status == "U_toku"
    assert pobjednik is None

    #4. Dodavanje drugog seta
    podaci_seta = {
        "mec_id": 1,
        "broj_seta": 2,
        "poeni_ekipa1": 15,
        "poeni_ekipa2": 7,
        "zavrsen_set": True,
        "poen_ekipa": 1,
        "servirajuca_ekipa": 1
    }
    setovi = client.put("/setovi/2", headers=auth_headers, json=podaci_seta)
    assert setovi.status_code == 200
    
    #5. Provjera statusa meca nakon zavrsetka drugog seta i provjera pobjednika
    db_kursor.execute("SELECT status, pobjednik, ekipa1_id FROM mecevi WHERE id = 1")
    status, pobjednik, ekipa1_id = db_kursor.fetchone()
    assert status == "Zavrsen"
    assert pobjednik == ekipa1_id

