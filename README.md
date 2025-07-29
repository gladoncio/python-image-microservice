# 🌀 Microservicio de Procesamiento de GIF con Avatar Circular

Este microservicio permite superponer un avatar circular centrado sobre cada frame de un GIF animado. Está construido con **Python, Flask, Pillow**, y usa **Docker** para ejecutarse fácilmente.

---

## 🚀 Uso

### 📦 Iniciar con Docker

```bash
docker-compose up --build
```

## 🌐 Endpoint disponible

GET /gif-avatar
Procesa un GIF con un avatar circular centrado sobre cada frame.

Parámetros:

gif_url: URL de un GIF animado

avatar_url: URL de una imagen PNG o JPG (preferentemente cuadrada)


```bash
curl "http://localhost:5000/gif-avatar?gif_url=https://wallpapercast.com/media/81c33cf4-9d80-4cf0-abf1-110ef032c713/fba53ad9-b1ec-4c89-aa1e-40873a861268.gif&avatar_url=https://cdn.discordapp.com/avatars/687173922512437301/529ab0624bd6b8284a1a9ac4a901175b.png?size=1024"

```