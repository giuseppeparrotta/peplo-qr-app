import streamlit as st
import qrcode
from PIL import Image, ImageDraw
import os
from io import BytesIO

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Peplo KeyChain Maker", page_icon="❤️", layout="centered")
st.title("❤️ Peplo Portachiavi Generator")
st.write("Genera QR per portachiavi contenente SOLO il Codice Fiscale.")

# --- INPUT ---
cf_input = st.text_input("Inserisci Codice Fiscale:", "RSSMRA80A01H501U")

# Pulizia: Solo testo, maiuscolo, niente spazi
final_data = cf_input.upper().strip()

# Mostriamo cosa c'è dentro il QR
if final_data:
    st.info(f"Dato codificato: {final_data} (Lunghezza: {len(final_data)} car.)")

# --- GRAFICA ---

def draw_heart_module(draw, x, y, size, color="black"):
    # Moduli "grassi" per la stampa fisica
    m = size * 0.05 
    draw.ellipse([x + m, y + m, x + size/2 + m/2, y + size/2 + m], fill=color)
    draw.ellipse([x + size/2 - m/2, y + m, x + size - m, y + size/2 + m], fill=color)
    draw.polygon([
        (x + m, y + size/2),
        (x + size/2, y + size - m*0.2),
        (x + size - m, y + size/2)
    ], fill=color)

def is_inside_heart_shape(px, py, cx, cy, scale):
    x = (px - cx) / scale
    y = -(py - cy) / scale 
    try:
        val = (x**2 + y**2 - 1)**3 - (x**2 * (y**3))
        return val <= 0
    except:
        return False

def crea_qr_portachiavi(testo):
    # Box size alto per stampa definita (300dpi ready)
    box_size = 60 
    
    # VERSIONE 2 + ECC H (High)
    # Versione 2-H contiene fino a 20 caratteri alfanumerici.
    # Il CF ne ha 16. È PERFETTO. Massima ridondanza, pixel enormi.
    qr = qrcode.QRCode(
        version=2, 
        error_correction=qrcode.constants.ERROR_CORRECT_H, # 30% di correzione errore!
        box_size=box_size,
        border=0
    )
    qr.add_data(testo)
    qr.make(fit=True)
    
    matrix = qr.get_matrix()
    qr_cells = len(matrix)
    qr_pixel_dim = qr_cells * box_size

    # Tela (più abbondante per la forma a cuore)
    canvas_w = int(qr_pixel_dim * 1.6) 
    canvas_h = int(qr_pixel_dim * 1.5)
    
    final_img = Image.new("RGB", (canvas_w, canvas_h), "white")
    draw = ImageDraw.Draw(final_img)
    
    cx, cy = canvas_w // 2, canvas_h // 2
    heart_scale = canvas_w / 2.7

    # Spostamento in basso (Lobi Alti)
    # Con la versione 2 la matrice è piccola (25x25), quindi abbassiamo di meno moduli ma proporzionati
    qr_shift_y = 3 * box_size 
    
    qr_start_x = cx - (qr_pixel_dim // 2)
    qr_start_y = cy - (qr_pixel_dim // 2) + qr_shift_y
    heart_center_cy = cy + (box_size * 2)

    # 1. Sfondo Texture
    for y in range(0, canvas_h, box_size):
        for x in range(0, canvas_w, box_size):
            # Controllo geometrico
            if is_inside_heart_shape(x + box_size/2, y + box_size/2, cx, heart_center_cy, heart_scale):
                draw_heart_module(draw, x, y, box_size, color="black")

    # 2. QR Sovrapposto
    # Calcolo buco centrale per logo
    # In Ver 2 (25x25), un gap di 4 o 6 è sufficiente
    center_gap = 4 
    mid = qr_cells // 2

    for r in range(qr_cells):
        for c in range(qr_cells):
            px = qr_start_x + c * box_size
            py = qr_start_y + r * box_size
            
            # Buco Logo
            if (mid - center_gap) < r < (mid + center_gap) and \
               (mid - center_gap) < c < (mid + center_gap):
                draw.rectangle([px, py, px+box_size, py+box_size], fill="white")
                continue

            cell = matrix[r][c]
            
            # Finder Patterns (Angoli)
            is_finder = (r < 7 and c < 7) or \
                        (r < 7 and c >= qr_cells-7) or \
                        (r >= qr_cells-7 and c < 7)

            if is_finder:
                if cell:
                    draw.rectangle([px, py, px+box_size, py+box_size], fill="black")
                else:
                    draw.rectangle([px, py, px+box_size, py+box_size], fill="white")
            elif cell:
                draw_heart_module(draw, px, py, box_size, color="black")
            else:
                draw.rectangle([px, py, px+box_size, py+box_size], fill="white")

    # 3. Logo
    if os.path.exists("logo_peplo.jpg"):
        try:
            logo = Image.open("logo_peplo.jpg").convert("RGBA")
            hole_size = (center_gap * 2) * box_size
            target_size = int(hole_size * 0.9)
            logo.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
            
            lx = qr_start_x + (qr_pixel_dim // 2) - (logo.size[0] // 2)
            ly = qr_start_y + (qr_pixel_dim // 2) - (logo.size[1] // 2)
            final_img.paste(logo, (lx, ly), logo)
        except:
            pass

    return final_img

# --- UI ---
if st.button("Genera File Portachiavi"):
    if len(final_data) == 0:
        st.error("Inserisci un codice fiscale!")
    else:
        with st.spinner('Creazione Matrice ad Alta Resistenza...'):
            img = crea_qr_portachiavi(final_data)
            st.image(img, caption=f"Fidelity Key: {final_data}", width=400)
            
            buf = BytesIO()
            img.save(buf, format="PNG")
            st.download_button(
                label=f"Scarica PNG {final_data}", 
                data=buf.getvalue(), 
                file_name=f"keychain_{final_data}.png", 
                mime="image/png"
            )
