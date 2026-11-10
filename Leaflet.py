import logging
import os
from typing import Optional
from urllib.parse import urlsplit

import pymysql
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from pymysql.cursors import DictCursor

load_dotenv()

app = FastAPI(title="Leaflet-Karte")
logger = logging.getLogger(__name__)


class LocationInput(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str = Field(min_length=1, max_length=2000)
    link: Optional[str] = Field(default=None, max_length=2048)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


def get_database_connection():
    required_settings = ("DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME")
    missing_settings = [key for key in required_settings if not os.getenv(key)]
    if missing_settings:
        logger.error("Missing required database settings: %s", ", ".join(missing_settings))
        raise HTTPException(
            status_code=503,
            detail="Die Datenbank ist derzeit nicht konfiguriert.",
        )

    return pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        charset="utf8mb4",
        cursorclass=DictCursor,
        connect_timeout=5,
    )


def validate_location(location: LocationInput) -> tuple[str, str, str]:
    name = location.name.strip()
    description = location.description.strip()
    link = location.link.strip() if location.link else None

    if not name or not description:
        raise HTTPException(
            status_code=422,
            detail="Name und Beschreibung dürfen nicht leer sein.",
        )

    if link:
        try:
            parsed_link = urlsplit(link)
        except ValueError:
            parsed_link = None
        if (
            parsed_link is None
            or parsed_link.scheme not in {"http", "https"}
            or not parsed_link.netloc
            or parsed_link.username
            or parsed_link.password
        ):
            raise HTTPException(
                status_code=422,
                detail="Der Link muss eine gültige HTTP- oder HTTPS-Adresse sein.",
            )
    else:
        # The locations table defines Link as NOT NULL and has no default.
        link = ""

    return name, description, link


@app.get("/api/locations")
def list_locations() -> list[dict]:
    connection = None
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT `ID` AS id, `Name` AS name, `Beschreibung` AS description,
                       `Link` AS link, `latitude` AS latitude, `longitude` AS longitude
                FROM `locations`
                ORDER BY `ID`
                """
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": row["id"],
                    "name": row["name"],
                    "description": row["description"],
                    "link": row["link"],
                    "latitude": float(row["latitude"]),
                    "longitude": float(row["longitude"]),
                }
                for row in rows
            ]
    except pymysql.MySQLError as exc:
        logger.exception("Could not load locations from MariaDB")
        raise HTTPException(
            status_code=503,
            detail="Die Marker konnten derzeit nicht aus der Datenbank geladen werden.",
        ) from exc
    finally:
        if connection is not None:
            connection.close()


@app.post("/api/locations", status_code=201)
def create_location(location: LocationInput) -> dict:
    name, description, link = validate_location(location)
    connection = None
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO `locations`
                    (`Name`, `Beschreibung`, `Link`, `latitude`, `longitude`)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    name,
                    description,
                    link,
                    location.latitude,
                    location.longitude,
                ),
            )
            location_id = cursor.lastrowid
        connection.commit()
        return {
            "id": location_id,
            "name": name,
            "description": description,
            "link": link,
            "latitude": location.latitude,
            "longitude": location.longitude,
        }
    except pymysql.MySQLError as exc:
        if connection is not None:
            connection.rollback()
        logger.exception("Could not save a location to MariaDB")
        raise HTTPException(
            status_code=503,
            detail="Der Marker konnte derzeit nicht in der Datenbank gespeichert werden.",
        ) from exc
    finally:
        if connection is not None:
            connection.close()


@app.get("/", response_class=HTMLResponse)
async def show_map() -> str:
    return """<!doctype html>
