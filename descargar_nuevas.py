#!/usr/bin/env python3
"""
Descarga las cartas de las 3 expansiones nuevas de Pokemon TCG Pocket
(C1 Dual Fusion, SP1 Special Pack: First Partners, PROMO-C), usando
la base de datos publica de leanny.github.io/pocket_tcg_resources,
y las deja listas en este repo, una carpeta por expansion.

Uso:
    python descargar_nuevas.py

Requisitos (instalar una vez):
    pip install requests pillow
"""

import io
import sys
import time
from pathlib import Path

import requests
from PIL import Image

CARDMAP_URL = "https://leanny.github.io/pocket_tcg_resources/data/cardmap.json"
IMAGE_PREFIX = "https://leanny.github.io/pocket_tcg_resources/img/M/US/"

EXPANSIONES = ["C1", "SP1", "PROMO-C"]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


def obtener_cardmap() -> dict:
    print(f"Descargando el mapa de cartas desde {CARDMAP_URL} ...")
    resp = requests.get(CARDMAP_URL, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    return resp.json()


def conseguir_imagen(illustration_id: str) -> bytes:
    for ext in (".png", ".webp", ".jpg", ".jpeg"):
        url = f"{IMAGE_PREFIX}{illustration_id}{ext}"
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.ok:
            return resp.content
    raise FileNotFoundError(f"No se encontro la imagen para {illustration_id}")


def guardar_como_png(nombre_base: str, contenido: bytes, carpeta_salida: Path):
    imagen = Image.open(io.BytesIO(contenido)).convert("RGBA")
    ruta_salida = carpeta_salida / f"{nombre_base}.png"
    imagen.save(ruta_salida, "PNG")
    return ruta_salida


def main():
    try:
        cardmap = obtener_cardmap()
    except Exception as e:
        print(f"No se pudo bajar/leer cardmap.json: {e}")
        sys.exit(1)

    for expansion_id in EXPANSIONES:
        cartas = []
        for card_id, info in cardmap.items():
            if info.get("ExpansionID") == expansion_id:
                cartas.append(
                    {
                        "card_id": card_id,
                        "numero": info.get("CollectionNumber"),
                        "illustration_id": info.get("IllustrationID"),
                    }
                )
        cartas.sort(key=lambda c: (c["numero"] is None, c["numero"]))

        print(f"\n=== {expansion_id}: {len(cartas)} cartas ===")
        carpeta_salida = Path(f"cartas_{expansion_id}")
        carpeta_salida.mkdir(parents=True, exist_ok=True)

        ok, fallidas = 0, []
        for carta in cartas:
            illustration_id = carta["illustration_id"]
            numero = carta["numero"]
            if not illustration_id:
                fallidas.append(carta["card_id"])
                continue
            try:
                contenido = conseguir_imagen(illustration_id)
                ruta = guardar_como_png(illustration_id, contenido, carpeta_salida)
                print(f"  [{numero}] Guardada: {ruta.name}")
                ok += 1
            except Exception as e:
                print(f"  [{numero}] Error con {illustration_id}: {e}")
                fallidas.append(illustration_id)
            time.sleep(0.03)

        print(f"  -> {ok} guardadas, {len(fallidas)} fallidas en {carpeta_salida}/")
        if fallidas:
            for f in fallidas:
                print(f"     - {f}")


if __name__ == "__main__":
    main()
