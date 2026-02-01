import streamlit as st
import qrcode
from PIL import Image, ImageDraw, ImagePath
import os
from io import BytesIO
import math
import numpy as np

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Peplo Heart QR Stylish", page_icon="❤️", layout="centered")
st.title("❤️ Peplo Heart QR - Forma Perfetta")
st.write("QR Code funzionante all'interno di un cuore dalla forma stilizzata ed elegante.")

link_input = st.text_input("Inserisci Link:", "https://peplo.shop")

# --- FUNZIONI DI GEOMETRIA E DISEGNO ---

def draw_heart_module(draw, x, y, size, color="black"):
    """
    Disegna un singolo 'pixel' del QR a forma di cuore (il modulo piccolo).
    """
    m = size * 0.15 # Margine
    # Cerchio sinistro
    draw.ellipse([x + m, y + m, x + size/2 + m/2, y + size/2 + m], fill=color)
    # Cerchio destro
    draw.ellipse([x + size/2 - m/2, y + m, x + size - m, y + size/2 + m], fill=color)
    # Triangolo inferiore
    draw.polygon([
        (x + m*1.2, y + size/2),
        (x + size/2, y + size - m*0.5),
        (x + size - m*1.2, y + size/2)
    ], fill=color)

def get_heart_polygon_points(cx, cy, scale):
    """
    Genera i punti per un poligono a forma di cuore stilizzato (formula parametrica elegante).
    """
    points = []
    # Usiamo 200 punti per una curva morbida
    for t in np.linspace(0, 2 * np.pi, 200):
        # Formula parametrica per un cuore stilizzato
        x_raw = 16 * np.sin(t)**3
        y_raw = 13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)
        
        # Scaliamo e trasliamo al centro della tela
        # Invertiamo la Y perché la Y cresce verso il basso nelle immagini
        x = cx + x_raw * scale
        y = cy - y_raw * scale 
        points.append((x, y))
    return points

def create_heart_mask(width, height):
    """
    Crea una maschera binaria (immagine in scala di grigi) della forma del cuore gigante.
    Bianco = dentro il cuore, Nero = fuori.
    """
    mask = Image.new("L", (width, height), "black") # Sfondo nero
    draw_mask = ImageDraw.Draw(mask)
    
    cx, cy = width // 2, height // 2
    # Scala empirica per riempire bene la tela
    scale = min(width, height) / 35 
    
    # Otteniamo i punti del poligono del cuore
    heart_points = get_heart_polygon_points(cx, cy + height*0.05, scale) # Leggero offset Y per centrare
    
    # Disegniamo il poligono bianco pieno sulla maschera
    draw_mask.polygon(heart_points, fill="white")
    
    return mask

# --- MOTORE DI GENERAZIONE ---

def crea_qr_peplo_stylish(testo):
    # 1. SETUP QR
    box_size = 30
    qr = qrcode.QRCode(
        version=6,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=0
    )
    qr.add_data(testo)
    qr.make(fit=True)
    
    matrix = qr.get_matrix()
    qr_cells = len(matrix)
    qr_pixel_dim = qr_cells * box_size

    # 2. CALCOLO DIMENSIONI TELA E POSIZIONE
    # Rapporto per far toccare gli angoli bassi del QR al bordo del cuore
    canvas_w = int(qr_pixel_dim * 1.4)
    canvas_h = int(qr_pixel_dim * 1.3)
    
    final_img = Image.new("RGB", (canvas_w, canvas_h), "white")
    draw = ImageDraw.Draw(final_img)
    
    # --- CREAZIONE DELLA MASCHERA DEL CUORE GIGANTE ---
    # Questa è la chiave per la nuova forma perfetta
    heart_mask = create_heart_mask(canvas_w, canvas_h)
    
    cx = canvas_w // 2
    cy = canvas_h // 2

    # --- SPOSTAMENTO verticale del QR ---
    shift_up_pixels = 3 * box_size
    
    qr_start_x = cx - (qr_pixel_dim // 2)
    qr_start_y = cy - (qr_pixel_dim // 2) - shift_up_pixels

    # 3. DISEGNO SFONDO (Usando la nuova maschera)
    for y in range(0, canvas_h, box_size):
        for x in range(0, canvas_w, box_size):
            # Controlliamo il centro del modulo sulla maschera
            # Se il pixel corrispondente sulla maschera è bianco (>0), siamo dentro il cuore
            # Usiamo un try/except per i bordi estremi della tela
            try:
                if heart_mask.getpixel((x + box_size//2, y + box_size//2)) > 0:
                    draw_heart_module(draw, x, y, box_size, color="black")
            except IndexError:
                continue

    # 4. SOVRAPPOSIZIONE QR CODE (Identico a prima)
    center_gap = qr_cells // 6
    mid = qr_cells // 2
    
    for r in range(qr_cells):
        for c in range(qr_cells):
            px = qr_start_x + c * box_size
            py = qr_start_y + r * box_size
            
            # Area Logo (Buco)
            if (mid - center_gap) < r < (mid + center_gap) and \
               (mid - center_gap) < c < (mid + center_gap):
                draw.rectangle([px, py, px+box_size, py+box_size], fill="white")
                continue

            cell = matrix[r][c]
            # Finder Patterns (Angoli solidi)
            is_finder = (r < 7 and c < 7) or \
                        (r < 7 and c >= qr_cells-7) or \
                        (r >= qr_cells-7 and c < 7)
            
            if is_finder:
                color = "black" if cell else "white"
                draw.rectangle([px, py, px+box_size, py+box_size], fill=color)
            elif cell:
                # Modulo dati NERO -> Disegna cuoricino
                draw_heart_module(draw, px, py, box_size, color="black")
            else:
                # Modulo dati BIANCO -> CANCELLA lo sfondo con un quadrato bianco
                draw.rectangle([px, py, px+box_size, py+box_size], fill="white")

    # 5. LOGO PEPLO
    if os.path.exists("logo_peplo.jpg"):
        try:
            logo = Image.open("logo_peplo.jpg").convert("RGBA")
            hole_pixel_size = (center_gap * 2) * box_size
            target_size = int(hole_pixel_size * 0.9)
            logo.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
            
            l_x = qr_start_x + (qr_pixel_dim // 2) - (logo.size[0] // 2)
            l_y = qr_start_y + (qr_pixel_dim // 2) - (logo.size[1] // 2)
            final_img.paste(logo, (l_x, l_y), logo)
        except:
            pass

    return final_img

# --- UI ---
if st.button("Genera QR Cuore Perfetto"):
    with st.spinner('Scolpendo il cuore...'):
        img = crea_qr_peplo_stylish(link_input)
        st.image(img, caption="Forma stilizzata e QR funzionante", width=500)
        
        buf = BytesIO()
        img.save(buf, format="PNG")
        st.download_button("Scarica PNG", buf.getvalue(), "peplo_heart_stylish.png", "image/png")