<html lang="de">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Orte auf der Karte</title>
    <link
        rel="stylesheet"
        href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
        integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
        crossorigin=""
    >
    <style>
        html, body, #map {
            width: 100%;
            height: 100%;
            margin: 0;
        }

        .map-heading {
            position: absolute;
            z-index: 1000;
            top: 16px;
            left: 56px;
            padding: 10px 14px;
            border-radius: 6px;
            background: #fff;
            box-shadow: 0 1px 5px rgb(0 0 0 / 35%);
            font: 16px/1.4 Arial, sans-serif;
        }

        .map-heading strong {
            display: block;
        }

        #location-dialog {
            width: min(420px, calc(100% - 48px));
            border: 0;
            border-radius: 8px;
            box-shadow: 0 2px 18px rgb(0 0 0 / 35%);
            font: 15px/1.4 Arial, sans-serif;
        }

        #location-dialog::backdrop {
            background: rgb(0 0 0 / 35%);
        }

        #location-form label {
            display: block;
            margin-top: 12px;
            font-weight: 600;
        }

        #location-form input, #location-form textarea {
            box-sizing: border-box;
            width: 100%;
            padding: 8px;
            margin-top: 4px;
            border: 1px solid #aaa;
            border-radius: 4px;
            font: inherit;
        }

        #location-form textarea {
            min-height: 90px;
            resize: vertical;
        }

        .form-actions {
            display: flex;
            justify-content: flex-end;
            gap: 8px;
            margin-top: 16px;
        }

        .form-actions button {
            padding: 8px 12px;
            cursor: pointer;
        }

        #form-error {
            color: #a40000;
        }

        .location-popup p {
            margin: 6px 0;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <div class="map-heading">
        <strong>Orte auf der Karte</strong>
        Vorhandene Marker auswählen oder auf die Karte klicken, um einen Ort hinzuzufügen.
    </div>
    <div id="map" aria-label="Interaktive Karte"></div>
    <dialog id="location-dialog">
        <form id="location-form">
            <h2>Neuen Ort hinzufügen</h2>
            <p id="coordinates"></p>
            <label>
                Name
                <input name="name" maxlength="150" required>
            </label>
            <label>
                Beschreibung
                <textarea name="description" maxlength="2000" required></textarea>
            </label>
            <label>
                Link (optional)
                <input name="link" type="url" maxlength="2048" placeholder="https://example.com">
            </label>
            <p id="form-error" role="alert" hidden></p>
            <div class="form-actions">
                <button type="button" id="cancel-button">Abbrechen</button>
                <button type="submit" id="submit-button">Speichern</button>
            </div>
        </form>
    </dialog>
    <script
        src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
        integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
        crossorigin=""
    ></script>
    <script>
        const map = L.map("map").setView([51.1657, 10.4515], 6);
        const dialog = document.getElementById("location-dialog");
        const form = document.getElementById("location-form");
        const coordinates = document.getElementById("coordinates");
        const formError = document.getElementById("form-error");
        const submitButton = document.getElementById("submit-button");
        let selectedCoordinates = null;

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        function addLocationMarker(location) {
            const popup = document.createElement("div");
            popup.className = "location-popup";

            const name = document.createElement("strong");
            name.textContent = location.name;
            popup.appendChild(name);

            const description = document.createElement("p");
            description.textContent = location.description;
            popup.appendChild(description);

            if (location.link) {
                const link = document.createElement("a");
                link.textContent = location.link;
                let parsedLink = null;
                try {
                    parsedLink = new URL(location.link);
                } catch {
                    parsedLink = null;
                }
                if (parsedLink && ["http:", "https:"].includes(parsedLink.protocol)) {
                    link.href = parsedLink.href;
                    link.target = "_blank";
                    link.rel = "noopener noreferrer";
                } else {
                    link.removeAttribute("href");
                }
                popup.appendChild(link);
            }

            L.marker([location.latitude, location.longitude])
                .addTo(map)
                .bindPopup(popup);
        }

        async function loadLocations() {
            const response = await fetch("/api/locations");
            if (!response.ok) {
                let detail = `HTTP ${response.status}`;
                try {
                    const result = await response.json();
                    if (result.detail) {
                        detail = result.detail;
                    }
                } catch {
                    // Keep the HTTP status when the response is not JSON.
                }
                throw new Error(`Die Marker konnten nicht geladen werden: ${detail}`);
            }
            const locations = await response.json();
            locations.forEach(addLocationMarker);
        }

        loadLocations().catch((error) => {
            window.alert(error.message);
        });

        map.on("click", (event) => {
            selectedCoordinates = event.latlng;
            coordinates.textContent =
                `Position: ${selectedCoordinates.lat.toFixed(5)}, ${selectedCoordinates.lng.toFixed(5)}`;
            form.reset();
            formError.hidden = true;
            formError.textContent = "";
            dialog.showModal();
            form.elements.name.focus();
        });

        document.getElementById("cancel-button").addEventListener("click", () => {
            dialog.close();
        });

        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            if (!selectedCoordinates) {
                return;
            }

            formError.hidden = true;
            submitButton.disabled = true;
            try {
                const formData = new FormData(form);
                const response = await fetch("/api/locations", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        name: formData.get("name"),
                        description: formData.get("description"),
                        link: formData.get("link") || null,
                        latitude: selectedCoordinates.lat,
                        longitude: selectedCoordinates.lng
                    })
                });

                if (!response.ok) {
                    const result = await response.json();
                    throw new Error(result.detail || "Der Ort konnte nicht gespeichert werden.");
                }

                const savedLocation = await response.json();
                addLocationMarker(savedLocation);
                dialog.close();
                form.reset();
            } catch (error) {
                formError.textContent = error.message || "Der Ort konnte nicht gespeichert werden.";
                formError.hidden = false;
            } finally {
                submitButton.disabled = false;
            }
        });
    </script>
</body>
</html>"""
