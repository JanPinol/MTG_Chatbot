##### DONE 1-Cuanto cuesta esta carta? COSTE MANA
##### DONE 2-Cuanto vale esta carta? VALOR PRECIO DINERO
##### DONE 3-De que tipo es esta carta? TIPO DE CARTA
##### DONE 4-Cuales son las reglas de esta carta? TEXTO REGLAS HABILIDADES
#5-Dame una imagen de esta carta. IMAGEN FOTO
#6-¿Qué colores tiene "Niv-Mizzet, Parun"?
##### DONE 7-¿Qué es la habilidad de "Deathtouch"? habilidades
##### DONE 8-Explícame cómo funciona "Flash". mecanicas
#9-Dime una carta roja
#10-Creame un mazo verde
#11-tiene x carta alguna norma especial?
#12- cuanto ataque tiene esta carta o defensa
#13- es legal esta carta? se puede usar?
#14- Dime los modos de juego de magic
#15-Que tipo de tierras/criaturas/artefactos/encantamientos hay
#16- Que habilidades tiene X carta?
#17- ¿Puedes darme un ejemplo de una carta con "Trample"?
##### DONE #18- En que consite un turno en magic?
##### DONE #19- cuantas cartas suele tener un mazo (lo tendriamos que definir
##### DONE #20 - En que momento se usa un instantaneo?
##### DONE #21 - Que cartas comunes valen más de 10 euros?
##### DONE #22 - Cual es la carta mas cara de Modern Horizons 2?
##### DONE #23 - Cual fué la primera carta de Eldrazi?
##### DONE #24 - Cuantas ediciones tiene Sol Ring?
##### DONE #25 - Hazme una lista de los contrahechizos azules mas jugados

import numpy
import spacy
import thinc
import re
import requests
from definiciones import definiciones_mtg
import time

print("NumPy version:", numpy.__version__)
print("spaCy version:", spacy.__version__)
print("Thinc version:", thinc.__version__)
nlp = spacy.load("es_core_news_md")

# Mapa de símbolos, lo que hace esto es que la api te devuelve el coste de mana o acciones de esta forma {T} {U}, esto sustituye estas cosas por simbolos
#o numeros sin los corchetes, si hay alguno que falta, ponedlo, la web desde donde se pillan es esta
#https://emojipedia.org/large-red-circle
SYMBOL_MAP = {
    "W": "⚪",
    "U": "🔵",
    "B": "⚫",
    "R": "🔴",
    "G": "🟢",
    "C": "◇",
    "T": "↻",
    "X": "X",
    # números de 0 a 20, por ejemplo:
    **{str(i): str(i) for i in range(0, 21)}
}

#cambiar el texto por los simbolos
def reemplazar_simbolos(texto: str) -> str:
    def _repl(m):
        clave = m.group(1)  # el contenido dentro de {}
        return SYMBOL_MAP.get(clave, m.group(0))
    return re.sub(r"\{([WUBRGCTX0-9]+)\}", _repl, texto)


# Pregunta 5: Busca en la api la carta y devuelve la imagen
def obtener_imagen_carta(nombre_carta):
    response = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={nombre_carta}")
    if response.status_code == 200:
        datos = response.json()
        return datos['image_uris']['normal']
    return "No se encontró la imagen de la carta."


# Pregunta 6: Busca en la api la carta y devuelve el coste de mana
def obtener_colores_carta(nombre_carta):
    response = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={nombre_carta}")
    if response.status_code == 200:
        datos = response.json()
        return datos['colors']  # ['U', 'R'] por ejemplo
    return "No se pudo determinar el color de la carta."


# Pregunta 9: Busca una carta aleatoria de un color específico
def carta_aleatoria_color(color):
    response = requests.get(f"https://api.scryfall.com/cards/random?q=color={color.lower()}")
    if response.status_code == 200:
        datos = response.json()
        return datos['name']
    return "No se encontró una carta de ese color."


# Pregunta 10: Crea un mazo de cartas de un color específico
def crear_mazo_color(color, cantidad=10):  # 10, ya que 40 tardaria demasiado
    mazo = []
    for _ in range(cantidad):
        carta = carta_aleatoria_color(color)
        mazo.append(carta)
    return mazo


# Pregunta 11: Busca en la api si la carta tiene alguna habilidad especial
def buscar_habilidad_en_carta(nombre_carta):
    response = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={nombre_carta}")
    if response.status_code == 200:
        datos = response.json()
        texto = datos.get('oracle_text', '').upper()
        habilidades = [clave for clave in definiciones_mtg if clave in texto]
        return habilidades if habilidades else "No se encontraron habilidades especiales."
    return "Carta no encontrada."


