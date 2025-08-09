# 🌀 Microservicio de Procesamiento de GIF con Avatar Circular

Este microservicio permite superponer un avatar circular centrado sobre cada frame de un GIF animado. Está construido con **Python, Flask, Pillow**, y usa **Docker** para ejecutarse fácilmente.

---

## 🚀 Uso

### 📦 Iniciar con Docker

```bash
docker-compose up --build
```

### 🌐 Probar con Formulario Web

Puedes probar fácilmente el servicio desde un formulario web accesible en:

```
http://127.0.0.1:5000/
```

---

## 🌐 Endpoint disponible

### GET /gif-avatar

Procesa un GIF con un avatar circular centrado sobre cada frame.

**Parámetros:**

- `gif_url`: URL de un GIF animado  
- `avatar_url`: URL de una imagen PNG o JPG (preferentemente cuadrada)  
- `text`: (opcional) Texto para superponer  
- `color`: (opcional) Color del texto en formato `R,G,B` (ejemplo: `255,255,255`)  
- `text_size`: (opcional) Tamaño del texto (número)  
- `font`: (opcional) Nombre del archivo de la fuente (ejemplo: `LiberationSansNarrow-Bold.ttf`)  

---

### Ejemplo CURL

```bash
curl "http://127.0.0.1:5000/gif-avatar?gif_url=https%3A%2F%2Fmedia1.tenor.com%2Fm%2FpMpEH8nge1MAAAAC%2Fgojo.gif&avatar_url=https%3A%2F%2Fcdn.discordapp.com%2Favatars%2F687173922512437301%2F529ab0624bd6b8284a1a9ac4a901175b.png%3Fsize%3D1024&text=seria+que+este+texto+esta+bonito&color=255%2C255%2C255&text_size=20&font=LiberationSansNarrow-Bold.ttf"
```

---

## 📸 Imagen de ejemplo

![Imagen muestra](/captura/muestra.png)


puedes visualizar una imagen de ejemplo almacenada en la carpeta `captura` con el nombre `muestra`.

---
