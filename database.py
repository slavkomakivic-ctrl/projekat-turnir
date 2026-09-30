import threading
from dotenv import load_dotenv
import psycopg2
import os

class ThreadLocalCursor:
    """Daje svakom threadu zaseban cursor nad postojećom konekcijom."""

    def __init__(self, konekcija):
        self.konekcija = konekcija
        self.lokalni_podaci = threading.local()

    def _cursor(self):
        if not hasattr(self.lokalni_podaci, "kursor"):
            self.lokalni_podaci.kursor = self.konekcija.cursor()
        return self.lokalni_podaci.kursor

    def __getattr__(self, naziv):
        return getattr(self._cursor(), naziv)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


if DATABASE_URL:
    konekcija1 = psycopg2.connect(DATABASE_URL)
else:
    konekcija1 = psycopg2.connect(
        dbname="korisnici_db",
        user="postgres",
        password= os.getenv("SIFRA"),
        host=os.getenv("DB_HOST", "localhost"),
        port="5432"
        )
kursor1 = ThreadLocalCursor(konekcija1)

kursor1.execute("""
    CREATE TABLE IF NOT EXISTS korisnici (
        id SERIAL PRIMARY KEY,
        korisnicko_ime TEXT UNIQUE,
        lozinka_hash TEXT
    )
""")
konekcija1.commit()

if DATABASE_URL:
    konekcija = psycopg2.connect(DATABASE_URL)
else:
    konekcija = psycopg2.connect(
        dbname="projekat_turnir_db",
        user="postgres",
        password=os.getenv("SIFRA"),
        host=os.getenv("DB_HOST", "localhost"),
        port="5432"
    )
kursor = ThreadLocalCursor(konekcija)

kursor.execute("""
    CREATE TABLE IF NOT EXISTS turnir (
        id SERIAL PRIMARY KEY,
        naziv TEXT,
        broj_terena INTEGER,
        dan_turnira DATE,
        trajanje_meca INTEGER
    )
""")

kursor.execute("""
    CREATE TABLE IF NOT EXISTS grupe (
        id SERIAL PRIMARY KEY,
        naziv TEXT
    )
""")

kursor.execute("""
    CREATE TABLE IF NOT EXISTS ekipa (
        id SERIAL PRIMARY KEY,
        naziv TEXT UNIQUE,
        grad TEXT,
        kontakt TEXT UNIQUE,
        grupa_id INTEGER,
        FOREIGN KEY (grupa_id) REFERENCES grupe(id)
    )
""")

kursor.execute("""
    CREATE TABLE IF NOT EXISTS imena_ucesnika (
        id SERIAL PRIMARY KEY,
        ekipa_id INTEGER,
        ime TEXT,
        FOREIGN KEY (ekipa_id) REFERENCES ekipa(id),
        UNIQUE (ekipa_id, ime)
    )
""")

kursor.execute("""
    CREATE TABLE IF NOT EXISTS mecevi (
        id SERIAL PRIMARY KEY,
        ekipa1_id INTEGER,
        ekipa2_id INTEGER,
        status TEXT CHECK(status IN ('Ceka', 'U_toku', 'Zavrsen')),
        pobjednik INTEGER,
        runda INTEGER DEFAULT 1,
        faza TEXT DEFAULT 'nokaut',
        grupa_id INTEGER,
        kolo INTEGER,
        servirajuca_ekipa INTEGER,
        FOREIGN KEY (ekipa1_id) REFERENCES ekipa(id),
        FOREIGN KEY (ekipa2_id) REFERENCES ekipa(id),
        FOREIGN KEY (pobjednik) REFERENCES ekipa(id),
        FOREIGN KEY (grupa_id) REFERENCES grupe(id)
    )
""")

kursor.execute("""
    CREATE TABLE IF NOT EXISTS setovi (
        id SERIAL PRIMARY KEY,
        mec_id INTEGER,
        broj_seta INTEGER CHECK(broj_seta IN (1, 2, 3)),
        poeni_ekipa1 INTEGER,
        poeni_ekipa2 INTEGER,
        zavrsen_set BOOLEAN
    )
""")

kursor.execute("""
    CREATE TABLE IF NOT EXISTS raspored (
        id SERIAL PRIMARY KEY,
        mec_id INTEGER,
        teren INTEGER,
        vrijeme_pocetka TEXT
    )
""")
konekcija.commit()