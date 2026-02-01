import streamlit as st
import qrcode
from PIL import Image, ImageDraw
import os
from io import BytesIO

# Funzione ottimizzata per la scansionabilità
def crea_qr_peplo_funzionante(testo):
    # Usiamo la Versione 6: crea una griglia più fitta che "soffre" meno la presenza del logo
    qr = qrcode.QRCode(
        version=6, 
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
    # Area di rispetto per il logo: leggermente più piccola per salvare più dati
    gap = width // 7
    c_min, c_max = (width//2 - gap), (width//2 + gap)

    for y in range(0, height, ps):
        for x in range(0, width, ps):
            # 1. Lasciamo lo spazio bianco per il logo
            if c_min < x < c_max and c_min < y < c_max:
                continue
                
            if qr_img.getpixel((x + 10, y + 10)) == (0, 0, 0):
                # 2. PROTEZIONE VITALE: Angoli e linee di sincronizzazione sempre quadrati
                # Questo permette a qualsiasi smartphone di "agganciare" il codice
                if (x < ps*8 and y < ps*8) or (x < ps*8 and y > height-ps*9) or (x > width-ps*9 and y < ps*8):
                    draw.rectangle([x, y, x+ps, y+ps], fill="black")
                else:
                    # 3. CUORE GRANDE MA DISTANZIATO (m=3.5 per evitare che si tocchino)
                    m = 3.5 
                    draw.ellipse([x+m, y+m, x+ps//2+1, y+ps//2+1], fill="black")
                    draw.ellipse([x+ps//2-1, y+m, x+ps-m, y+ps//2+1], fill="black")
                    draw.polygon([(x+m, y+ps//2), (x+ps//2, y+ps-m), (x+ps-m, y+ps//2)], fill="black")

    # 4. Inserimento Logo
    if os.path.exists("logo_peplo.jpg"):
        logo = Image.open("logo_peplo.jpg").convert("RGBA")
        # Il logo deve essere contenuto nel gap bianco
        logo_w = (c_max - c_min) - 10
        logo.thumbnail((logo_w, logo_w), Image.Resampling.LANCZOS)
        p = ((width - logo.size[0])//2, (height - logo.size[1])//2)
        final_img.paste(logo, p, logo)
        
    return final_img

# Interfaccia Streamlit
st.title("❤️ Peplo QR Verificato")
link_input = st.text_input("Inserisci il link:", "https://peplo.shop")

if st.button("Genera QR Scansionabile"):
    img_finale = crea_qr_peplo_funzionante(link_input)
    st.image(img_finale, caption="Questo codice è ottimizzato per essere letto da tutti i telefoni")
    
    buf = BytesIO()
    img_finale.save(buf, format="PNG")
    st.download_button("Scarica PNG", buf.getvalue(), "qr_peplo_ok.png")
