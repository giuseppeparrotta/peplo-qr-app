import streamlit as st
import qrcode
from PIL import Image, ImageDraw
import os
from io import BytesIO
import math

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Peplo Heart QR Ultimate", page_icon="❤️", layout="centered")
st.title("❤️ Peplo Heart QR - Perfect Fit")
st.write("QR Code spostato in alto e allargato per toccare i bordi del cuore.")

link_input = st.text_input("Inserisci Link:", "https://peplo.shop")

# --- FUNZIONI DI GEOMETRIA E DISEGNO ---

def draw_heart_module(draw, x, y, size, color="black"):
    """
    Disegna un singolo 'pixel' del QR a forma di cuore.
    """
    # Margine per definire bene la forma
    m = size * 0.15 
    
    # Parte sinistra (cerchio)
    draw.ellipse([x + m, y + m, x + size/2 + m/2, y + size/2 + m], fill=color)
    # Parte destra (cerchio)
    draw.ellipse([x + size/2 - m/2, y + m, x + size - m, y + size/2 + m], fill=color)
    # Triangolo inferiore
    draw.polygon([
        (x + m*1.2, y + size/2),          # Punto sinistro
        (x + size/2, y + size - m*0.5),   # Punta in basso
        (x + size - m*1.2, y + size/2)    # Punto destro
    ], fill=color)

def is_point_in_heart(px, py, cx, cy, radius):
    """
    Restituisce True se il punto (px, py) è dentro la sagoma del cuore gigante.
    cx, cy: Centro del cuore
    radius: Scala del cuore
    """
    # Normalizzazione coordinate
    x = (px - cx) / radius
    y = -(py - cy) / radius # Invertiamo Y
    
    # Equazione del cuore: (x^2 + y^2 - 1)^3 - x^2 * y^3 <= 0
    # Aggiungiamo un fattore di tolleranza per renderlo "cicciotto"
    try:
        val = (x**2 + y**2 - 1)**3 - (x**2 * (y**3))
        return val <= 0
    except:
        return False

# --- MOTORE DI GENERAZIONE ---

