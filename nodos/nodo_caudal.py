import time
import random
from utils_nodo import enviar_medicion, ejecutar_nodo
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import INTERVALO_ENVIO

NODO = "caudal"
CAUDAL = 70.0   # m³/s
LIMITES = (0.0, 160.0)

# Porcentaje de apertura de la compuerta: 0=cerrada, 100=abierta
apertura_compuerta = 60.0

def loop(conn):
    global apertura_compuerta
    caudal = CAUDAL

    while True:
        # El caudal depende de la apertura de la compuerta + variación aleatoria
        objetivo = apertura_compuerta * 1.8  # escala aproximada
        caudal += (objetivo - caudal) * 0.05 + random.gauss(0, 1.5)
        caudal = max(LIMITES[0], min(LIMITES[1], caudal))

        respuesta = enviar_medicion(conn, NODO, "caudal", caudal)
        print(f"[{NODO}] caudal={caudal:.2f} m³/s → {respuesta}")

        if respuesta.get("status") == "comando":
            comando = respuesta.get("comando")
            parametro = respuesta.get("parametro", apertura_compuerta)
            if comando == "cerrar_compuerta":
                apertura_compuerta = max(0.0, apertura_compuerta - parametro * 0.5)
                print(f"[{NODO}] Compuerta cerrada al {apertura_compuerta:.1f}%")
            elif comando == "abrir_compuerta":
                apertura_compuerta = min(100.0, apertura_compuerta + parametro * 0.5)
                print(f"[{NODO}] Compuerta abierta al {apertura_compuerta:.1f}%")
            # Para regular temperatura de la turbina
            elif comando == "reducir_caudal":
                apertura_compuerta = max(0.0, apertura_compuerta - parametro * 0.3)
                print(f"[{NODO}] Caudal reducido - compuerta al {apertura_compuerta:.1f}%")

        time.sleep(INTERVALO_ENVIO)

if __name__ == "__main__":
    ejecutar_nodo(NODO, loop)