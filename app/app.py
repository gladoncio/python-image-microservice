from flask import Flask, request, send_file, jsonify, send_from_directory
from PIL import Image, ImageDraw, ImageFont
import requests
import io
import os
import uuid

app = Flask(__name__)
FRAMES_DIR = 'frames'
GENERATED_DIR = 'generated'
os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

def download_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return io.BytesIO(response.content)
    except Exception as e:
        raise Exception(f"Error descargando {url}: {str(e)}")

def circular_crop_with_border(image: Image.Image, size: int, border_width: int, border_color=(255, 255, 255)) -> Image.Image:
    image = image.resize((size - 2 * border_width, size - 2 * border_width)).convert("RGBA")
    
    # Círculo recortado
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, image.size[0], image.size[1]), fill=255)

    avatar_cropped = Image.new('RGBA', image.size)
    avatar_cropped.paste(image, (0, 0), mask)

    # Imagen con borde
    final_size = (size, size)
    final_img = Image.new('RGBA', final_size, (0, 0, 0, 0))
    border_draw = ImageDraw.Draw(final_img)
    border_draw.ellipse((0, 0, size, size), fill=border_color)
    final_img.paste(avatar_cropped, (border_width, border_width), avatar_cropped)

    return final_img

@app.route('/gif-avatar', methods=['GET'])
def gif_with_avatar():
    gif_url = request.args.get('gif_url')
    avatar_url = request.args.get('avatar_url')

    if not gif_url or not avatar_url:
        return jsonify({'error': 'Faltan parámetros: gif_url y avatar_url son requeridos'}), 400

    try:
        gif_io = download_image(gif_url)
        gif = Image.open(gif_io)

        avatar_io = download_image(avatar_url)
        avatar = Image.open(avatar_io).convert("RGBA")

        frames = []
        frame_number = 0

        # Limpiar frames anteriores
        for f in os.listdir(FRAMES_DIR):
            os.remove(os.path.join(FRAMES_DIR, f))

        gif_width, gif_height = gif.size
        avatar_size = min(gif_width, gif_height) // 3
        border_width = avatar_size // 12

        # Preparar avatar con borde circular
        avatar_with_border = circular_crop_with_border(avatar, avatar_size, border_width)

        # Coordenadas centradas
        pos_x = (gif_width - avatar_size) // 2
        pos_y = (gif_height - avatar_size) // 2
        position = (pos_x, pos_y)

        while True:
            frame = gif.copy().convert("RGBA")
            frame.paste(avatar_with_border, position, mask=avatar_with_border)

            frame_path = os.path.join(FRAMES_DIR, f"frame_{frame_number}.png")
            frame.save(frame_path)

            frames.append(frame)
            frame_number += 1

            try:
                gif.seek(gif.tell() + 1)
            except EOFError:
                break

        # Crear nuevo GIF en memoria
        output = io.BytesIO()
        frames[0].save(output, format='GIF', save_all=True, append_images=frames[1:], loop=0, duration=gif.info.get("duration", 100))
        output_size = output.tell()
        output.seek(0)

        if output_size > 10 * 1024 * 1024:  # 10 MB
            return jsonify({'error': 'El GIF generado supera el tamaño máximo de 10 MB'}), 413

        # Guardar archivo físico para servirlo por URL
        gif_id = str(uuid.uuid4()) + ".gif"
        filepath = os.path.join(GENERATED_DIR, gif_id)
        with open(filepath, "wb") as f:
            f.write(output.read())

        # Devolver URL pública
        gif_url = f"http://localhost:5000/generated/{gif_id}"
        return jsonify({'url': gif_url}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generated/<filename>')
def serve_generated_file(filename):
    return send_from_directory(GENERATED_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
