import streamlit as st
import qrcode
from PIL import Image, ImageDraw
import os
from io import BytesIO

st.set_page_config(page_title="Peplo QR Generator", page_icon="❤️")

st.title("❤️ Peplo QR Generator")
st.write("Versione con cuori grandi e logo protetto.")

link = st.text_input("Inserisci l'URL per il QR:", "https://peplo.shop")

def crea_qr_peplo_grande(testo):
    # Usiamo la versione 8 o superiore per avere abbastanza densità per il logo
    qr = qrcode.QRCode(
        version=None, 
        error_correction=qrcode.constants.ERROR_CORRECT_H, 
        box_size=20, 
        border=4
    )
    qr.add_data(testo)
    qr.make(fit=True)
    qr_img = qr.make_image().convert("RGB")
    width, height = qr_img.size
    
    final_img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(final_img)
    
    ps = 20 # Dimensione fissa del modulo
    
    # Definiamo l'area centrale da lasciare bianca per il logo (circa il 25% del totale)
    margine_centro = width // 5 
    centro_inizio = (width // 2) - margine_centro
    centro_fine = (width // 2) + margine_centro

    for y in range(0, height, ps):
        for x in range(0, width, ps):
            # Saltiamo il disegno se siamo nell'area destinata al logo
            if centro_inizio < x < centro_fine and centro_inizio < y < centro_fine:
                continue
                
            if qr_img.getpixel((x + 10, y + 10)) == (0, 0, 0):
                # 1. PROTEZIONE ANGOLI (Finder Patterns): quadrati per la massima leggibilità
                if (x < ps*7 and y < ps*7) or (x < ps*7 and y > height-ps*8) or (x > width-ps*8 and y < ps*7):
                    draw.rectangle([x, y, x+ps, y+ps], fill="black")
                else:
                    # 2. DISEGNO CUORE GRANDE (come il primo codice)
                    # Usiamo m=2 per farli quasi toccare e apparire grandi
                    m = 2 
                    # Cerchio sinistro
                    draw.ellipse([x+m, y+m, x+ps//2+2, y+ps//2+2], fill="black")
                    # Cerchio destro
                    draw.ellipse([x+ps//2-2, y+m, x+ps-m, y+ps//2+2], fill="black")
                    # Triangolo inferiore (punta)
                    draw.polygon([
                        (x+m, y+ps//2+1), 
                        (x+ps//2, y+ps-m), 
                        (x+ps-m, y+ps//2+1)
                    ], fill="black")

    # 3. Inserimento LOGO PEPLO
    try:
        if os.path.exists("logo_peplo.jpg"):
            logo = Image.open("logo_peplo.jpg").convert("RGBA")
            # Adattiamo il logo allo spazio bianco creato
            area_logo_size = (centro_fine - centro_inizio) - 10
            logo.thumbnail((area_logo_size, area_logo_size), Image.Resampling.LANCZOS)
            
            p = ((width - logo.size[0])//2, (height - logo.size[1])//2)
            # Incolliamo il logo senza aggiungere ulteriore rettangolo bianco sopra (lo spazio è già vuoto)
            final_img.paste(logo, p, logo)
    except Exception as e:
        st.error(f"Logo non caricato: {e}")
        
    return final_img

if st.button("Genera QR Code"):
    with st.spinner('Creazione in corso...'):
        img = crea_qr_peplo_grande(link)
        st.image(img, use_container_width=True)
        
        buf = BytesIO()
        img.save(buf, format="PNG")
        st.download_button("Scarica QR Peplo", buf.getvalue(), "qr_peplo_hearts_big.png", "image/png")
