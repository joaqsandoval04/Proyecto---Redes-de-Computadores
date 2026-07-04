# Configuración general del sistema
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 65432

# Clave HMAC compartida (en producción iría en variable de entorno)
HMAC_KEY = b"clave_secreta_hidro_2026"

# Umbrales operacionales
UMBRALES = {
    "nivel":       {"min": 10.0,    "max": 95.0,    "unidad": "m"},
    "caudal":      {"min": 0.0,    "max": 160.0,   "unidad": "m3/s"},
    "rpm":         {"min": 0.0,   "max": 700.0,   "unidad": "RPM"},
    "temperatura": {"min": 5.0,    "max": 100.0,    "unidad": "C"},
    "voltaje":     {"min": 8000.0, "max": 16000.0, "unidad": "V"},
}

# Nodos reconocidos
NODOS_VALIDOS = {"represa", "caudal", "turbina", "generador"}

# Intervalo de envío de cada nodo (segundos)
INTERVALO_ENVIO = 2