##### DONE 1-Cuanto cuesta esta carta? COSTE MANA
##### DONE 2-Cuanto vale esta carta? VALOR PRECIO DINERO
##### DONE 3-De que tipo es esta carta? TIPO DE CARTA *no me va*
##### DONE 4-Cuales son las reglas de esta carta? TEXTO REGLAS HABILIDADES
##### DONE 5-Dame una imagen de esta carta. IMAGEN FOTO
##### DONE 6-¿Qué colores tiene "Niv-Mizzet, Parun"?
##### DONE 7-¿Qué es la habilidad de "Deathtouch"? habilidades
##### DONE 8-Explícame cómo funciona "Flash". mecanicas
##### DONE 9-Dime una carta roja
##### DONE 10-Creame un mazo verde
##### DONE 11-tiene x carta alguna norma especial?
##### DONE 12- cuanto ataque tiene esta carta o defensa
##### DONE 13- es legal esta carta? se puede usar? *peta en nombres compuestos*
##### DONE 14- Dime los modos de juego de magic
##### DONE 15-Que tipo de tierras/criaturas/artefactos/encantamientos hay *no me va*
##### DONE 16- Que habilidades tiene X carta?
##### DONE 17- ¿Puedes darme un ejemplo de una carta con "Trample"? *no me va, me explica la mecanica no me da la carta*
##### DONE #18- En que consite un turno en magic?
##### DONE #19- cuantas cartas suele tener un mazo (lo tendriamos que definir
##### DONE #20 - En que momento se usa un instantaneo? *no me va*
##### DONE #21 - Que cartas comunes valen más de 10 euros? *no me va*
##### DONE #22 - Cual es la carta mas cara de Modern Horizons 2?
##### DONE #23 - Cual fué la primera carta de Eldrazi?
##### DONE #24 - Cuantas ediciones tiene Sol Ring?
##### DONE #25 - Hazme una lista de los contrahechizos azules mas jugados
from __future__ import annotations
import re
from typing import List, Optional
import requests
import spacy
from definiciones import definiciones_mtg

nlp = spacy.load("es_core_news_md")  # NLP model

# ---------------------------------------------------------------------------
# 1· Tablas de traducción y utilidades
# ---------------------------------------------------------------------------
SYMBOL_MAP = {"W":"⚪","U":"🔵","B":"⚫","R":"🔴","G":"🟢","C":"◇","T":"↻","X":"X", **{str(i):str(i) for i in range(21)}}
COLOR_MAP = {"W":"Blanco","U":"Azul","B":"Negro","R":"Rojo","G":"Verde","C":"Incoloro"}
TIPO_MAP = {"tierras":"land-types","criaturas":"creature-types","artefactos":"artifact-types","encantamientos":"enchantment-types"}

def reemplazar_simbolos(texto: str) -> str:
    """Sustituye {X} por emoji."""
    return re.sub(r"\{([WUBRTCX0-9]+)\}", lambda m: SYMBOL_MAP.get(m.group(1), m.group(0)), texto)

# ---------------------------------------------------------------------------
# 2· API helpers
# ---------------------------------------------------------------------------

def get_card_info(nombre: str) -> Optional[dict]:
    """Devuelve carta en ES o EN."""
    for lang in ("es","en"):
        r = requests.get(f"https://api.scryfall.com/cards/named?fuzzy={nombre}&lang={lang}")
        if r.status_code == 200 and r.json().get("object")=="card":
            return r.json()
    return None

def obtener_imagen_carta(nombre: str) -> str:
    c = get_card_info(nombre)
    return c["image_uris"]["normal"] if c else "No se encontró la imagen."

def obtener_colores_carta(nombre: str) -> str:
    c = get_card_info(nombre)
    if not c: return "Carta no encontrada."
    cols = c.get("colors",[]) or ["C"]
    return ", ".join(COLOR_MAP.get(x,x) for x in cols)

# Funciones de ejemplo/mazo

def carta_aleatoria_color(color: str) -> str:
    r = requests.get(f"https://api.scryfall.com/cards/random?q=color={color}")
    return r.json().get("name","¿?") if r.status_code==200 else "Error de conexión."

