import os
import sys
from datetime import datetime, timezone

import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, render_template

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import UMBRALES

app = Flask(__name__)

DB_CONFIG = {
    "host": os.getenv("HIDRO_DB_HOST", "localhost"),
    "port": int(os.getenv("HIDRO_DB_PORT", "5432")),
    "dbname": os.getenv("HIDRO_DB_NAME", "hidroelectrica"),
    "user": os.getenv("HIDRO_DB_USER", "hidro"),
    "password": os.getenv("HIDRO_DB_PASSWORD", "hidro1234"),
}

VARIABLES = [
    ("represa", "nivel", "Nivel"),
    ("caudal", "caudal", "Caudal"),
    ("turbina", "rpm", "RPM"),
    ("turbina", "temperatura", "Temperatura"),
    ("generador", "voltaje", "Voltaje"),
]


def conectar_db():
    return psycopg2.connect(**DB_CONFIG)


def fecha_iso(valor):
    if isinstance(valor, datetime):
        return valor.astimezone(timezone.utc).isoformat()
    return valor


def estado_variable(variable, valor):
    if valor is None or variable not in UMBRALES:
        return "sin datos"
    rango = UMBRALES[variable]
    if valor < rango["min"] or valor > rango["max"]:
        return "alerta"
    return "normal"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/datos")
def datos():
    try:
        with conectar_db() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT DISTINCT ON (nodo, variable)
                           nodo, variable, valor, unidad, timestamp
                    FROM mediciones
                    ORDER BY nodo, variable, timestamp DESC
                    """
                )
                mediciones = {(r["nodo"], r["variable"]): r for r in cur.fetchall()}

                cur.execute(
                    """
                    SELECT timestamp, nodo, descripcion
                    FROM eventos
                    ORDER BY timestamp DESC
                    LIMIT 5
                    """
                )
                eventos = [dict(r) for r in cur.fetchall()]
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 503

    tarjetas = []
    for nodo, variable, nombre in VARIABLES:
        fila = mediciones.get((nodo, variable))
        valor = float(fila["valor"]) if fila else None
        tarjetas.append({
            "nodo": nodo,
            "variable": variable,
            "nombre": nombre,
            "valor": valor,
            "unidad": fila["unidad"] if fila else UMBRALES.get(variable, {}).get("unidad", ""),
            "estado": estado_variable(variable, valor),
            "timestamp": fecha_iso(fila["timestamp"]) if fila else None,
        })

    for evento in eventos:
        evento["timestamp"] = fecha_iso(evento["timestamp"])

    return jsonify({
        "ok": True,
        "actualizado": datetime.now(timezone.utc).isoformat(),
        "tarjetas": tarjetas,
        "eventos": eventos,
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)