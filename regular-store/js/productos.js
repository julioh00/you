/* ============================================================
   CATÁLOGO DE PRODUCTOS — edita este archivo para añadir,
   quitar o modificar productos.

   Cada producto tiene:
     id        -> número único
     nombre    -> nombre que se muestra
     categoria -> "camisetas" | "sudaderas" | "pantalones" | "accesorios"
     precio    -> precio en euros (número)
     tallas    -> tallas disponibles
     etiqueta  -> (opcional) texto de la pegatina sobre la foto ("Nuevo", "-20%"...)
     imagen    -> ruta de la foto. Coloca tus imágenes en assets/img/
                   y cambia aquí el nombre del archivo.
   ============================================================ */

const PRODUCTOS = [
  {
    id: 1,
    nombre: "Camiseta Regular Negra",
    categoria: "camisetas",
    precio: 24.99,
    tallas: ["S", "M", "L", "XL"],
    etiqueta: "Nuevo",
    imagen: "assets/img/producto-1.svg" // <-- sustituye por tu foto
  },
  {
    id: 2,
    nombre: "Camiseta Regular Rosa",
    categoria: "camisetas",
    precio: 24.99,
    tallas: ["S", "M", "L", "XL"],
    etiqueta: "",
    imagen: "assets/img/producto-2.svg"
  },
  {
    id: 3,
    nombre: "Sudadera Logo Triángulo",
    categoria: "sudaderas",
    precio: 54.99,
    tallas: ["M", "L", "XL", "XXL"],
    etiqueta: "Nuevo",
    imagen: "assets/img/producto-3.svg"
  },
  {
    id: 4,
    nombre: "Sudadera Negra Essential",
    categoria: "sudaderas",
    precio: 49.99,
    tallas: ["S", "M", "L", "XL"],
    etiqueta: "",
    imagen: "assets/img/producto-4.svg"
  },
  {
    id: 5,
    nombre: "Pantalón Cargo Negro",
    categoria: "pantalones",
    precio: 59.99,
    tallas: ["S", "M", "L", "XL"],
    etiqueta: "",
    imagen: "assets/img/producto-5.svg"
  },
  {
    id: 6,
    nombre: "Pantalón Recto Rosa",
    categoria: "pantalones",
    precio: 54.99,
    tallas: ["S", "M", "L"],
    etiqueta: "-20%",
    imagen: "assets/img/producto-6.svg"
  },
  {
    id: 7,
    nombre: "Gorra Regular Negra",
    categoria: "accesorios",
    precio: 19.99,
    tallas: ["Única"],
    etiqueta: "",
    imagen: "assets/img/producto-7.svg"
  },
  {
    id: 8,
    nombre: "Gorra Regular Rosa",
    categoria: "accesorios",
    precio: 19.99,
    tallas: ["Única"],
    etiqueta: "Nuevo",
    imagen: "assets/img/producto-8.svg"
  }
];

/* ============================================================
   TEXTOS DE LA TIENDA — cámbialos aquí o directamente en el HTML
   ============================================================ */

const TEXTOS = {
  // Mensaje que aparece al añadir un producto al carrito
  anadido: "añadido al carrito",
  // Mensaje al finalizar la compra (cámbialo por el enlace a tu pago)
  checkout: "Demo: aquí conectarías tu pasarela de pago (Stripe, PayPal, Bizum...)",
  // Mensaje cuando el carrito está vacío
  carritoVacio: "Tu carrito está vacío.",
  // Botón de cada producto
  botonProducto: "Añadir al carrito"
};

/* Categorías que aparecen en los filtros (se generan solas) */
const CATEGORIAS = ["todos", "camisetas", "sudaderas", "pantalones", "accesorios"];
