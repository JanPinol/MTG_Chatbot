# streamlit run app.py
import streamlit as st
import time
from main import responder_pregunta

# CSS para el bubble
st.markdown(
    """
    <style>
    /* Burbuja de texto estilo retro */
    .bubble {
        position: relative;
        display: inline-block;
        margin: 16px;
        text-align: center;
        font-family: 'Press Start 2P', cursive;
        font-size: 16px;
        line-height: 1.3em;
        background-color: #fff;
        color: #000;
        padding: 12px;
        box-shadow:
            0 -4px #fff,
            0 -8px #000,
            4px 0 #fff,
            4px -4px #000,
            8px 0 #000,
            0 4px #fff,
            0 8px #000,
            -4px 0 #fff,
            -4px 4px #000,
            -8px 0 #000,
            -4px -4px #000,
            4px 4px #000;
        box-sizing: border-box;
    }
    .bubble.right::after {
        content: '';
        position: absolute;
        height: 4px;
        width: 4px;
        top: 84%;
        right: -8px;
        background: white;
        box-shadow:
            4px -4px #fff,
            4px 0 #fff,
            8px 0 #fff,
            0 -8px #fff,
            4px 4px #000,
            8px 4px #000,
            12px 4px #000,
            16px 4px #000,
            12px 0 #000,
            8px -4px #000,
            4px -8px #000,
            0 -4px #fff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("MTG Chatbot")
st.write("¡Bienvenido, haz tu pregunta al viejo sabio!")

# URLs de las imágenes de la boca animada
IMAGES = [
    "res/WizardBocaAbierta0%.png",
    "res/WizardBocaAbierta50%.png",
    "res/WizardBocaAbierta100%.png",
]

col_text, col_mago = st.columns([3, 1])

# Placeholders
with col_text:
    text_ph = st.empty()
    card_ph = st.empty()

with col_mago:
    img_ph = st.empty()
    img_ph.image(IMAGES[0], width=200)

# Input de la pregunta
user_input = st.text_input("Pregunta:")

if user_input:
    # Limpiar texto y carta de ejecuciones anteriores
    with col_text:
        text_ph.empty()
        card_ph.empty()
    # Boca cerrada mientras responde
    with col_mago:
        img_ph.image(IMAGES[0], width=200)

    # Llamada al backend
    respuesta = responder_pregunta(user_input)

    # Si la respuesta es URL, animar mensaje fijo y luego mostrar carta
    if respuesta.startswith(("http://", "https://")):
        mensaje = "¡Aquí está la imagen que me has pedido!"
        texto_parcial = ""
        img_idx = 0

        for ch in mensaje:
            texto_parcial += ch
            img_idx += 1
            # Actualizar boca
            with col_mago:
                img_ph.image(IMAGES[img_idx % len(IMAGES)], width=200)
            # Actualizar texto (dentro de una burbuja)
            with col_text:
                text_ph.markdown(f'<div class="bubble right">{texto_parcial}</div>', unsafe_allow_html=True)
            time.sleep(0.05)

        # Boca cerrada al terminar animación
        with col_mago:
            img_ph.image(IMAGES[0], width=200)

        # Mostrar carta debajo
        with col_text:
            card_ph.image(respuesta,  use_container_width=True)

    else:
        # Animación texto normal letra a letra
        texto_parcial = ""
        img_idx = 0

        for ch in respuesta:
            texto_parcial += ch
            img_idx += 1
            with col_mago:
                img_ph.image(IMAGES[img_idx % len(IMAGES)], width=200)
            with col_text:
                text_ph.markdown(f'<div class="bubble right">{texto_parcial}</div>', unsafe_allow_html=True)
            time.sleep(0.05)

        # Boca cerrada al finalizar
        with col_mago:
            img_ph.image(IMAGES[0], width=200)
