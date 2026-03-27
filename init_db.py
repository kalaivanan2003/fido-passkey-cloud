"""
init_db.py — Run this ONCE to create the SQLite database.
Usage:  python init_db.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'fidoclouddb.sqlite')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS regtb (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            Name          TEXT    NOT NULL,
            Mobile        TEXT    NOT NULL,
            Email         TEXT    NOT NULL,
            Address       TEXT    NOT NULL,
            UserName      TEXT    NOT NULL,
            Password      TEXT    NOT NULL,
            Status        TEXT    NOT NULL DEFAULT 'waiting',
            Pubkey        TEXT    NOT NULL DEFAULT '',
            Prikey        TEXT    NOT NULL DEFAULT '',
            prikey1       TEXT    NOT NULL DEFAULT '',
            prikey2       TEXT    NOT NULL DEFAULT '',
            face_encoding TEXT
        );

        CREATE TABLE IF NOT EXISTS backuptb (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            UserName TEXT    NOT NULL,
            Enckey   TEXT    NOT NULL,
            pubkey   TEXT    NOT NULL,
            prikey2  TEXT    NOT NULL,
            Qrcode   TEXT    NOT NULL,
            Hash1    TEXT    NOT NULL,
            Hash2    TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS filetb (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            OwnerName TEXT    NOT NULL,
            FileInfo  TEXT    NOT NULL,
            FileName  TEXT    NOT NULL,
            Pukey     TEXT    NOT NULL,
            Pvkey     TEXT    NOT NULL,
            hash1     TEXT    NOT NULL,
            hash2     TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS temptb (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            UserName TEXT    NOT NULL
        );
    """)

    conn.commit()
    conn.close()
    print(f"SQLite database initialised at: {DB_PATH}")

if __name__ == '__main__':
    init_db()
