import streamlit as st
import qrcode
from PIL import Image, ImageDraw
import os
from io import BytesIO
import math

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Peplo Heart Perfect", page_icon="❤️", layout="centered")
st.title("❤️ Peplo QR: Lobi Alti")
st.write("QR Code posizionato in basso per lasciare ampio spazio alle curve superiori del cuore.")

link_input = st.text_input("Inserisci Link:", "https://peplo.shop")

# --- DISEGNO MODULO (Il singolo cuoricino) ---
def draw_heart_module(draw, x, y, size, color="black"):
    m = size * 0.15 # Margine per non farli toccare troppo
    # Cerchio sx
    draw.ellipse([x + m, y + m, x + size/2 + m/2, y + size/2 + m], fill=color)
    # Cerchio dx
    draw.ellipse([x + size/2 - m/2, y + m, x + size - m, y + size/2 + m], fill=color)
    # Punta
    draw.polygon([
        (x + m*1.2, y + size/2),
        (x + size/2, y + size - m*0.5),
        (x + size - m*1.2, y + size/2)
    ], fill=color)

# --- MATEMATICA DEL CUORE ---
def is_inside_heart_shape(px, py, cx, cy, scale):
    # Normalizza coordinate
    x = (px - cx) / scale
    y = -(py - cy) / scale # Invertiamo Y
    
    # Formula del cuore "cicciotto"
    try:
        val = (x**2 + y**2 - 1)**3 - (x**2 * (y**3))
        return val <= 0
    except:
        return False

# --- GENERATORE ---
def crea_qr_lobi_alti(testo):
    # 1. SETUP QR
    box_size = 30 # Grande per definizione
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

    # 2. CALCOLO TELA
    # La tela deve essere più alta per accogliere i lobi sopra il QR
    canvas_w = int(qr_pixel_dim * 1.5) 
    canvas_h = int(qr_pixel_dim * 1.4) 
    
    final_img = Image.new("RGB", (canvas_w, canvas_h), "white")
    draw = ImageDraw.Draw(final_img)
    
    cx = canvas_w // 2
    cy = canvas_h // 2
    
    # Scala del cuore (Molto grande per fare l'effetto avvolgente)
    heart_scale = canvas_w / 2.7

    # 3. SPOSTAMENTO QR (IL TRUCCO)
    # Spostiamo il QR in BASSO (aumentando Y) di 4 moduli
    # Questo fa sì che il cuore sembri "salire" sopra il QR
    qr_shift_y = 4 * box_size 
    
    # Calcolo coordinate angolo in alto a sinistra del QR
    qr_start_x = cx - (qr_pixel_dim // 2)
    qr_start_y = cy - (qr_pixel_dim // 2) + qr_shift_y

    # Centro geometrico del cuore (lo alziamo un po' per compensare il QR basso)
    heart_center_cy = cy + (box_size * 2)

    # 4. DISEGNO SFONDO (TEXTURE CUORI)
    for y in range(0, canvas_h, box_size):
        for x in range(0, canvas_w, box_size):
            # Verifichiamo se siamo dentro il cuore gigante
            if is_inside_heart_shape(x + box_size/2, y + box_size/2, cx, heart_center_cy, heart_scale):
                draw_heart_module(draw, x, y, box_size, color="black")

    # 5. SOVRAPPOSIZIONE QR CODE
    center_gap = qr_cells // 6
    mid = qr_cells // 2

    for r in range(qr_cells):
        for c in range(qr_cells):
            # Posizione pixel sulla tela (tenendo conto dello spostamento in basso)
            px = qr_start_x + c * box_size
            py = qr_start_y + r * box_size
            
            # Salta area logo centrale
            if (mid - center_gap) < r < (mid + center_gap) and \
               (mid - center_gap) < c < (mid + center_gap):
                draw.rectangle([px, py, px+box_size, py+box_size], fill="white")
                continue

            cell = matrix[r][c]
            
            # Finder Patterns (Angoli solidi per scansione)
            is_finder = (r < 7 and c < 7) or \
                        (r < 7 and c >= qr_cells-7) or \
                        (r >= qr_cells-7 and c < 7)

            if is_finder:
                if cell:
                    draw.rectangle([px, py, px+box_size, py+box_size], fill="black")
                else:
                    draw.rectangle([px, py, px+box_size, py+box_size], fill="white")
            elif cell:
                # Modulo NERO -> Disegna cuore (ridondante su sfondo nero, ma serve se il QR esce dalla sagoma)
                draw_heart_module(draw, px, py, box_size, color="black")
            else:
                # Modulo BIANCO -> CANCELLA il cuore di sfondo
                draw.rectangle([px, py, px+box_size, py+box_size], fill="white")

    # 6. LOGO PEPLO
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
if st.button("Genera QR Definitivo"):
    with st.spinner('Creazione in corso...'):
        img = crea_qr_lobi_alti(link_input)
        st.image(img, caption="Curve alte e QR integrato", width=500)
        
        buf = BytesIO()
        img.save(buf, format="PNG")
        st.download_button("Scarica PNG", buf.getvalue(), "peplo_lobi_alti.png", "image/png")
