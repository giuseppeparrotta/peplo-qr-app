import streamlit as st
import qrcode
from PIL import Image, ImageDraw
import requests
from io import BytesIO

# Configurazione semplice
st.title("❤️ Peplo QR Generator")

link = st.text_input("Inserisci link:", "https://peplo.shop")

def crea_qr(testo):
    url_logo = "https://peplo.shop/img/peplo-logo-1632147760.jpg"
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=20, border=4)
    qr.add_data(testo)
    qr.make(fit=True)
    qr_img = qr.make_image().convert("RGB")
    width, height = qr_img.size
    final_img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(final_img)
    
    # Disegno cuori
    ps = 20 
    for y in range(0, height, ps):
        for x in range(0, width, ps):
            if qr_img.getpixel((x + 10, y + 10)) == (0, 0, 0):
                draw.ellipse([x+2, y+2, x+11, y+11], fill="black")
                draw.ellipse([x+9, y+2, x+18, y+11], fill="black")
                draw.polygon([(x+2, y+10), (x+10, y+18), (x+18, y+10)], fill="black")

    # Logo
    try:
        res = requests.get(url_logo, timeout=10)
        logo = Image.open(BytesIO(res.content))
        logo.thumbnail((width//4, height//4))
        p = ((width - logo.size[0])//2, (height - logo.size[1])//2)
        draw.rectangle([p[0]-10, p[1]-10, p[0]+logo.size[0]+10, p[1]+logo.size[1]+10], fill="white")
        final_img.paste(logo, p)
    except:
        pass
    return final_img

if st.button("Genera"):
    img = crea_qr(link)
    st.image(img)
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.download_button("Scarica", buf.getvalue(), "qr.png", "image/png")
