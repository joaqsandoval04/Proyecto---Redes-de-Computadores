import socket
import json
import hmac
import hashlib
import time
from datetime import datetime, timezone
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SERVER_HOST, SERVER_PORT, HMAC_KEY

def firmar_mensaje(mensaje: dict) -> str:
    copia = {k: v for k, v in mensaje.items() if k != "hmac"}
    contenido = json.dumps(copia, sort_keys=True).encode()
    return hmac.new(HMAC_KEY, contenido, hashlib.sha256).hexdigest()

def enviar_medicion(conn, nodo: str, variable: str, valor: float) -> dict:
    mensaje = {
        "nodo":      nodo,
        "variable":  variable,
        "valor":     round(valor, 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    mensaje["hmac"] = firmar_mensaje(mensaje)
    conn.sendall((json.dumps(mensaje) + "\n").encode())

    # Leer respuesta hasta encontrar delimitador
    buffer = ""
    while "\n" not in buffer:
        chunk = conn.recv(1024).decode()
        if not chunk:
            raise ConnectionError("Servidor cerró la conexión")
        buffer += chunk

    return json.loads(buffer.strip())

def conectar_servidor(nombre: str) -> socket.socket:
    while True:
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((SERVER_HOST, SERVER_PORT))
            print(f"[{nombre}] Conectado al servidor")
            return conn
        except ConnectionRefusedError:
            print(f"[{nombre}] Servidor no disponible, reintentando en 5s...")
            time.sleep(5)

def ejecutar_nodo(nombre: str, loop_fn):
    # Bucle principal con reconexión automática.
    while True:
        conn = conectar_servidor(nombre)
        try:
            loop_fn(conn)
        except (ConnectionError, OSError) as e:
            print(f"[{nombre}] Conexión perdida: {e}. Reconectando en 3s...")
            time.sleep(3)
        finally:
            conn.close()