def crear_mazo_color(color: str, n:int=10) -> List[str]:
    return [carta_aleatoria_color(color) for _ in range(n)]

# Datos de carta

def listar_habilidades_carta(nombre: str) -> List[str]:
    c = get_card_info(nombre)
    if not c: return []
    txt = c.get("oracle_text","" ).lower()
    return [h for h in definiciones_mtg if h.lower() in txt]

def obtener_fuerza_defensa(nombre: str) -> str:
    c = get_card_info(nombre)
    return f"Ataque: {c.get('power','?')}, Defensa: {c.get('toughness','?')}" if c else "Carta no encontrada."

def es_legal(nombre: str, formato:str="commander") -> str:
    c = get_card_info(nombre)
    return f"Legal en {formato}: {c.get('legalities',{{}}).get(formato,'desconocido')}" if c else "Carta no encontrada."

# ---------------------------------------------------------------------------
# 3· NLP helpers
# ---------------------------------------------------------------------------

def check_word(palabras:List[str], tokens, thr:float) -> bool:
    lem = {nlp(p)[0].lemma_.lower() for p in palabras}
    for t in tokens:
        if t.lemma_.lower() in lem: return True
    pv = [nlp(p)[0] for p in palabras]
    return any(pt.has_vector and tok.has_vector and pt.similarity(tok)>=thr
               for pt in pv for tok in tokens)

def extraer_nombre_carta(texto:str) -> Optional[str]:
    doc = nlp(texto)
    for ent in doc.ents:
        if get_card_info(ent.text): return ent.text
    for chunk in reversed(list(doc.noun_chunks)):
        if any(t.pos_=="PROPN" for t in chunk):
            nombre = re.sub(r"\b(el|la|los|las|un|una|unos|unas|de|del|al)\b","",chunk.text,flags=re.I).strip()
            if get_card_info(nombre): return nombre
    return None

# ---------------------------------------------------------------------------
# 4· Respuestas estáticas (#18-20)
# ---------------------------------------------------------------------------
TEXTO_TURNO = (
    "Un turno se divide en cinco fases:\n"
    "1. Enderezar\n2. Mantenimiento\n3. Fase principal\n4. Combate\n5. Segunda fase principal y limpieza."
)
TEXTO_TAMANIO_MAZO = (
    "Tamaños habituales de mazo:\n"
    "• Construido: 60 cartas mín.\n"
    "• Limitado: 40 cartas mín.\n"
    "• Commander: 100 + comandante."
)
TEXTO_INSTANTANEO = (
    "Un instantáneo puede lanzarse siempre que tengas prioridad — incluso como respuesta a otro hechizo."
)

