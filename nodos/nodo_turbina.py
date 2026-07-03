import time
import random
from utils_nodo import enviar_medicion, ejecutar_nodo
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import INTERVALO_ENVIO

NODO = "turbina"
RPM = 420.0   # RPM promedio de una turbina
TEMP = 35.0   # °C

LIMITES_RPM = (0.0, 700.0)
LIMITES_TEMP = (5.0, 100.0)

def loop(conn):
    rpm = RPM
    temp = TEMP

    while True:
        # RPM: Tiende a volver al valor inicial (420.0 RPM)
        rpm += (RPM - rpm) * 0.02 + random.gauss(0, 8.0)
        rpm = max(LIMITES_RPM[0], min(LIMITES_RPM[1],  rpm))

        # Temperatura: sube con RPM alta, baja lentamente si RPM es baja
        carga_termica = (rpm / RPM - 1.0) * 5.0
        temp += carga_termica * 0.1 + random.gauss(0, 0.4)
        temp = max(LIMITES_TEMP[0], min(LIMITES_TEMP[1], temp))

        # Enviar RPM
        resp_rpm = enviar_medicion(conn, NODO, "rpm", rpm)
        print(f"[{NODO}] rpm={rpm:.1f} → {resp_rpm}")

        # Enviar temperatura
        resp_temp = enviar_medicion(conn, NODO, "temperatura", temp)
        print(f"[{NODO}] temperatura={temp:.2f} °C → {resp_temp}")

        # Reaccionar a comandos
        for resp in (resp_rpm, resp_temp):
            if resp.get("status") == "comando":
                comando = resp.get("comando")
                if comando == "reducir_caudal":
                    rpm  -= 30.0
                    print(f"[{NODO}] Reduciendo RPM por carga térmica")

        time.sleep(INTERVALO_ENVIO)

if __name__ == "__main__":
    ejecutar_nodo(NODO, loop)