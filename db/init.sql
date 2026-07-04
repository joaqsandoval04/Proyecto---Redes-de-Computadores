-- Tabla principal de mediciones
CREATE TABLE mediciones (
    id          SERIAL PRIMARY KEY,
    timestamp   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    nodo        VARCHAR(20) NOT NULL,  -- 'represa', 'caudal', 'turbina', 'generador'
    variable    VARCHAR(30) NOT NULL,  -- 'nivel', 'caudal', 'rpm', 'temperatura', 'voltaje'
    valor       DOUBLE PRECISION NOT NULL,
    unidad      VARCHAR(10) NOT NULL
);

-- Eventos y alertas
CREATE TABLE eventos (
    id          SERIAL PRIMARY KEY,
    timestamp   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    nodo        VARCHAR(20) NOT NULL,
    tipo        VARCHAR(20) NOT NULL,  -- 'alerta', 'anomalia', 'info'
    descripcion TEXT NOT NULL,
    resuelto    BOOLEAN DEFAULT FALSE
);

-- Comandos enviados por el servidor hacia los nodos
CREATE TABLE comandos (
    id              SERIAL PRIMARY KEY,
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    nodo_destino    VARCHAR(20) NOT NULL,
    comando         VARCHAR(50) NOT NULL,  -- 'abrir_compuerta', 'cerrar_compuerta', etc.
    parametro       DOUBLE PRECISION,      -- ej: porcentaje de apertura
    ejecutado       BOOLEAN DEFAULT FALSE
);

-- Índices para queries de Grafana
CREATE INDEX idx_mediciones_timestamp ON mediciones(timestamp);
CREATE INDEX idx_mediciones_nodo ON mediciones(nodo);
CREATE INDEX idx_eventos_timestamp ON eventos(timestamp);