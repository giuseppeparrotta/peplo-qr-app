import streamlit as st
import qrcode
from PIL import Image, ImageDraw
import math
import random
import os
from io import BytesIO

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Peplo Heart QR", page_icon="❤️")
st.title("❤️ Peplo Heart QR Generator")
st.write("Genera un QR che forma un cuore completo, perfettamente scansionabile.")

link_input = st.text_input("Inserisci Link:", "https://peplo.shop")

# --- FUNZIONI DI DISEGNO ---

def draw_heart_shape(draw, cx, cy, size, fill=None, outline=None):
    """
    Disegna un cuore vettoriale centrato in (cx, cy).
    Accetta sia 'fill' (colore riempimento) che 'outline' (colore bordo).
    """
    points = []
    # Usiamo più punti per renderlo morbido
    for t in range(0, 360, 5): 
        rad = math.radians(t)
        # Formula geometrica del cuore
        x = 16 * math.sin(rad)**3
        y = 13 * math.cos(rad) - 5 * math.cos(2*rad) - 2 * math.cos(3*rad) - math.cos(4*rad)
        
        # Adattiamo scala e posizione
        px = cx + x * (size / 35)
        py = cy - y * (size / 35) # Invertiamo Y perché nei computer Y cresce verso il basso
        points.append((px, py))
    
    # Disegno effettivo
    draw.polygon(points, fill=fill, outline=outline)

def crea_qr_cuore_pieno(url):
    # 1. SETUP QR (Versione alta per avere densità)
    qr = qrcode.QRCode(
        version=5,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=1 # Bordo minimo, lo gestiamo noi
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image().convert("RGB")
    
    # Dati per calcoli
    matrix = qr.get_matrix()
    dim_matrix = len(matrix)
    mod_size = 20 # Grandezza singolo modulo (cuoricino)
    
    # 2. CREAZIONE TELA (Più grande del QR per fare la forma a cuore)
    canvas_w = dim_matrix * mod_size * 2 # Molto spazio ai lati
    canvas_h = dim_matrix * mod_size * 1.8 
    final_img = Image.new("RGB", (int(canvas_w), int(canvas_h)), "white")
    draw = ImageDraw.Draw(final_img)
    
    # Centro della tela
    cx, cy = canvas_w // 2, canvas_h // 2
    
    # 3. DEFINIAMO L'AREA DEL CUORE GIGANTE (Contenitore)
    heart_radius = dim_matrix * mod_size * 0.75
    
    # Funzione per capire se un punto è dentro il cuore gigante
    def is_inside_big_heart(px, py):
        # Normalizziamo le coordinate rispetto al centro e al raggio
        x = (px - cx) / (heart_radius / 35)
        y = -(py - cy) / (heart_radius / 35)
        try:
            val = (x**2 + y**2 - 1)**3 - x**2 * y**3
            return val <= 0
        except:
            return False

    # 4. DISEGNO DEL QR QUADRATO (AL CENTRO)
    start_x = cx - (dim_matrix * mod_size) // 2
    start_y = cy - (dim_matrix * mod_size) // 2
    
    for r in range(dim_matrix):
        for c in range(dim_matrix):
            x = start_x + c * mod_size
            y = start_y + r * mod_size
            
            # Gestione LOGO CENTRALE (lasciamo il buco)
            # Calcoliamo il centro del QR
            if (dim_matrix//2 - 4) < r < (dim_matrix//2 + 4) and (dim_matrix//2 - 4) < c < (dim_matrix//2 + 4):
                continue

            if matrix[r][c]:
                # FINDER PATTERNS (I 3 occhioni): Devono essere ben visibili
                if (r < 7 and c < 7) or (r < 7 and c >= dim_matrix-7) or (r >= dim_matrix-7 and c < 7):
                     draw.rectangle([x, y, x+mod_size, y+mod_size], fill="black")
                else:
                    # Moduli dati: Cuoricini
                    draw_heart_shape(draw, x+mod_size//2, y+mod_size//2, mod_size*0.9, fill="black")

    # 5. RIEMPIMENTO DECORATIVO ("Filler")
    # Disegniamo cuoricini casuali fuori dal QR ma dentro il Cuore Gigante
    # per dare l'illusione della forma completa
    
    step = mod_size # Griglia dei decori
    for y in range(0, int(canvas_h), step):
        for x in range(0, int(canvas_w), step):
            # Se siamo dentro il QR, saltiamo
            if start_x - step < x < start_x + (dim_matrix * mod_size) + step and \
               start_y - step < y < start_y + (dim_matrix * mod_size) + step:
                continue
            
            # Se siamo dentro la forma del cuore grande
            if is_inside_big_heart(x, y):
                # Aggiungiamo un cuoricino decorativo
                # Leggermente più piccolo per differenziarlo dai dati
                draw_heart_shape(draw, x, y, step*0.7, fill="black")

    # 6. INSERIMENTO LOGO
    if os.path.exists("logo_peplo.jpg"):
        logo = Image.open("logo_peplo.jpg").convert("RGBA")
        logo_w = mod_size * 7
        logo.thumbnail((logo_w, logo_w), Image.Resampling.LANCZOS)
        logo_pos = (int(cx - logo.size[0]//2), int(cy - logo.size[1]//2))
        
        # Sfondo bianco dietro logo
        draw.rectangle([logo_pos[0]-10, logo_pos[1]-10, logo_pos[0]+logo.size[0]+10, logo_pos[1]+logo.size[1]+10], fill="white")
        final_img.paste(logo, logo_pos, logo)

    return final_img

# --- INTERFACCIA ---
if st.button("Genera QR Cuore"):
    with st.spinner('Creazione arte...'):
        img = crea_qr_cuore_pieno(link_input)
        st.image(img, caption="Forma a cuore completa")
        
        buf = BytesIO()
        img.save(buf, format="PNG")
        st.download_button("Scarica PNG", buf.getvalue(), "peplo_heart_shape.png", "image/png")
