import socket
import json
import hmac
import hashlib
from datetime import datetime, timezone
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SERVER_HOST, SERVER_PORT, HMAC_KEY

def firmar_mensaje(mensaje: dict) -> str:
    copy = {k: v for k, v in mensaje.items() if k != "hmac"}
    contenido = json.dumps(copy, sort_keys=True).encode()
    return hmac.new(HMAC_KEY, contenido, hashlib.sha256).hexdigest()

# Mensaje original legítimo
msg = {
    "nodo":      "turbina",
    "variable":  "rpm",
    "valor":     435.70,
    "timestamp": datetime.now(timezone.utc).isoformat(),
}

# Se firma el mensaje con el valor original
msg["hmac"] = firmar_mensaje(msg)

# Se altera el valor despues de firmarlo (simula una manipulación en el tránsito)
msg["valor"] = 9999.99


conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.connect((SERVER_HOST, SERVER_PORT))
conn.sendall((json.dumps(msg) + "\n").encode())

respuesta = ""
while "\n" not in respuesta:
    respuesta += conn.recv(1024).decode()

print(f"Respuesta del servidor: {respuesta.strip()}")
conn.close()