# Pregunta 12: Busca en la api el ataque y defensa de la carta
def obtener_fuerza_defensa(nombre_carta):
    response = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={nombre_carta}")
    if response.status_code == 200:
        datos = response.json()
        return f"Ataque: {datos.get('power', '?')}, Defensa: {datos.get('toughness', '?')}"
    return "Carta no encontrada."


# Pregunta 13: Busca en la api si la carta es legal en un formato
def es_legal(nombre_carta, formato="commander"):
    response = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={nombre_carta}")
    if response.status_code == 200:
        datos = response.json()
        legalidad = datos.get('legalities', {})
        return f"Legal en {formato}: {legalidad.get(formato, 'desconocido')}"
    return "Carta no encontrada."


# busca en la api la carta en especifico
def get_card_info(card_name):
    url = f"https://api.scryfall.com/cards/named?fuzzy={card_name}"
    response = requests.get(url)
    if response.status_code == 200 and response.json().get("object") == "card":
        return response.json()
    return None


# busca en la api el set en especifico y devuelve la primera carta que tenga valor
def get_set_info(url):
    print(url)
    response = requests.get(url).json()
    for card in response.get("data", []):
        price = card.get("prices", {}).get("eur")
        if price:
            return card["name"], price
    return None, None


# se dedica a revisar sinonimos de las palabras, se puede cambiar el nivel de sinonimo cambiando el valor de rango
def check_word(palabras, tokens, rango):
    kw_lemmas = {nlp(w)[0].lemma_.lower() for w in palabras}
    for tok in tokens:
        if tok.lemma_.lower() in kw_lemmas:
            return True

    palabra_tokens = [nlp(w)[0] for w in palabras]
    for pt in palabra_tokens:
        for tok in tokens:
            # print para ver la similitud que sale
            # print(f"[VECTOR MATCH] palabra clave «{pt.text}» ≃ token «{tok.text}» ({pt.similarity(tok):.2f})")
            if pt.has_vector and tok.has_vector and pt.similarity(tok) >= rango:
                return True
    return False


def extraer_nombre_carta(pregunta):
    doc = nlp(pregunta)

    # Primer Metodo, usamos Spacy para encontrar nombres de entidades y enviarselo a la api, si la api responde bien, devolvemos
    for ent in doc.ents:
        nombre = ent.text.strip()
        if get_card_info(nombre):
            print("Primero")
            return nombre

    # Segundo Metodo, buscamos conjuntos de palbras conspacy que tengan algun nombre y lo buscamos, quitamos cosas como el la y tal
    for chunk in reversed(list(doc.noun_chunks)):
        # descartamos chunks sin PROPN
        if not any(tok.pos_ == "PROPN" for tok in chunk):
            continue
        # limpiamos artículos y determinantes
        nombre = re.sub(
            r"\b(el|la|los|las|un|una|unos|unas|de|del|al)\b",
            "",
            chunk.text,
            flags=re.IGNORECASE
        ).strip()
        if 3 <= len(nombre) <= 60 and get_card_info(nombre):
            return nombre

    # 3) Tercer metodo: prueba a hacer combinaciones con las 3 ultimas palabras enviadas
    palabras = [tok.text for tok in doc if tok.is_alpha and not tok.is_stop]
    # probamos pares y tríos
    for size in (3, 2):
        for i in range(len(palabras) - size + 1, 0, -1):
            candidate = " ".join(palabras[i:i + size])
            if get_card_info(candidate):
                print("Tercero")
                return candidate

    return None


# se encarga de pedir cosas a la api sobre el set de cartas
def set_respond(codigo, tokens):
    if check_word(["caro"], tokens, 0.70):
        url = f"https://api.scryfall.com/cards/search?q=set:{codigo}&order=eur&dir=desc"
        descripcion, valor = get_set_info(url)
        if descripcion is None or valor is None:
            return f"No hay informacion disponible sobre este set"
        return f"La carta mas cara de este set es {descripcion} con un valor de: {valor}"
    elif check_word(["barato"], tokens, 0.70):
        url = f"https://api.scryfall.com/cards/search?q=s%3A{codigo}&order=eur&dir=asc"
        descripcion, valor = get_set_info(url)
        if descripcion is None or valor is None:
            return f"No hay informacion disponible sobre este set"
        return f"La carta mas barata de este set es {descripcion} con un valor de: {valor}"
    else:
        return 0
    # ///////////////////////////////////PRINTAR SOLUCIONES


