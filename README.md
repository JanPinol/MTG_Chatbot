# Chatbot MTG – Asistente inteligente para Magic: The Gathering

Este proyecto consiste en un chatbot especializado en el universo de **Magic: The Gathering (MTG)**, diseñado para responder preguntas en lenguaje natural usando procesamiento de lenguaje natural (NLP) y consultas a la API pública de **Scryfall**.

## ¿Qué puede hacer?

Nuestro asistente es capaz de:

- Responder preguntas sobre reglas, cartas y habilidades.
- Mostrar imágenes y detalles de cualquier carta de MTG.
- Explicar mecánicas clave del juego con definiciones claras.
- Crear mazos temáticos según colores.
- Consultar precios, legalidad y formatos de juego.
- Ofrecer respuestas en español incluso con sinónimos o lenguaje informal.

## Tecnologías utilizadas

- **Python 3.10+**
- **spaCy** (`es_core_news_md`) – para el procesamiento del lenguaje
- **Streamlit** – para crear la interfaz web interactiva
- **Scryfall API** – para obtener datos actualizados sobre cartas
- **Diccionario local** – para definir conceptos clave y sinónimos

## Cómo ejecutarlo

1. Instala las dependencias necesarias:
```
$ pip install streamlit spacy requests
```


2. Asegúrate de tener descargado el modelo de spaCy en español:

```
$ python -m spacy download es_core_news_md
```

3. Ejecuta el servidor con Streamlit:

```
$ streamlit run app.py
```

4. Abre tu navegador en `http://localhost:8501` para interactuar con el chatbot.

## Estructura del proyecto

```
chatbot-mtg/
├── app.py                 # Interfaz de usuario con animaciones
├── main.py                # Lógica del chatbot (procesamiento y respuestas)
├── definiciones.py        # Diccionario local de términos y alias
├── README.md              # Este archivo
├── res/                   # Imágenes del mago animado
```

## Ejemplos de uso

Puedes hacer preguntas como:

- `¿Cuánto cuesta Niv-Mizzet, Parun?`
- `¿Qué hace la habilidad de Deathtouch?`
- `Dame una imagen de Black Lotus.`
- `¿Qué colores tiene Atraxa, Praetors' Voice?`
- `¿Es legal Sol Ring en Commander?`
- `Hazme un mazo verde.`
- `¿Qué es una carta con Flash?`

## Autores

- **Gael Caballero** - `gael.caballero@students.salle.url.edu`
- **Ivan Tubella** - `ivan.tubella@students.salle.url.edu`
- **Jan Piñol** - `jan.pinol@students.salle.url.edu`
- **Pablo Molina** - `p.molina@students.salle.url.edu`

---