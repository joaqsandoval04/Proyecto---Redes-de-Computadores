const estado = document.querySelector("#estado");
const tarjetas = document.querySelector("#tarjetas");
const alertas = document.querySelector("#alertas");

function valorTexto(valor) {
  if (valor === null || valor === undefined) return "--";
  return Number(valor).toLocaleString("es-CL", { maximumFractionDigits: 2 });
}

function hora(iso) {
  if (!iso) return "sin datos";
  return new Date(iso).toLocaleTimeString("es-CL", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function pintarTarjetas(items) {
  tarjetas.innerHTML = items.map((item) => `
    <article class="tarjeta ${item.estado.replace(" ", "-")}">
      <div class="nombre">${item.nombre}</div>
      <div class="valor">${valorTexto(item.valor)} <span class="unidad">${item.unidad}</span></div>
      <div class="nodo">${item.nodo} - ${hora(item.timestamp)}</div>
      <span class="badge">${item.estado}</span>
    </article>
  `).join("");
}

function pintarAlertas(items) {
  if (!items.length) {
    alertas.innerHTML = "<p>No hay alertas registradas.</p>";
    return;
  }

  alertas.innerHTML = items.map((item) => `
    <div class="alerta-item">
      <strong>${item.nodo}</strong>
      <div>${item.descripcion}</div>
      <div class="fecha">${hora(item.timestamp)}</div>
    </div>
  `).join("");
}

async function actualizar() {
  try {
    const respuesta = await fetch("/api/datos", { cache: "no-store" });
    const datos = await respuesta.json();
    if (!respuesta.ok || !datos.ok) throw new Error(datos.error || "Error de conexion");

    estado.textContent = "DB conectada";
    estado.className = "estado ok";
    pintarTarjetas(datos.tarjetas);
    pintarAlertas(datos.eventos);
  } catch (error) {
    estado.textContent = "Sin DB";
    estado.className = "estado error";
    tarjetas.innerHTML = "";
    alertas.innerHTML = `<p>${error.message}</p>`;
  }
}

actualizar();
setInterval(actualizar, 2000);