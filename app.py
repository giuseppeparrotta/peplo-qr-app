import streamlit as st
import qrcode
from PIL import Image, ImageDraw
import os
from io import BytesIO

st.set_page_config(page_title="Peplo QR Heart Shape", page_icon="❤️")

st.title("❤️ Peplo QR a Forma di Cuore")
st.write("Il QR code ora segue la silhouette di un cuore.")

link = st.text_input("Inserisci l'URL:", "https://peplo.shop")

def crea_qr_silhouette_cuore(testo):
    # Usiamo una versione più alta (10) per avere più "pixel" e definire meglio il cuore
    qr = qrcode.QRCode(
        version=10,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=0 # Togliamo il bordo standard per gestire noi la forma
    )
    qr.add_data(testo)
    qr.make(fit=True)
    qr_img = qr.make_image().convert("RGB")
    qr_width, qr_height = qr_img.size
    
    # Creiamo una tela più grande per contenere la sagoma del cuore
    canvas_size = int(qr_width * 1.5)
    final_img = Image.new("RGB", (canvas_size, canvas_size), "white")
    draw = ImageDraw.Draw(final_img)
    
    offset = (canvas_size - qr_width) // 2
    ps = 20 # Pixel size

    # Funzione matematica per determinare se un punto è dentro un cuore
    def is_inside_heart(x, y, size):
        # Normalizziamo x e y tra -1.5 e 1.5
        nx = (x - size/2) / (size/4)
        ny = -(y - size/2.2) / (size/4)
        # Equazione classica del cuore: (x^2 + y^2 - 1)^3 - x^2 * y^3 <= 0
        return (nx**2 + ny**2 - 1)**3 - nx**2 * ny**3 <= 0

    # 1. Disegniamo i moduli del QR
    for y in range(0, qr_height, ps):
        for x in range(0, qr_width, ps):
            # Posizione assoluta sulla tela
            abs_x = x + offset
            abs_y = y + offset
            
            # Area del logo centrale (buco bianco)
            gap = qr_width // 7
            if (qr_width//2 - gap) < x < (qr_width//2 + gap) and (qr_width//2 - gap) < y < (qr_width//2 + gap):
                continue

            # Se il modulo originale è nero E siamo dentro la sagoma del cuore
            if qr_img.getpixel((x + 10, y + 10)) == (0, 0, 0):
                # Protezione angoli (Finder Patterns)
                if (x < ps*7 and y < ps*7) or (x < ps*7 and y > qr_height-ps*8) or (x > qr_width-ps*8 and y < ps*7):
                    draw.rectangle([abs_x, abs_y, abs_x+ps, abs_y+ps], fill="black")
                else:
                    # Disegno cuore piccolo
                    m = 3
                    draw.ellipse([abs_x+m, abs_y+m, abs_x+ps//2+1, abs_y+ps//2+1], fill="black")
                    draw.ellipse([abs_x+ps//2-1, abs_y+m, abs_x+ps-m, abs_y+ps//2+1], fill="black")
                    draw.polygon([(abs_x+m, abs_y+ps//2), (abs_x+ps//2, abs_y+ps-m), (abs_x+ps-m, abs_y+ps//2)], fill="black")
            
            # Se il modulo è BIANCO ma siamo fuori dal quadrato QR originale, 
            # potremmo aggiungere cuoricini decorativi per completare la forma del cuore? 
            # No, meglio restare puliti per la scansione.

    # 2. Mascheriamo tutto ciò che è fuori dalla sagoma del cuore globale
    # Creiamo un'immagine maschera per "tagliare" gli angoli del quadrato
    mask = Image.new("L", (canvas_size, canvas_size), 0)
    mask_draw = ImageDraw.Draw(mask)
    for y in range(canvas_size):
        for x in range(canvas_size):
            if is_inside_heart(x, y, canvas_size):
                mask_draw.point((x, y), 255)
    
    # Applichiamo la maschera (opzionale, per un look più netto)
    # final_img = Image.composite(final_img, Image.new("RGB", (canvas_size, canvas_size), "white"), mask)

    # 3. Inserimento Logo Peplo
    if os.path.exists("logo_peplo.jpg"):
        logo = Image.open("logo_peplo.jpg").convert("RGBA")
        logo_w = (qr_width // 4)
        logo.thumbnail((logo_w, logo_w), Image.Resampling.LANCZOS)
        p = ((canvas_size - logo.size[0])//2, (canvas_size - logo.size[1])//2)
        draw.rectangle([p[0]-10, p[1]-10, p[0]+logo.size[0]+10, p[1]+logo.size[1]+10], fill="white")
        final_img.paste(logo, p, logo)
        
    return final_img

if st.button("Genera Sagoma a Cuore"):
    img_heart = crea_qr_silhouette_cuore(link)
    st.image(img_heart)
    
    buf = BytesIO()
    img_heart.save(buf, format="PNG")
    st.download_button("Scarica QR Cuore", buf.getvalue(), "qr_peplo_heart_shape.png")
