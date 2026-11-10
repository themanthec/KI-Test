import os
from pathlib import Path

import pymysql
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

required_settings = ("DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME")
missing_settings = [name for name in required_settings if not os.getenv(name)]
if missing_settings:
    raise SystemExit(
        "Fehlende Datenbank-Einstellungen in .env: " + ", ".join(missing_settings)
    )

conn = pymysql.connect(
    host=os.environ["DB_HOST"],
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    database=os.environ["DB_NAME"],
    charset="utf8mb4",
    connect_timeout=5,
)

print("Verbindung erfolgreich")

try:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM `Kategorie` WHERE `Beschreibung` LIKE %s",
            ("%Florian%",),
        )
        print(" | ".join(column[0] for column in cur.description))
        for row in cur:
            print(" | ".join(str(value) for value in row))
finally:
    conn.close()
