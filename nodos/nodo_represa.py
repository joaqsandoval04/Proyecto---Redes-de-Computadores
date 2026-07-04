import time
import random
from utils_nodo import enviar_medicion, ejecutar_nodo
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import INTERVALO_ENVIO

NODO = "represa"
ALTURA = 60.0   # metros
LIMITES = (10.0, 95.0)  # límites físicos de la represa

def loop(conn):
    nivel = ALTURA

    while True:
        # Variación lenta del agua, con una variación de ~0.3m por ciclo.
        delta = random.gauss(0, 0.3)

        # Si el nivel está muy alto, subirá menos que si está muy bajo, y viceversa.
        if nivel > 75.0:
            delta -= 0.2
        elif nivel < 40.0:
            delta += 0.15

        nivel = max(LIMITES[0], min(LIMITES[1], nivel + delta))

        respuesta = enviar_medicion(conn, NODO, "nivel", nivel)
        print(f"[{NODO}] nivel={nivel:.2f} m → {respuesta}")

        # Ejecutar comando del servidor si corresponde
        if respuesta.get("status") == "comando":
            comando = respuesta.get("comando")
            if comando == "cerrar_compuerta":
                print(f"[{NODO}] Ejecutando: cerrar compuerta - reduciendo caudal de entrada")
                delta += 0.5  # simula efecto inmediato
            elif comando == "abrir_compuerta":
                print(f"[{NODO}] Ejecutando: abrir compuerta - aumentando caudal de entrada")
                delta -= 0.5

        time.sleep(INTERVALO_ENVIO)

if __name__ == "__main__":
    ejecutar_nodo(NODO, loop)