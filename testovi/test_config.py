def test_config(client, auth_headers):
    podaci = {
        "naziv": "Test",
        "broj_terena": 1,
        "dan_turnira": "12.12.2027",
        "trajanje_meca": 25
    }
    odgovor = client.post("/config", json=podaci, headers=auth_headers)
    assert odgovor.status_code == 200