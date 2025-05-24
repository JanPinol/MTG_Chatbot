# Iniciar en localhost
# Imports
import streamlit as st
import time
from main import responder_pregunta

# Rutas a las imagenes de la boca
IMAGES = [
    "res/WizardBocaAbierta0%.png",
    "res/WizardBocaAbierta50%.png",
    "res/WizardBocaAbierta100%.png",
]

st.title("MTG Chatbot")
st.write("¡Bienvenido, haz tu pregunta al viejo sabio!")
img_ph = st.empty()
text_ph = st.empty()

img_ph.image(IMAGES[0], width=200)

user_input = st.text_input("Pregunta:")

if user_input:
    img_ph.image(IMAGES[0], width=200)

    # calculamos la respuesta
    respuesta = responder_pregunta(user_input)
    texto_parcial = ""
    img_idx = 0

    # animamos letra a letra con cambio de boca Cada 5 ms sale una letra
    for ch in respuesta:
        texto_parcial += ch
        img_idx += 1

        img_ph.image(IMAGES[img_idx % len(IMAGES)], width=200)
        text_ph.markdown(f"> {texto_parcial}  ")
        time.sleep(0.05)

    # Al terminar, boca cerrada
    img_ph.image(IMAGES[0], width=200)