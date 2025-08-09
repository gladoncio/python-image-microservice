from flask import Flask, request, jsonify, send_from_directory, render_template, url_for
from PIL import Image, ImageDraw, ImageFont
import requests
import io
import os
import uuid
import shutil

app = Flask(__name__, template_folder="templates")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRAMES_ROOT_DIR = os.path.join(BASE_DIR, 'frames')
GENERATED_DIR = os.path.join(BASE_DIR, 'generated')
FONTS_DIR = os.path.join(BASE_DIR, 'fonts')

os.makedirs(FRAMES_ROOT_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

MAX_TEXT_RATIO = 0.9
DEFAULT_TEXT_SIZE = 40

# Ruta para servir archivos de fuentes
@app.route('/fonts/<path:filename>')
def fonts(filename):
    return send_from_directory(FONTS_DIR, filename)

# Ruta para la página principal que muestra el formulario
@app.route('/')
def index():
    # Listar las fuentes ttf disponibles
    fonts_list = [f for f in os.listdir(FONTS_DIR) if f.lower().endswith('.ttf')]
    return render_template("index.html", fonts=fonts_list)

def download_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return io.BytesIO(response.content)
    except Exception as e:
        raise Exception(f"Error descargando {url}: {str(e)}")

def circular_crop_with_border(image: Image.Image, size: int, border_width: int, border_color=(255, 255, 255)) -> Image.Image:
    image = image.resize((size - 2 * border_width, size - 2 * border_width)).convert("RGBA")
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, image.size[0], image.size[1]), fill=255)
    avatar_cropped = Image.new('RGBA', image.size)
    avatar_cropped.paste(image, (0, 0), mask)
    final_size = (size, size)
    final_img = Image.new('RGBA', final_size, (0, 0, 0, 0))
    border_draw = ImageDraw.Draw(final_img)
    border_draw.ellipse((0, 0, size, size), fill=border_color)
    final_img.paste(avatar_cropped, (border_width, border_width), avatar_cropped)
    return final_img

def parse_color(color_str):
    try:
        parts = [int(p) for p in color_str.split(',')]
        if len(parts) == 3:
            return tuple(parts)
    except:
        pass
    return (255, 255, 255)

@app.route('/gif-avatar', methods=['GET'])
def gif_with_avatar():
    gif_url = request.args.get('gif_url')
    avatar_url = request.args.get('avatar_url')
    text = request.args.get('text', '')
    color_str = request.args.get('color', '255,255,255')
    text_color = parse_color(color_str)

    try:
        text_size = int(request.args.get('text_size', DEFAULT_TEXT_SIZE))
        if text_size < 10:
            text_size = DEFAULT_TEXT_SIZE
    except:
        text_size = DEFAULT_TEXT_SIZE

    # Obtener fuente de la query, si no existe usar DejaVuSans.ttf
    font_name = request.args.get('font', 'DejaVuSans.ttf')
    font_path_candidate = os.path.join(FONTS_DIR, font_name)
    if not os.path.isfile(font_path_candidate):
        font_path_candidate = os.path.join(FONTS_DIR, 'DejaVuSans.ttf')
    FONT_PATH = font_path_candidate

    if not gif_url or not avatar_url:
        return jsonify({'error': 'Faltan parámetros: gif_url y avatar_url son requeridos'}), 400

    try:
        gif_io = download_image(gif_url)
        gif = Image.open(gif_io)
        avatar_io = download_image(avatar_url)
        avatar = Image.open(avatar_io).convert("RGBA")
        request_id = str(uuid.uuid4())
        frames_dir = os.path.join(FRAMES_ROOT_DIR, request_id)
        os.makedirs(frames_dir, exist_ok=True)
        gif_width, gif_height = gif.size
        avatar_size = min(gif_width, gif_height) // 3
        border_width = avatar_size // 12
        avatar_with_border = circular_crop_with_border(avatar, avatar_size, border_width)
        margin_text_vertical = avatar_size // 10
        pos_x = (gif_width - avatar_size) // 2
        pos_y = (gif_height - avatar_size - margin_text_vertical - text_size) // 2
        position = (pos_x, pos_y)
        frames = []
        frame_number = 0

        while True:
            frame = gif.copy().convert("RGBA")
            frame.paste(avatar_with_border, position, mask=avatar_with_border)
            draw = ImageDraw.Draw(frame)
            if text:
                try:
                    font = ImageFont.truetype(FONT_PATH, size=text_size)
                except IOError:
                    font = ImageFont.load_default()
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                text_x = (gif_width - text_width) // 2
                text_y = pos_y + avatar_size + margin_text_vertical
                shadow_color = (0, 0, 0, 150)
                for offset in [(1,1), (-1,1), (1,-1), (-1,-1)]:
                    draw.text((text_x + offset[0], text_y + offset[1]), text, font=font, fill=shadow_color)
                draw.text((text_x, text_y), text, font=font, fill=text_color + (255,))
            frame_path = os.path.join(frames_dir, f"frame_{frame_number}.png")
            frame.save(frame_path)
            frames.append(frame)
            frame_number += 1
            try:
                gif.seek(gif.tell() + 1)
            except EOFError:
                break

        output = io.BytesIO()
        frames[0].save(output, format='GIF', save_all=True, append_images=frames[1:], loop=0, duration=gif.info.get("duration", 100))
        output_size = output.tell()
        output.seek(0)
        if output_size > 10 * 1024 * 1024:
            shutil.rmtree(frames_dir, ignore_errors=True)
            return jsonify({'error': 'El GIF generado supera el tamaño máximo de 10 MB'}), 413
        gif_id = f"{request_id}.gif"
        filepath = os.path.join(GENERATED_DIR, gif_id)
        with open(filepath, "wb") as f:
            f.write(output.read())
        shutil.rmtree(frames_dir, ignore_errors=True)
        gif_url_resp = f"/generated/{gif_id}"
        return jsonify({'url': gif_url_resp}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/generated/<filename>')
def serve_generated_file(filename):
    return send_from_directory(GENERATED_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
