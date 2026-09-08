import sqlite3

konekcija = sqlite3.connect("korisnici.db", check_same_thread=False)
kursor = konekcija.cursor()

kursor.execute("""
    CREATE TABLE IF NOT EXISTS korisnici (
        id INTEGER PRIMARY KEY,
        korisnicko_ime TEXT UNIQUE,
        lozinka_hash TEXT
    )
""")
konekcija.commit()