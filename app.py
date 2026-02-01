import streamlit as st
import qrcode
from PIL import Image, ImageDraw
import os
from io import BytesIO

st.set_page_config(page_title="Peplo QR Generator", page_icon="❤️")

st.title("❤️ Peplo QR Generator")
st.write("Versione Ottimizzata: il logo non copre più i dati vitali.")

link = st.text_input("Inserisci l'URL per il QR:", "https://peplo.shop")

def crea_qr_peplo_blindato(testo):
    # 1. Creazione QR con Versione fissa (10) per avere più spazio
    # L'error correction H è fondamentale per i QR artistici
    qr = qrcode.QRCode(
        version=10, 
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
    
    ps = 20 # Dimensione del modulo
    
    # 2. Definiamo l'area "Proibita" (dove starà il logo)
    # Calcoliamo il centro per lasciare un buco bianco perfetto
    centro_inizio = (width // 2) - (width // 6)
    centro_fine = (width // 2) + (width // 6)

    for y in range(0, height, ps):
        for x in range(0, width, ps):
            # Se siamo nell'area centrale, saltiamo il disegno (lasciamo bianco)
            if centro_inizio < x < centro_fine and centro_inizio < y < centro_fine:
                continue
                
            if qr_img.getpixel((x + 10, y + 10)) == (0, 0, 0):
                # PROTEZIONE ANGOLI (Finder Patterns) - Devono essere quadrati!
                if (x < ps*7 and y < ps*7) or (x < ps*7 and y > height-ps*8) or (x > width-ps*8 and y < ps*7):
                    draw.rectangle([x, y, x+ps, y+ps], fill="black")
                else:
                    # DISEGNO CUORE (Leggermente più cicciotto per estetica)
                    m = 3 
                    draw.ellipse([x+m, y+m, x+ps//2+2, y+ps//2+2], fill="black")
                    draw.ellipse([x+ps//2-2, y+m, x+ps-m, y+ps//2+2], fill="black")
                    draw.polygon([(x+m, y+ps//2+1), (x+ps//2, y+ps-m), (x+ps-m, y+ps//2+1)], fill="black")

    # 3. Inserimento LOGO PEPLO
    try:
        if os.path.exists("logo_peplo.jpg"):
            logo = Image.open("logo_peplo.jpg").convert("RGBA")
            # Ridimensioniamo il logo per stare perfettamente nel "buco" creato
            logo_w = (centro_fine - centro_inizio) - 20
            ratio = logo.size[1] / logo.size[0]
            logo_h = int(logo_w * ratio)
            logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
            
            p = ((width - logo.size[0])//2, (height - logo.size[1])//2)
            final_img.paste(logo, p, logo)
    except Exception as e:
        st.error(f"Errore logo: {e}")
        
    return final_img

if st.button("Genera QR Code"):
    img = crea_qr_peplo_blindato(link)
    st.image(img, use_container_width=True)
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.download_button("Scarica Ora", buf.getvalue(), "qr_peplo_final.png", "image/png")
