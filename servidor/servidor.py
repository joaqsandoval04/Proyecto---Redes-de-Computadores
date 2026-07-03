import socket
import threading
import json
import hmac
import hashlib
import psycopg2
from datetime import datetime, timezone
from config import SERVER_HOST, SERVER_PORT, HMAC_KEY, UMBRALES, NODOS_VALIDOS

#  Conexión a la base de datos 
def conectar_db():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="hidroelectrica",
        user="hidro",
        password="hidro1234"
    )

#  Verificación HMAC 
def verificar_hmac(mensaje: dict, hmac_recibido: str) -> bool:
    copia = {k: v for k, v in mensaje.items() if k != "hmac"}
    contenido = json.dumps(copia, sort_keys=True).encode()
    hmac_calculado = hmac.new(HMAC_KEY, contenido, hashlib.sha256).hexdigest()
    return hmac.compare_digest(hmac_calculado, hmac_recibido)

#  Evaluación de umbrales 
def evaluar_umbral(nodo: str, variable: str, valor: float, db) -> dict:
    if variable not in UMBRALES:
        return {"status": "ok"}

    rango = UMBRALES[variable]
    respuesta = {"status": "ok"}

    if valor < rango["min"] or valor > rango["max"]:
        descripcion = (
            f"{variable} fuera de rango en {nodo}: "
            f"{valor} {rango['unidad']} "
            f"(rango: {rango['min']}–{rango['max']})"
        )
        print(f"[ALERTA] {descripcion}")

        # Guardar evento en DB
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO eventos (nodo, tipo, descripcion) VALUES (%s, %s, %s)",
                (nodo, "alerta", descripcion)
            )

        # Determinar comando de actuación
        comando, parametro = resolver_comando(nodo, variable, valor, rango)

        if comando:
            with db.cursor() as cur:
                cur.execute(
                    "INSERT INTO comandos (nodo_destino, comando, parametro) VALUES (%s, %s, %s)",
                    (nodo, comando, parametro)
                )
            respuesta = {"status": "comando", "comando": comando, "parametro": parametro}

        db.commit()

    return respuesta

#  Lógica de actuación 
def resolver_comando(nodo: str, variable: str, valor: float, rango: dict):
    if variable == "nivel":
        if valor > rango["max"]:
            return "cerrar_compuerta", 0.0
        if valor < rango["min"]:
            return "abrir_compuerta", 100.0

    if variable == "caudal":
        if valor > rango["max"]:
            return "cerrar_compuerta", 50.0
        if valor < rango["min"]:
            return "abrir_compuerta", 50.0

    if variable == "temperatura":
        if valor > rango["max"]:
            return "reducir_caudal", 30.0

    return None, None

#  Guardar medición 
def guardar_medicion(nodo: str, variable: str, valor: float, db):
    unidad = UMBRALES[variable]["unidad"] if variable in UMBRALES else ""
    with db.cursor() as cur:
        cur.execute(
            "INSERT INTO mediciones (nodo, variable, valor, unidad) VALUES (%s, %s, %s, %s)",
            (nodo, variable, valor, unidad)
        )
    db.commit()

#  Manejo de cada cliente 
def manejar_cliente(conn, addr):
    print(f"[+] Nodo conectado: {addr}")
    db = conectar_db()

    try:
        buffer = ""
        while True:
            datos = conn.recv(4096).decode()
            if not datos:
                break

            buffer += datos
            while "\n" in buffer:
                linea, buffer = buffer.split("\n", 1)
                linea = linea.strip()
                if not linea:
                    continue

                try:
                    mensaje = json.loads(linea)
                except json.JSONDecodeError:
                    conn.sendall(b'{"status": "error", "detalle": "JSON invalido"}\n')
                    continue

                # Validar campos obligatorios
                campos = {"nodo", "variable", "valor", "timestamp", "hmac"}
                if not campos.issubset(mensaje):
                    conn.sendall(b'{"status": "error", "detalle": "campos faltantes"}\n')
                    continue

                # Validar nodo reconocido
                if mensaje["nodo"] not in NODOS_VALIDOS:
                    conn.sendall(b'{"status": "error", "detalle": "nodo desconocido"}\n')
                    continue

                # Verificar HMAC
                if not verificar_hmac(mensaje, mensaje["hmac"]):
                    print(f"[!] HMAC invalido desde {addr}")
                    conn.sendall(b'{"status": "error", "detalle": "hmac invalido"}\n')
                    continue

                nodo     = mensaje["nodo"]
                variable = mensaje["variable"]
                valor    = float(mensaje["valor"])

                print(f"[{nodo}] {variable}: {valor}")

                guardar_medicion(nodo, variable, valor, db)
                respuesta = evaluar_umbral(nodo, variable, valor, db)

                conn.sendall((json.dumps(respuesta) + "\n").encode())

    except Exception as e:
        print(f"[ERROR] {addr}: {e}")
    finally:
        db.close()
        conn.close()
        print(f"[-] Nodo desconectado: {addr}")

#  Main 
def main():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((SERVER_HOST, SERVER_PORT))
    servidor.listen()
    print(f"[*] Servidor escuchando en {SERVER_HOST}:{SERVER_PORT}")

    while True:
        conn, addr = servidor.accept()
        hilo = threading.Thread(target=manejar_cliente, args=(conn, addr), daemon=True)
        hilo.start()

if __name__ == "__main__":
    main()