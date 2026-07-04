# Configuración general del sistema
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 65432

# Clave HMAC compartida (en producción iría en variable de entorno)
HMAC_KEY = b"clave_secreta_hidro_2026"

# Umbrales operacionales
UMBRALES = {
    "nivel":       {"min": 30.0,    "max": 85.0,    "unidad": "m"},
    "caudal":      {"min": 15.0,    "max": 130.0,   "unidad": "m3/s"},
    "rpm":         {"min": 200.0,   "max": 600.0,   "unidad": "RPM"},
    "temperatura": {"min": 10.0,    "max": 80.0,    "unidad": "C"},
    "voltaje":     {"min": 10000.0, "max": 14000.0, "unidad": "V"},
}

# Nodos reconocidos
NODOS_VALIDOS = {"represa", "caudal", "turbina", "generador"}

# Intervalo de envío de cada nodo (segundos)
INTERVALO_ENVIO = 2