import streamlit as st
import qrcode
from PIL import Image, ImageDraw
import os
from io import BytesIO

st.set_page_config(page_title="Peplo QR Generator", page_icon="❤️")

st.title("❤️ Peplo QR Generator")
st.write("Generatore di QR funzionante con cuoricini e logo Peplo.")

link = st.text_input("Inserisci l'URL per il QR:", "https://peplo.shop")

def crea_qr_peplo(testo):
    # 1. Creazione QR base (Alta correzione per massima leggibilità)
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=20, border=4)
    qr.add_data(testo)
    qr.make(fit=True)
    qr_img = qr.make_image().convert("RGB")
    width, height = qr_img.size
    
    final_img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(final_img)
    
    ps = 20 # Pixel size
    for y in range(0, height, ps):
        for x in range(0, width, ps):
            if qr_img.getpixel((x + 10, y + 10)) == (0, 0, 0):
                # PROTEZIONE ANGOLI: Se siamo nei tre quadrati grandi, usiamo quadrati normali
                # Questo garantisce che ogni telefono riesca a leggere il codice
                if (x < ps*7 and y < ps*7) or (x < ps*7 and y > height-ps*8) or (x > width-ps*8 and y < ps*7):
                    draw.rectangle([x, y, x+ps, y+ps], fill="black")
                else:
                    # DISEGNO CUORE OTTIMIZZATO (più piccolo per leggibilità)
                    m = 4 # Aumentiamo il margine per separare i cuori
                    draw.ellipse([x+m, y+m, x+ps//2+1, y+ps//2+1], fill="black")
                    draw.ellipse([x+ps//2-1, y+m, x+ps-m, y+ps//2+1], fill="black")
                    draw.polygon([(x+m, y+ps//2), (x+ps//2, y+ps-m), (x+ps-m, y+ps//2)], fill="black")

    # 2. Inserimento LOGO LOCALE
    try:
        if os.path.exists("logo_peplo.jpg"):
            logo = Image.open("logo_peplo.jpg").convert("RGBA")
            logo_w = width // 5 # Logo leggermente più piccolo per non disturbare la lettura
            logo_h = int((logo_w * logo.size[1]) / logo.size[0])
            logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
            p = ((width - logo.size[0])//2, (height - logo.size[1])//2)
            
            # Sfondo bianco pulito
            pad = 15
            draw.rectangle([p[0]-pad, p[1]-pad, p[0]+logo.size[0]+pad, p[1]+logo.size[1]+pad], fill="white")
            final_img.paste(logo, p, logo)
    except:
        pass
        
    return final_img

if st.button("Genera QR Code"):
    img = crea_qr_peplo(link)
    st.image(img, use_container_width=True)
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.download_button("Scarica Immagine", buf.getvalue(), "qr_peplo_fix.png", "image/png")
