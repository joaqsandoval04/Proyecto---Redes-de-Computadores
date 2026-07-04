import time
import random
from utils_nodo import enviar_medicion, ejecutar_nodo
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import INTERVALO_ENVIO

NODO = "generador"
VOLTAJE = 13800.0  # V
LIMITES = (8000.0, 16000.0)

def loop(conn):
    voltaje = VOLTAJE

    while True:
        # El voltaje varía con la velocidad del generador (relacionado a RPM de turbina)
        delta = random.gauss(0,80.0)

        # Voltaje con pequeña variación aleatoria
        voltaje += delta + (VOLTAJE - voltaje) * 0.03
        voltaje = max(LIMITES[0], min(LIMITES[1], voltaje))

        respuesta = enviar_medicion(conn, NODO, "voltaje", voltaje)
        print(f"[{NODO}] voltaje={voltaje:.1f} V → {respuesta}")

        # El generador no recibe comandos directos en este sistema
        # Las anomalías de voltaje generan alertas para operador humano

        time.sleep(INTERVALO_ENVIO)

if __name__ == "__main__":
    ejecutar_nodo(NODO, loop)