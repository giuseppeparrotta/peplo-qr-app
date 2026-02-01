import streamlit as st
import qrcode
from PIL import Image, ImageDraw
import requests
from io import BytesIO

st.set_page_config(page_title="Peplo QR Generator", page_icon="❤️")

st.title("❤️ Peplo QR Generator")
st.write("Crea il tuo QR con i cuoricini e il logo Peplo ufficiale.")

link = st.text_input("Inserisci l'URL per il QR:", "https://peplo.shop")

def crea_qr_peplo(testo):
    # URL diretto del logo
    url_logo = "https://peplo.shop/img/peplo-logo-1632147760.jpg"
    
    # 1. Creazione QR base
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=20, border=4)
    qr.add_data(testo)
    qr.make(fit=True)
    qr_img = qr.make_image().convert("RGB")
    width, height = qr_img.size
    
    # 2. Creazione tela per cuori
    final_img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(final_img)
    
    # 3. Disegno cuori (ottimizzato)
    ps = 20 
    for y in range(0, height, ps):
        for x in range(0, width, ps):
            if qr_img.getpixel((x + 10, y + 10)) == (0, 0, 0):
                draw.ellipse([x+2, y+2, x+11, y+11], fill="black")
                draw.ellipse([x+9, y+2, x+18, y+11], fill="black")
                draw.polygon([(x+2, y+10), (x+10, y+18), (x+18, y+10)], fill="black")

    # 4. Inserimento LOGO (Versione rinforzata)
    try:
        # Usiamo un User-Agent per evitare che il sito blocchi lo scaricamento
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url_logo, headers=headers, timeout=10)
        logo = Image.open(BytesIO(res.content)).convert("RGBA")
        
        # Dimensioni logo (circa il 25% del QR)
        logo_w = width // 4
        logo_h = int((logo_w * logo.size[1]) / logo.size[0])
        logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        
        # Posizione centrale
        p = ((width - logo.size[0])//2, (height - logo.size[1])//2)
        
        # Sfondo bianco protettivo un po' più grande per far risaltare la scritta
        pad = 20
        draw.rectangle([p[0]-pad, p[1]-pad, p[0]+logo.size[0]+pad, p[1]+logo.size[1]+pad], fill="white")
        
        # Incolla logo
        final_img.paste(logo, p, logo)
    except Exception as e:
        st.error(f"Errore nel caricamento del logo: {e}")
        
    return final_img

if st.button("Genera QR Code"):
    with st.spinner('Creazione in corso...'):
        img = crea_qr_peplo(link)
        st.image(img, use_container_width=True)
        
        # Preparazione download
        buf = BytesIO()
        img.save(buf, format="PNG")
        st.download_button("Scarica Immagine PNG", buf.getvalue(), "qr_peplo.png", "image/png")