# ---------------------------------------------------------------------------
# 5· Dispatcher principal (preguntas 1-25)
# ---------------------------------------------------------------------------
def responder_pregunta(pregunta:str) -> str:
    low = pregunta.lower()
    tokens = [t for t in nlp(low) if t.is_alpha]

    # 1-6: propiedades básicas de carta
    if check_word(["mana","coste"], tokens,0.5):
        nom=get_card_info(extraer_nombre_carta(low))
        return reemplazar_simbolos(nom["mana_cost"]) if nom else "Carta no encontrada."
    if check_word(["precio","vale","cuesta"],tokens,0.5):
        nom=get_card_info(extraer_nombre_carta(low))
        return f"{nom['prices']['eur']}€" if nom else "Carta no encontrada."
    if check_word(["tipo","categoria"],tokens,0.5):
        nom=get_card_info(extraer_nombre_carta(low))
        return nom.get("printed_type_line") or nom.get("type_line","?") if nom else "Carta no encontrada."
    if check_word(["texto","efecto","regla"],tokens,0.5):
        nom=get_card_info(extraer_nombre_carta(low))
        txt = nom.get("printed_text") or nom.get("oracle_text","?") if nom else None
        return reemplazar_simbolos(txt) if txt else "Carta no encontrada."
    if check_word(["imagen","foto"],tokens,0.7):
        return obtener_imagen_carta(extraer_nombre_carta(low))
    if check_word(["color","colores"],tokens,0.7):
        return obtener_colores_carta(extraer_nombre_carta(low))

    # 7-8: definiciones de habilidades/mechanics
    for hab in definiciones_mtg:
        if hab.lower() in low or hab.lower().replace('-',' ') in low:
            return f"{hab.title()}: {definiciones_mtg[hab]}"

    # 9-10: ejemplos y mazos
    if "carta roja" in low:
        return "Ejemplo de carta roja: " + carta_aleatoria_color("red")
    if "mazo verde" in low:
        return "Mazo verde:\n" + "\n".join(crear_mazo_color("green"))

    # 11-13: normas, stats y legalidad
    if check_word(["norma especial","habilidad especial"],tokens,0.7):
        return ", ".join(listar_habilidades_carta(extraer_nombre_carta(low))) or "No se encontraron habilidades."
    if check_word(["ataque","fuerza","defensa"],tokens,0.7):
        return obtener_fuerza_defensa(extraer_nombre_carta(low))
    if check_word(["legal","permitida","usar"],tokens,0.7):
        return es_legal(extraer_nombre_carta(low))

    # 14-17: formatos, subtipos y trample
    if check_word(["modo","modos","formato","formatos"],tokens,0.7):
        return "Construido, Limitado, Commander, Pauper, Brawl, etc."
    for k,e in TIPO_MAP.items():
        if k in low:
            return ", ".join(requests.get(f"https://api.scryfall.com/catalog/{e}").json().get("data",[])[:30])
    if ("trample" in low or "arrollar" in low) and "carta" in low:
        return requests.get("https://api.scryfall.com/cards/random?q=o:trample").json().get("name","?")

    # 18-20: respuestas estáticas
    if "turno" in low:       return TEXTO_TURNO
    if "cartas" in low and ("cuantas" in low or "cuántas" in low): return TEXTO_TAMANIO_MAZO
    if "instantáneo" in low and "cuando" in low: return TEXTO_INSTANTANEO

    # 21-25: búsquedas avanzadas
    if "comunes" in low and ("10" in low or "diez" in low):
        data=requests.get("https://api.scryfall.com/cards/search?q=rarity:common+eur>10").json().get("data",[])
        return "Comunes >10€:\n- " + "\n- ".join(f"{c['name']}: {c['prices']['eur']} €" for c in data[:10] if c['prices']['eur'])
    if "modern horizons 2" in low or "modern horizons ii" in low:
        card=requests.get("https://api.scryfall.com/cards/search?q=set:mh2+order:eur+dir:desc").json().get("data",[])[0]
        return f"La carta más cara de MH2 es «{card['name']}» con {card['prices']['eur']} €."
    if "eldrazi" in low and ("primera" in low or "primero" in low):
        c=requests.get("https://api.scryfall.com/cards/search?q=type:eldrazi&order=released&dir=asc").json().get("data",[])[0]
        return f"La primera Eldrazi es «{c['name']}», publicada el {c.get('released_at','?')}."
    if "sol ring" in low and any(w in low for w in ["ediciones","versiones","cuantas","número"]):
        base=get_card_info("Sol Ring"); total=0; nxt=base.get("prints_search_uri")
        while nxt:
            j=requests.get(nxt).json(); total+=len(j.get("data",[])); nxt=j.get("next_page")
        return f"Sol Ring tiene {total} ediciones en Scryfall."
    if any(w in low for w in ["counterspell","contrarrestar","contrahechizo"]) and "azul" in low:
        data=requests.get("https://api.scryfall.com/cards/search?q=o:counter+c:u&order=edhrec").json().get("data",[])[:10]
        return "Counterspells azules más usados:\n- " + "\n- ".join(c['name'] for c in data)

    return "No entendí tu pregunta."

# ---------------------------------------------------------------------------
# 5 · Función main y loop interactivo
# ---------------------------------------------------------------------------
def main() -> None:
    # tu bucle interactivo, por ejemplo:
    print("Chatbot MTG operativo (Escribe 'salir' para terminar')")
    while True:
        q = input("Tú: ")
        if q.lower().strip() in ("salir", "exit", "quit"):
            print("Bot: ¡Hasta luego!")
            break
        print("Bot:", responder_pregunta(q))

if __name__ == "__main__":
    main()
