# Proyecto---Redes-de-Computadores
Proyecto Final Redes de Computadores, Central hidroeléctrica.

# 1. Levantar DB y Grafana
# En carpeta raíz
docker compose up -d

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Arrancar servidor (terminal 1)
python servidor/servidor.py

# 4. Arrancar un nodo de prueba (terminal 2)
cd nodos
python nodo_represa.py

