>>> import streamlit as st
... import qrcode
... from PIL import Image, ImageDraw
... import requests
... from io import BytesIO
... 
... # Configurazione della pagina
... st.set_page_config(page_title="Peplo QR Generator", page_icon="❤️")
... 
... st.title("❤️ Peplo QR Generator")
... st.write("Genera QR code personalizzati con cuoricini e logo Peplo.")
... 
... # 1. Input dell'utente nella barra laterale o principale
... testo_qr = st.text_input("Inserisci il link o il testo:", "https://peplo.shop")
... nome_file_output = st.text_input("Nome del file da scaricare:", "qr_peplo_hearts")
... 
... # Funzione core di disegno (adattata per Streamlit)
... def genera_qr_cuori(testo):
...     url_logo = "https://peplo.shop/img/peplo-logo-1632147760.jpg"
...     
...     qr = qrcode.QRCode(
...         error_correction=qrcode.constants.ERROR_CORRECT_H,
...         box_size=20,
...         border=4,
...     )
...     qr.add_data(testo)
...     qr.make(fit=True)
...     
...     qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
...     width, height = qr_img.size
...     
...     final_img = Image.new("RGB", (width, height), "white")
...     draw = ImageDraw.Draw(final_img)
...     
...     pixel_size = 20 
    for y in range(0, height, pixel_size):
        for x in range(0, width, pixel_size):
            if qr_img.getpixel((x + pixel_size//2, y + pixel_size//2)) == (0, 0, 0):
                m = pixel_size // 10
                draw.ellipse([x+m, y+m, x+pixel_size//2+1, y+pixel_size//2+1], fill="black")
                draw.ellipse([x+pixel_size//2-1, y+m, x+pixel_size-m, y+pixel_size//2+1], fill="black")
                draw.polygon([(x+m, y+pixel_size//2), (x+pixel_size//2, y+pixel_size-m), (x+pixel_size-m, y+pixel_size//2)], fill="black")

    # Inserimento Logo
    try:
        response = requests.get(url_logo, timeout=10)
        logo = Image.open(BytesIO(response.content))
        logo_size = width // 4
        logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
        pos = ((width - logo.size[0]) // 2, (height - logo.size[1]) // 2)
        
        padding = 15
        draw.rectangle([pos[0]-padding, pos[1]-padding, pos[0]+logo.size[0]+padding, pos[1]+logo.size[1]+padding], fill="white")
        final_img.paste(logo, pos)
    except:
        st.warning("Impossibile caricare il logo, genero QR solo con cuori.")
        
    return final_img

# 2. Generazione al clic del pulsante
if st.button("Genera QR Code"):
    risultato = genera_qr_cuori(testo_qr)
    
    # Mostra l'anteprima
    st.image(risultato, caption="Anteprima del tuo QR Peplo", use_column_width=True)
    
    # Preparazione per il download
    buf = BytesIO()
    risultato.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    st.download_button(
        label="Scarica Immagine PNG",
        data=byte_im,
        file_name=f"{nome_file_output}.png",
        mime="image/png"

