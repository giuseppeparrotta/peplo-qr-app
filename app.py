import streamlit as st
import qrcode
from PIL import Image, ImageDraw
import os
from io import BytesIO

st.set_page_config(page_title="Peplo QR Generator", page_icon="❤️")

st.title("❤️ Peplo QR Generator")
st.write("Versione ad Alta Scansionabilità (Testata)")

link = st.text_input("Inserisci l'URL:", "https://peplo.shop")

def crea_qr_peplo_perfetto(testo):
    # Forziamo la Versione 5 e Error Correction High per la massima robustezza
    qr = qrcode.QRCode(
        version=5, 
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
    
    ps = 20 
    # Area centrale vuota per il logo (ridotta per sicurezza dati)
    gap = width // 6 
    c_min, c_max = (width//2 - gap), (width//2 + gap)

    for y in range(0, height, ps):
        for x in range(0, width, ps):
            # Lasciamo lo spazio bianco per il logo
            if c_min < x < c_max and c_min < y < c_max:
                continue
                
            if qr_img.getpixel((x + 10, y + 10)) == (0, 0, 0):
                # ANGOLI DI POSIZIONAMENTO: devono restare quadrati perfetti
                if (x < ps*7 and y < ps*7) or (x < ps*7 and y > height-ps*8) or (x > width-ps*8 and y < ps*7):
                    draw.rectangle([x, y, x+ps, y+ps], fill="black")
                else:
                    # CUORE GRANDE MA DISTANZIATO (m=3 per lasciare aria)
                    m = 3 
                    draw.ellipse([x+m, y+m, x+ps//2+1, y+ps//2+1], fill="black")
                    draw.ellipse([x+ps//2-1, y+m, x+ps-m, y+ps//2+1], fill="black")
                    draw.polygon([(x+m, y+ps//2), (x+ps//2, y+ps-m), (x+ps-m, y+ps//2)], fill="black")

    # Inserimento Logo Peplo
    if os.path.exists("logo_peplo.jpg"):
        logo = Image.open("logo_peplo.jpg").convert("RGBA")
        logo_w = (c_max - c_min) - 10
        logo.thumbnail((logo_w, logo_w), Image.Resampling.LANCZOS)
        p = ((width - logo.size[0])//2, (height - logo.size[1])//2)
        final_img.paste(logo, p, logo)
        
    return final_img

if st.button("Genera e Verifica"):
    img = crea_qr_peplo_perfetto(link)
    st.image(img, caption="Inquadra questo codice con il tuo telefono")
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.download_button("Scarica PNG", buf.getvalue(), "qr_peplo_scansionabile.png")
