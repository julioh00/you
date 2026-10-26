# REGULAR — Tienda de ropa (HTML puro)

Tienda online estática, sin dependencias ni frameworks. Solo HTML, CSS y JavaScript.

## Cómo usarla

Abre el archivo `index.html` directamente en el navegador, o sirvela localmente:

```bash
cd regular-store
python3 -m http.server 8000
# abre http://localhost:8000
```

## Cómo editar el texto

Todo el texto editable está marcado en `index.html` con comentarios
`<!-- ===== EDITABLE: ... ===== -->`. Busca esos comentarios y cambia lo que quieras:
titulares, descripciones, email, teléfono, redes, horario, textos del pie...

## Cómo cambiar el logo

Sustituye el archivo `assets/img/logo.jpeg` por el tuyo (mismo nombre o actualiza
la ruta en `index.html`, en la etiqueta `<img src="assets/img/logo.jpeg">`).

## Cómo añadir productos e imágenes

1. Guarda las fotos de tus productos en `assets/img/` (jpg, png, webp...).
2. Edita `js/productos.js` y modifica la lista `PRODUCTOS`, o añade productos
   copiando uno de los ejemplos:

```js
{
  id: 9,                          // número único
  nombre: "Pantalón Vaquero",
  categoria: "pantalones",        // camisetas | sudaderas | pantalones | accesorios
  precio: 64.99,
  tallas: ["S", "M", "L", "XL"],
  etiqueta: "Nuevo",              // opcional: pegatina sobre la foto
  imagen: "assets/img/vaquero.jpg" // tu foto
}
```

3. Las imágenes de ejemplo (`producto-1.svg` ... `producto-8.svg`) son marcadores
   con un triángulo. Bórralas cuando tengas fotos reales.

## Cómo cambiar los colores

En `css/styles.css`, al principio, las variables:

```css
--negro: #0d0d0d;
--rosa: #ff3ea5;
```

## Funcionalidades incluidas

- Catálogo con filtros por categoría
- Carrito de la compra lateral (se guarda en el navegador con localStorage)
- Total automático y contador en el header
- Diseño responsive (móvil y escritorio)
- Ticker de anuncios en la parte superior

## Conectar los pagos

El botón "Finalizar compra" muestra un aviso de demostración. Para cobrar de
verdad, enlázalo con tu pasarela (Stripe, PayPal, Redsys...) o cámbialo por un
enlace a WhatsApp/Instagram para pedidos manuales. El texto está en
`js/productos.js`, en el objeto `TEXTOS`.
