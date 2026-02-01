import streamlit as st
import qrcode
from PIL import Image, ImageDraw
import os
from io import BytesIO

st.set_page_config(page_title="Peplo QR Generator", page_icon="❤️")

st.title("❤️ Peplo QR Generator")
st.write("Generatore di QR Code personalizzati per Peplo.")

link = st.text_input("Inserisci l'URL per il QR:", "https://peplo.shop")

def crea_qr_peplo(testo):
    # 1. Creazione QR base
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=20, border=4)
    qr.add_data(testo)
    qr.make(fit=True)
    qr_img = qr.make_image().convert("RGB")
    width, height = qr_img.size
    
    # 2. Creazione tela per cuori
    final_img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(final_img)
    
    # 3. Disegno cuori
    ps = 20 
    for y in range(0, height, ps):
        for x in range(0, width, ps):
            if qr_img.getpixel((x + 10, y + 10)) == (0, 0, 0):
                draw.ellipse([x+2, y+2, x+11, y+11], fill="black")
                draw.ellipse([x+9, y+2, x+18, y+11], fill="black")
                draw.polygon([(x+2, y+10), (x+10, y+18), (x+18, y+10)], fill="black")

    # 4. Inserimento LOGO LOCALE
    try:
        # Cerchiamo il file caricato nel repository
        if os.path.exists("logo_peplo.jpg"):
            logo = Image.open("logo_peplo.jpg").convert("RGBA")
            
            # Dimensioni logo
            logo_w = width // 4
            logo_h = int((logo_w * logo.size[1]) / logo.size[0])
            logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
            
            # Posizionamento
            p = ((width - logo.size[0])//2, (height - logo.size[1])//2)
            
            # Sfondo bianco
            pad = 20
            draw.rectangle([p[0]-pad, p[1]-pad, p[0]+logo.size[0]+pad, p[1]+logo.size[1]+pad], fill="white")
            
            final_img.paste(logo, p, logo)
        else:
            st.warning("File logo_peplo.jpg non trovato nel repository.")
    except Exception as e:
        st.error(f"Errore tecnico col logo: {e}")
        
    return final_img

if st.button("Genera QR Code"):
    img = crea_qr_peplo(link)
    st.image(img, use_container_width=True)
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.download_button("Scarica Immagine", buf.getvalue(), "qr_peplo.png", "image/png")
