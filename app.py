import streamlit as st
import qrcode
from PIL import Image, ImageDraw
import os
from io import BytesIO
import math

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Peplo Total Heart QR", page_icon="❤️", layout="centered")
st.title("❤️ Peplo Total Heart QR")
st.write("Un cuore gigante fatto di cuori, che contiene il tuo QR code.")

link_input = st.text_input("Inserisci Link:", "https://peplo.shop")

# --- FUNZIONI DI DISEGNO ---

def draw_single_heart(draw, x, y, size, color="black"):
    """Disegna un singolo modulo a forma di cuore."""
    # Usiamo un cuore leggermente più cicciotto per riempire bene lo spazio
    m = size * 0.1 # Margine dinamico (10%)
    
    # Cerchio sinistro
    draw.ellipse([x + m, y + m, x + size/2 + m, y + size/2 + m], fill=color)
    # Cerchio destro
    draw.ellipse([x + size/2 - m, y + m, x + size - m, y + size/2 + m], fill=color)
    # Triangolo inferiore (punta)
    draw.polygon([
        (x + m*1.5, y + size/2), 
        (x + size/2, y + size - m), 
        (x + size - m*1.5, y + size/2)
    ], fill=color)

def is_inside_big_heart(cx, cy, x, y, radius):
    """Determina matematicamente se un punto (x,y) è dentro il cuore gigante."""
    # Normalizza le coordinate rispetto al centro e al raggio
    nx = (x - cx) / radius
    ny = -(y - cy) / radius # Invertiamo Y per la grafica computerizzata
    
    # Formula parametrica del cuore
    # (x^2 + y^2 - 1)^3 - x^2 * y^3 <= 0
    try:
        val = (nx**2 + ny**2 - 1)**3 - (nx**2 * (ny**3))
        return val <= 0.02 # Usiamo una piccola tolleranza per bordi più morbidi
    except:
        return False

# --- GENERATORE PRINCIPALE ---

def crea_qr_cuore_totale(testo):
    # 1. SETUP QR (Versione fissa per controllo dimensioni)
    # Aumentiamo box_size a 25 per cuori PIÙ GRANDI come richiesto
    ps = 25 
    qr = qrcode.QRCode(
        version=8, # Versione media per un buon equilibrio densità/grandezza
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=ps,
        border=0 # Nessun bordo, lo gestiamo noi
    )
    qr.add_data(testo)
    qr.make(fit=True)
    
    matrix = qr.get_matrix()
    qr_dim = len(matrix) # Numero di moduli per lato
    qr_pixel_size = qr_dim * ps # Dimensione totale in pixel del quadrato QR

    # 2. CREAZIONE TELA GIGANTE
    # La tela deve essere molto più grande del QR per contenere il cuore
    canvas_size = int(qr_pixel_size * 1.6) 
    final_img = Image.new("RGB", (canvas_size, canvas_size), "white")
    draw = ImageDraw.Draw(final_img)
    
    cx, cy = canvas_size // 2, canvas_size // 2 # Centro della tela
    
    # Raggio del cuore gigante (un po' meno della metà della tela per lasciare margine)
    heart_radius = (canvas_size // 2) * 0.9

    # 3. FASE 1: RIEMPIMENTO DELLO SFONDO (Il "Cuore Pieno")
    # Disegniamo una griglia di cuori su TUTTA la tela, se sono dentro la forma gigante
    for y in range(0, canvas_size, ps):
        for x in range(0, canvas_size, ps):
            # Calcoliamo il centro del modulo corrente
            mod_cx = x + ps // 2
            mod_cy = y + ps // 2
            
            if is_inside_big_heart(cx, cy, mod_cx, mod_cy, heart_radius):
                draw_single_heart(draw, x, y, ps, color="black")

    # 4. FASE 2: SOVRAPPOSIZIONE DEL QR CODE FUNZIONANTE
    # Calcoliamo dove inizia il quadrato del QR al centro della tela
    start_x_qr = cx - (qr_pixel_size // 2)
    start_y_qr = cy - (qr_pixel_size // 2)

    # Definiamo l'area centrale da saltare per il LOGO PEPLO
    center_gap = qr_dim // 6
    c_min_idx = qr_dim // 2 - center_gap
    c_max_idx = qr_dim // 2 + center_gap

    for r in range(qr_dim):
        for c in range(qr_dim):
            # Coordinate pixel sulla tela grande
            px = start_x_qr + c * ps
            py = start_y_qr + r * ps

            # Se siamo nell'area del logo centrale, puliamo e saltiamo
            if c_min_idx < r < c_max_idx and c_min_idx < c < c_max_idx:
                 draw.rectangle([px, py, px+ps, py+ps], fill="white")
                 continue

            # --- LOGICA DI SOVRAPPOSIZIONE ---
            cell_is_black = matrix[r][c]

            # Protezione Finder Patterns (i 3 angoli devono essere quadrati solidi)
            is_finder = (r < 7 and c < 7) or \
                        (r < 7 and c >= qr_dim-7) or \
                        (r >= qr_dim-7 and c < 7)

            if is_finder and cell_is_black:
                 # Disegna quadrato nero solido (sovrascrive lo sfondo)
                 draw.rectangle([px, py, px+ps, py+ps], fill="black")
            elif cell_is_black:
                 # È un modulo dati nero: Ridisegna il cuore (per sicurezza)
                 draw_single_heart(draw, px, py, ps, color="black")
            else:
                 # IMPORTANTE: È un modulo BIANCO del QR.
                 # Dobbiamo CANCELLARE il cuore di sfondo che c'è sotto!
                 draw.rectangle([px, py, px+ps, py+ps], fill="white")

    # 5. INSERIMENTO LOGO CENTRALE
    if os.path.exists("logo_peplo.jpg"):
        logo = Image.open("logo_peplo.jpg").convert("RGBA")
        # Calcola la dimensione del buco bianco centrale
        hole_size = (c_max_idx - c_min_idx) * ps
        # Ridimensiona il logo per starci dentro (con un piccolo margine)
        logo_target_size = int(hole_size * 0.9)
        logo.thumbnail((logo_target_size, logo_target_size), Image.Resampling.LANCZOS)
        
        # Posiziona al centro esatto
        logo_pos = (cx - logo.size[0]//2, cy - logo.size[1]//2)
        final_img.paste(logo, logo_pos, logo)

    return final_img

# --- INTERFACCIA ---
if st.button("Genera QR Cuore Totale"):
    with st.spinner('Creazione del cuore gigante in corso...'):
        img_finale = crea_qr_cuore_totale(link_input)
        # Mostriamo l'immagine più grande in Streamlit
        st.image(img_finale, caption="Scansiona il centro del cuore!", width=500)
        
        buf = BytesIO()
        img_finale.save(buf, format="PNG")
        st.download_button("Scarica Immagine PNG", buf.getvalue(), "peplo_total_heart.png", "image/png")
