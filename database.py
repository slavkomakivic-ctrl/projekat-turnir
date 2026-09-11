import sqlite3

konekcija1 = sqlite3.connect("korisnici.db", check_same_thread=False)
kursor1 = konekcija1.cursor()

konekcija = sqlite3.connect("turnir.db", check_same_thread=False)
kursor = konekcija.cursor()

kursor1.execute("""
    CREATE TABLE IF NOT EXISTS korisnici (
        id INTEGER PRIMARY KEY,
        korisnicko_ime TEXT UNIQUE,
        lozinka_hash TEXT
    )
""")
konekcija1.commit()

kursor.execute("""
    CREATE TABLE IF NOT EXISTS turnir (
        id INTEGER PRIMARY KEY,
        naziv TEXT,
        broj_terena INTEGER,
        dan_turnira DATE,
        trajanje_meca INTEGER
    )
""")

kursor.execute("""
    CREATE TABLE IF NOT EXISTS ekipa (
        id INTEGER PRIMARY KEY,
        naziv TEXT UNIQUE,
        grad TEXT,
        kontakt TEXT UNIQUE
    )
""")

kursor.execute("""
    CREATE TABLE IF NOT EXISTS imena_ucesnika (
        id INTEGER PRIMARY KEY,
        ekipa_id INTEGER,
        ime TEXT,
        FOREIGN KEY (ekipa_id) REFERENCES ekipa(id),
        UNIQUE (ekipa_id, ime)
    )
""")

kursor.execute("""
    CREATE TABLE IF NOT EXISTS mecevi (
        id INTEGER PRIMARY KEY,
        ekipa1_id INTEGER,
        ekipa2_id INTEGER,
        status TEXT CHECK(status IN ('Ceka', 'U_toku', 'Zavrsen')),
        pobjednik INTEGER,
        runda INTEGER DEFAULT 1,
        FOREIGN KEY (ekipa1_id) REFERENCES ekipa(id),
        FOREIGN KEY (ekipa2_id) REFERENCES ekipa(id),
        FOREIGN KEY (pobjednik) REFERENCES ekipa(id)
    )
""")

kursor.execute("""
    CREATE TABLE IF NOT EXISTS setovi (
        id INTEGER PRIMARY KEY,
        mec_id INTEGER,
        broj_seta INTEGER CHECK(broj_seta IN (1, 2, 3)),
        poeni_ekipa1 INTEGER,
        poeni_ekipa2 INTEGER,
        zavrsen_set BOOLEAN
    )
""")
konekcija.commit()