# se dedica a pedir a la api sobre una carta y tratar los datos
def card_respond(campo, descripcion, pregunta):
    # Extraer y validar nombre de la carta SI ES NECESARIO
    nombre = extraer_nombre_carta(pregunta)
    if not nombre:
        return "No pude identificar un nombre de carta válido. ¿Podrías escribirlo exacto o más completo?"

    # /////////////////////////////////Consultar la API (se ha de mejorar por cada tipo de pregunta
    card = get_card_info(nombre)
    if not card:
        return f"No encontré la carta «{nombre}». Asegúrate de escribir bien el nombre."

    # ///////////////////////////////////PRINTAR SOLUCIONES
    if campo == "image_uris":
        return f"{descripcion}: {card['image_uris']['normal']}"
    if campo == "eur":
        return f"{descripcion}: {card['prices']['eur']}"
    if campo in card:
        return f"{descripcion}: {card[campo]}"
    return "No encontré esa información específica en la carta."


# se encarga de responder la pregunta que han echo
def responder_pregunta(pregunta):
    pregunta = pregunta.lower()
    doc = nlp(pregunta)
    # esto filtra las comas y signos de puntuacion, se le puede añadir la linea comentada pero quitara algunos verbos, cosa que para preguntas con
    # "hacer" lo rompe,
    tokens = [token for token in doc if token.is_alpha]  # and not token.is_stop

    # ver si se esta hablando de un set
    resp = requests.get("https://api.scryfall.com/sets").json()
    for s in resp.get("data", []):
        if s["name"].lower() in pregunta:
            print("yes")
            texto = set_respond(s["code"], tokens)
            if texto != 0:
                return texto

    # este primer for es para ver si pide algo de una key de nuestro diccionario, recorre el diccionario por cada palabra
    # Ver si esta hablando de una key

    # Preguntas 7, 8
    for palabra in definiciones_mtg:
        if palabra.lower() in pregunta or palabra.lower().replace("-", " ") in pregunta:
            return f"{palabra.title()}: {definiciones_mtg[palabra]}"

    # aqui las preguntas normales sobre cartas

    # Pregunta 1: Coste de maná de la carta
    if check_word(["mana", "coste"], tokens, 0.5):
        campo = "mana_cost"
        descripcion = "El coste de maná de la carta es"

    # Pregunta 2: Precio en euros de la carta
    elif check_word(["precio", "cuesta", "vale", "dinero", "vender"], tokens, 0.5):
        campo = "eur"
        descripcion = "El precio de la carta en euros es"

    # Pregunta 3: Tipo de la carta
    elif check_word(["tipo", "clase", "categoria"], tokens, 0.5):
        campo = "type_line"
        descripcion = "La categoria de la carta es"

    # Pregunta 4: Reglas de la carta
    elif check_word(["texto", "instrucciones", "efecto", "descripcion", "hacer", "cara"], tokens, 0.5):
        campo = "oracle_text"
        descripcion = "El efecto de esta carta es el siguiente"

    # Pregunta 5 - Imagen de la carta
    elif check_word(["imagen", "foto"], tokens, 0.7):
        nombre = extraer_nombre_carta(pregunta)
        if nombre:
            return obtener_imagen_carta(nombre)
        else:
            return "No pude encontrar el nombre de la carta para mostrarte la imagen."

    # Pregunta 6 - Colores de la carta
    elif check_word(["color", "colores"], tokens, 0.7):
        nombre = extraer_nombre_carta(pregunta)
        if nombre:
            colores = obtener_colores_carta(nombre)
            if isinstance(colores, list):
                return f"La carta tiene los colores: {', '.join(colores)}"
            else:
                return colores
        else:
            return "No pude determinar el nombre de la carta para darte sus colores."

    # Preguntas 7 y 8 ya se responden antes

    # Pregunta 9 - Carta roja
    elif "carta roja" in pregunta:
        return f"Una carta roja aleatoria: {carta_aleatoria_color('red')}"

    # Pregunta 10 - Mazo verde
    elif "mazo verde" in pregunta:
        mazo = crear_mazo_color("green")
        return "Aquí tienes un mazo verde:\n" + "\n".join(mazo)

    # Pregunta 11 - ¿Tiene alguna norma especial?
    elif check_word(["norma especial", "habilidad especial"], tokens, 0.7):
        nombre = extraer_nombre_carta(pregunta)
        if nombre:
            habilidades = buscar_habilidad_en_carta(nombre)
            if isinstance(habilidades, list):
                return f"La carta tiene las siguientes habilidades: {', '.join(habilidades)}"
            else:
                return habilidades
        else:
            return "No encontré el nombre de la carta."

    # Pregunta 12 - Ataque o defensa
    elif check_word(["ataque", "fuerza", "defensa", "resistencia"], tokens, 0.7):
        nombre = extraer_nombre_carta(pregunta)
        if nombre:
            return obtener_fuerza_defensa(nombre)
        else:
            return "No encontré el nombre de la carta."

    # Pregunta 13 - Legalidad
    elif check_word(["legal", "permitida", "usar"], tokens, 0.7):
        nombre = extraer_nombre_carta(pregunta)
        if nombre:
            return es_legal(nombre)
        else:
            return "No encontré el nombre de la carta para decirte si es legal."

    # Pregunta 21: Pregunta a la api sobre cartas comunes que valen más de 10 euros
    elif (check_word(["comunes", "común", "common"], tokens, 0.7) and
          ("más de 10 euros" in pregunta or "mayor a 10 euros" in pregunta or "valen más de 10 euros" in pregunta)):
        url = "https://api.scryfall.com/cards/search?q=rarity:common+eur>10"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            cards = data.get("data", [])
            if not cards:
                return "No hay cartas comunes que valgan más de 10 euros."
            # Listar las primeras 3 cartas y su precio para no saturar la respuesta
            result_lines = []
            for card in cards[:11]:
                name = card.get("name")
                price = card.get("prices", {}).get("eur")
                if name and price:
                    result_lines.append(f"{name}: {price}€")
            return "Cartas comunes que valen más de 10 euros:\n" + "\n".join(result_lines)
        else:
            return "Hubo un problema al consultar la API de Scryfall."

    # Pregunta 23: Pregunta a la api sobre la primera carta de Eldrazi
    elif check_word(["eldrazi"], tokens, 0.7) and check_word(["primera", "primero", "inicial"], tokens, 0.6):
        url = "https://api.scryfall.com/cards/search?q=type:eldrazi&order=released&dir=asc"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            cards = data.get("data", [])
            if cards:
                first_card = cards[0]
                name = first_card.get("name", "Desconocida")
                released = first_card.get("released_at", "sin fecha")
                set_name = first_card.get("set_name", "set desconocido")
                return f"La primera carta Eldrazi fue «{name}», publicada el {released} en el set {set_name}."
            else:
                return "No se encontró ninguna carta del tipo Eldrazi."
        else:
            return "Hubo un problema al consultar la API de Scryfall."

    # Pregunta 24: Pregunta a la api sobre el número de ediciones de Sol Ring
    elif (check_word(["sol ring"], tokens, 0.7) and
          check_word(["cuantas", "numero", "versiones", "ediciones"], tokens,0.6)):
        carta = get_card_info("Sol Ring")
        if carta and "prints_search_uri" in carta:
            prints_url = carta["prints_search_uri"]
            total = 0
            next_page = prints_url
            while next_page:
                resp = requests.get(next_page).json()
                total += len(resp.get("data", []))
                next_page = resp.get("next_page", None)
            return f"«Sol Ring» tiene un total de {total} ediciones distintas registradas en Scryfall."
        else:
            return "No pude obtener la información sobre Sol Ring desde la API."

    # Pregunta 25: Pregunta a la api sobre los contrahechizos azules
    elif check_word(["counterspell", "contrarrestar", "anular", "contrahechizo"], tokens, 0.6) and check_word(
            ["azul", "azules"], tokens, 0.6):
        url = "https://api.scryfall.com/cards/search?q=o%3Acounter+c%3Au&order=edhrec"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            cards = data.get("data", [])[:10]
            if cards:
                nombres = [card["name"] for card in cards]
                return "Aquí tienes una lista de los counterspells azules más populares:\n- " + "\n- ".join(nombres)
            else:
                return "No encontré counterspells azules populares en la base de datos."
        else:
            return "Ocurrió un error al consultar la API de Scryfall."

    else:
        return "No entendí tu pregunta."

    return card_respond(campo, descripcion, pregunta)


# Ejemplo de uso en modo interactivo
if __name__ == "__main__":
    while True:
        pregunta_usuario = input("Tú: ")
        if pregunta_usuario.lower().strip() in ("salir", "exit", "quit"):
            print("Bot: ¡Hasta luego!")
            break
        print("Bot:", reemplazar_simbolos(responder_pregunta(pregunta_usuario)))