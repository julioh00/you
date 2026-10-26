/* ============================================================
   LÓGICA DE LA TIENDA — no hace falta tocar este archivo.
   Lee los productos de js/productos.js y los pinta en el HTML.
   ============================================================ */

const state = {
  filtro: "todos",
  carrito: JSON.parse(localStorage.getItem("regular-carrito")) || []
};

const grid = document.getElementById("productosGrid");
const filtrosEl = document.getElementById("filtros");
const carritoPanel = document.getElementById("carritoPanel");
const overlay = document.getElementById("overlay");
const carritoItemsEl = document.getElementById("carritoItems");
const carritoCountEl = document.getElementById("carritoCount");
const carritoTotalEl = document.getElementById("carritoTotal");
const toast = document.getElementById("toast");

const formatearPrecio = (n) => n.toFixed(2).replace(".", ",") + " €";

function productosFiltrados() {
  if (state.filtro === "todos") return PRODUCTOS;
  return PRODUCTOS.filter((p) => p.categoria === state.filtro);
}

function renderFiltros() {
  filtrosEl.innerHTML = "";
  CATEGORIAS.forEach((cat) => {
    const btn = document.createElement("button");
    btn.textContent = cat === "todos" ? "Todos" : cat.charAt(0).toUpperCase() + cat.slice(1);
    btn.className = state.filtro === cat ? "activo" : "";
    btn.addEventListener("click", () => {
      state.filtro = cat;
      renderFiltros();
      renderProductos();
    });
    filtrosEl.appendChild(btn);
  });
}

function renderProductos() {
  grid.innerHTML = "";
  productosFiltrados().forEach((p) => {
    const card = document.createElement("article");
    card.className = "producto";
    card.innerHTML = `
      <div class="foto">
        <img src="${p.imagen}" alt="${p.nombre}" loading="lazy">
        ${p.etiqueta ? `<span class="etiqueta">${p.etiqueta}</span>` : ""}
      </div>
      <div class="info">
        <div class="categoria">${p.categoria}</div>
        <h3>${p.nombre}</h3>
        <div class="precio">${formatearPrecio(p.precio)}</div>
        <div class="tallas">Tallas: ${p.tallas.join(" · ")}</div>
        <button data-id="${p.id}">${TEXTOS.botonProducto}</button>
      </div>
    `;
    card.querySelector("button").addEventListener("click", () => anadirAlCarrito(p));
    grid.appendChild(card);
  });
}

/* ---------- Carrito ---------- */

function guardarCarrito() {
  localStorage.setItem("regular-carrito", JSON.stringify(state.carrito));
}

function anadirAlCarrito(producto) {
  const existente = state.carrito.find((i) => i.id === producto.id);
  if (existente) {
    existente.cantidad += 1;
  } else {
    state.carrito.push({ ...producto, cantidad: 1 });
  }
  guardarCarrito();
  actualizarCarrito();
  mostrarToast(`${producto.nombre} ${TEXTOS.anadido}`);
}

function eliminarDelCarrito(id) {
  state.carrito = state.carrito.filter((i) => i.id !== id);
  guardarCarrito();
  actualizarCarrito();
}

function actualizarCarrito() {
  const unidades = state.carrito.reduce((acc, i) => acc + i.cantidad, 0);
  const total = state.carrito.reduce((acc, i) => acc + i.precio * i.cantidad, 0);

  carritoCountEl.textContent = unidades;
  carritoTotalEl.textContent = formatearPrecio(total);

  if (state.carrito.length === 0) {
    carritoItemsEl.innerHTML = `<p class="carrito-vacio">${TEXTOS.carritoVacio}</p>`;
    return;
  }

  carritoItemsEl.innerHTML = "";
  state.carrito.forEach((item) => {
    const div = document.createElement("div");
    div.className = "item-carrito";
    div.innerHTML = `
      <img src="${item.imagen}" alt="${item.nombre}">
      <div class="datos">
        <h4>${item.nombre}</h4>
        <div class="precio">${formatearPrecio(item.precio)} × ${item.cantidad}</div>
      </div>
      <button class="eliminar" aria-label="Eliminar">×</button>
    `;
    div.querySelector(".eliminar").addEventListener("click", () => eliminarDelCarrito(item.id));
    carritoItemsEl.appendChild(div);
  });
}

function abrirCarrito() {
  carritoPanel.classList.add("abierto");
  overlay.classList.add("visible");
}

function cerrarCarrito() {
  carritoPanel.classList.remove("abierto");
  overlay.classList.remove("visible");
}

/* ---------- Toast ---------- */

let toastTimer;
function mostrarToast(mensaje) {
  toast.textContent = mensaje;
  toast.classList.add("visible");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("visible"), 2200);
}

/* ---------- Ticker duplicado para bucle continuo ---------- */

const ticker = document.getElementById("tickerTrack");
ticker.innerHTML += ticker.innerHTML;

/* ---------- Eventos ---------- */

document.getElementById("abrirCarrito").addEventListener("click", abrirCarrito);
document.getElementById("cerrarCarrito").addEventListener("click", cerrarCarrito);
overlay.addEventListener("click", cerrarCarrito);
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") cerrarCarrito();
});

document.getElementById("checkout").addEventListener("click", () => {
  if (state.carrito.length === 0) {
    mostrarToast(TEXTOS.carritoVacio);
    return;
  }
  mostrarToast(TEXTOS.checkout);
});

/* ---------- Arranque ---------- */

renderFiltros();
renderProductos();
actualizarCarrito();
