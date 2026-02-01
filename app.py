import streamlit as st
import qrcode
from PIL import Image, ImageDraw, ImageOps
import numpy as np
import os
from io import BytesIO

# --- CONFIGURAZIONE STREAMLIT ---
st.set_page_config(page_title="Peplo Heart QR", page_icon="❤️")
st.title("❤️ Peplo Heart QR Generator")
st.write("Genera un QR code a forma di cuore, con moduli a cuore e il logo Peplo al centro.")

# --- INPUT UTENTE ---
link_input = st.text_input("Inserisci l'URL per il QR:", "https://peplo.shop")
logo_path = "logo_peplo.jpg" # Assicurati che questo file sia nel tuo repository

# --- FUNZIONI DI SUPPORTO ---

def draw_heart(draw, x, y, size, color):
    """Disegna un singolo cuore nel punto specificato."""
    # Formula approssimativa per un cuore
    # Regola i parametri per modificare la forma
    x0, y0 = x + size // 2, y + size // 2
    points = []
    for t in np.linspace(0, 2 * np.pi, 100):
        x_val = 16 * np.sin(t)**3
        y_val = 13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)
        # Scala e trasla il cuore
        points.append((x0 + x_val * size / 40, y0 - y_val * size / 40))
    draw.polygon(points, fill=color)

def create_heart_mask(size):
    """Crea una maschera a forma di cuore."""
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    # Disegna un grande cuore bianco sulla maschera nera
    draw_heart(draw, 0, 0, size, 255)
    return mask

def draw_finder_pattern(draw, x, y, size, color):
    """Disegna un pattern di ricerca circolare/a cuore."""
    # Cerchio esterno
    draw.ellipse((x, y, x + size, y + size), outline=color, width=int(size/10))
    # Cuore interno
    draw_heart(draw, x + size//4, y + size//4, size//2, color)

# --- FUNZIONE PRINCIPALE DI GENERAZIONE ---

def generate_heart_qr(data, logo_path):
    """Genera il QR code a forma di cuore."""
    
    # 1. Genera il QR code base
    qr = qrcode.QRCode(
        version=6,  # Versione più alta per una griglia più fitta
        error_correction=qrcode.constants.ERROR_CORRECT_H, # Alta correzione per il logo
        box_size=20,
        border=2
    )
    qr.add_data(data)
    qr.make(fit=True)
    qr_matrix = qr.get_matrix()
    matrix_size = len(qr_matrix)
    
    # 2. Crea l'immagine finale
    module_size = 20
    img_size = matrix_size * module_size
    qr_img = Image.new("RGB", (img_size, img_size), "white")
    draw = ImageDraw.Draw(qr_img)
    
    # Colore rosso per i cuori (puoi cambiarlo)
    heart_color = (200, 0, 0) 

    # 3. Disegna i moduli a forma di cuore
    for r in range(matrix_size):
        for c in range(matrix_size):
            if qr_matrix[r][c]:
                x = c * module_size
                y = r * module_size
                
                # Identifica e disegna i finder patterns in modo speciale
                if (r < 7 and c < 7) or \
                   (r < 7 and c >= matrix_size - 7) or \
                   (r >= matrix_size - 7 and c < 7):
                    # Disegna solo l'angolo in alto a sinistra del pattern 7x7
                    if (r == 0 and c == 0) or \
                       (r == 0 and c == matrix_size - 7) or \
                       (r == matrix_size - 7 and c == 0):
                        draw_finder_pattern(draw, x, y, 7 * module_size, heart_color)
                # Non disegnare sopra i finder patterns
                elif not ((r < 7 and c < 7) or \
                          (r < 7 and c >= matrix_size - 7) or \
                          (r >= matrix_size - 7 and c < 7)):
                    draw_heart(draw, x, y, module_size, heart_color)

    # 4. Applica la maschera a forma di cuore
    heart_mask = create_heart_mask(img_size)
    final_img = Image.new("RGB", (img_size, img_size), "white")
    final_img.paste(qr_img, (0, 0), heart_mask)
    
    # Disegna il contorno del cuore
    draw_final = ImageDraw.Draw(final_img)
    # Usa la stessa funzione per il contorno
    draw_heart(draw_final, 0, 0, img_size, outline=heart_color, width=5)

    # 5. Inserisci il logo al centro
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        # Dimensione del logo (circa 1/5 dell'immagine)
        logo_size = img_size // 5
        logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
        
        # Posizione centrale
        logo_pos = ((img_size - logo.size[0]) // 2, (img_size - logo.size[1]) // 2)
        
        # Crea uno sfondo bianco per il logo
        draw_final.rectangle(
            (logo_pos[0] - 10, logo_pos[1] - 10, 
             logo_pos[0] + logo.size[0] + 10, logo_pos[1] + logo.size[1] + 10),
            fill="white"
        )
        
        # Incolla il logo
        final_img.paste(logo, logo_pos, logo)
    else:
        st.warning(f"Logo non trovato in: {logo_path}. Caricalo nel repository.")

    return final_img

# --- INTERFACCIA DI GENERAZIONE ---

if st.button("Genera QR Cuore"):
    with st.spinner("Creazione del QR a forma di cuore in corso..."):
        try:
            final_qr = generate_heart_qr(link_input, logo_path)
            st.image(final_qr, caption="Il tuo Peplo Heart QR", use_container_width=True)
            
            # Preparazione per il download
            buf = BytesIO()
            final_qr.save(buf, format="PNG")
            st.download_button(
                label="Scarica Immagine PNG",
                data=buf.getvalue(),
                file_name="peplo_heart_qr.png",
                mime="image/png"
            )
        except Exception as e:
            st.error(f"Si è verificato un errore: {e}")