def crea_qr_peplo_fit(testo):
    # 1. SETUP QR
    # Usiamo box_size grande per avere cuori ben definiti
    box_size = 30 
    
    # Version 6 è un buon compromesso tra densità e leggibilità per questa forma
    qr = qrcode.QRCode(
        version=6, 
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=0
    )
    qr.add_data(testo)
    qr.make(fit=True)
    
    matrix = qr.get_matrix()
    qr_cells = len(matrix)          # Numero di celle (es. 41)
    qr_pixel_dim = qr_cells * box_size # Dimensione in pixel del quadrato QR (es. 1230px)

    # 2. CALCOLO DIMENSIONI TELA E POSIZIONE
    # Per far "toccare" gli spigoli, il cuore deve essere solo leggermente più grande del QR.
    # Un rapporto di 1.35 è ottimale per far toccare gli angoli bassi quando il QR è alzato.
    canvas_w = int(qr_pixel_dim * 1.35)
    canvas_h = int(qr_pixel_dim * 1.25) # Leggermente meno alto per compattare
    
    final_img = Image.new("RGB", (canvas_w, canvas_h), "white")
    draw = ImageDraw.Draw(final_img)
    
    cx = canvas_w // 2
    cy = canvas_h // 2
    
    # Raggio del cuore gigante
    heart_radius = (canvas_w // 2) * 0.95

    # --- SPOSTAMENTO RICHIESTO ---
    # "Salire di 3 interlinee" -> Spostiamo la Y di partenza in alto di 3 * box_size
    shift_up_pixels = 3 * box_size
    
    # Calcolo coordinate angolo in alto a sinistra del QR
    qr_start_x = cx - (qr_pixel_dim // 2)
    qr_start_y = cy - (qr_pixel_dim // 2) - shift_up_pixels

    # 3. DISEGNO SFONDO (IL CUORE GIGANTE PIENO DI CUORICINI)
    # Iteriamo su tutta la tela con passo = box_size
    for y in range(0, canvas_h, box_size):
        for x in range(0, canvas_w, box_size):
            # Centro del modulo corrente
            mcx = x + box_size // 2
            mcy = y + box_size // 2
            
            # Se siamo dentro la forma del cuore, disegniamo un cuoricino nero
            # Applichiamo un piccolo offset verticale al cuore gigante per centrarlo visivamente
            if is_point_in_heart(mcx, mcy, cx, cy + box_size*2, heart_radius):
                draw_heart_module(draw, x, y, box_size, color="black")

    # 4. SOVRAPPOSIZIONE QR CODE (SCULTUREA)
    # Ora "scolpiamo" il QR sopra lo sfondo
    
    # Definiamo l'area centrale per il LOGO (buco bianco)
    center_gap = qr_cells // 6
    mid = qr_cells // 2
    
    for r in range(qr_cells):
        for c in range(qr_cells):
            # Coordinate pixel attuali sulla tela
            px = qr_start_x + c * box_size
            py = qr_start_y + r * box_size
            
            # Gestione Buco Logo
            if (mid - center_gap) < r < (mid + center_gap) and \
               (mid - center_gap) < c < (mid + center_gap):
                # Pulisce l'area per il logo (disegna quadrato bianco sopra i cuori di sfondo)
                draw.rectangle([px, py, px+box_size, py+box_size], fill="white")
                continue

            cell = matrix[r][c]
            
            # Identifica i Finder Patterns (Angoli)
            is_finder = (r < 7 and c < 7) or \
                        (r < 7 and c >= qr_cells-7) or \
                        (r >= qr_cells-7 and c < 7)
            
            if is_finder:
                if cell: # Se è nero nel finder
                    draw.rectangle([px, py, px+box_size, py+box_size], fill="black")
                else:    # Se è bianco nel finder
                    draw.rectangle([px, py, px+box_size, py+box_size], fill="white")
            
            elif cell:
                # È un dato NERO: Assicuriamoci che ci sia un cuore nero
                # (Lo sfondo lo ha già fatto, ma lo ridisegniamo per sicurezza o se fuori sagoma)
                draw_heart_module(draw, px, py, box_size, color="black")
            
            else:
                # È un dato BIANCO: DOBBIAMO CANCELLARE IL CUORE DI SFONDO!
                # Questo è il passaggio chiave per rendere il QR leggibile
                # Disegniamo un quadrato bianco che "copre" il cuore decorativo sottostante
                draw.rectangle([px, py, px+box_size, py+box_size], fill="white")

    # 5. LOGO PEPLO
    if os.path.exists("logo_peplo.jpg"):
        try:
            logo = Image.open("logo_peplo.jpg").convert("RGBA")
            # Calcolo dimensione buco logo
            hole_pixel_size = (center_gap * 2) * box_size
            # Logo leggermente più piccolo del buco
            target_size = int(hole_pixel_size * 0.9)
            
            logo.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
            
            # Posizione Logo (centrato rispetto al QR, non alla tela)
            l_x = qr_start_x + (qr_pixel_dim // 2) - (logo.size[0] // 2)
            l_y = qr_start_y + (qr_pixel_dim // 2) - (logo.size[1] // 2)
            
            final_img.paste(logo, (l_x, l_y), logo)
        except:
            pass

    return final_img

# --- UI ---
if st.button("Genera QR Peplo Definitivo"):
    with st.spinner('Calcolo geometria...'):
        img = crea_qr_peplo_fit(link_input)
        st.image(img, caption="QR alzato e allargato", width=500)
        
        buf = BytesIO()
        img.save(buf, format="PNG")
        st.download_button("Scarica PNG", buf.getvalue(), "peplo_heart_fit.png", "image/png")
