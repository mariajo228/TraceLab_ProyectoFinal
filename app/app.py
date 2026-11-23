import random
import time
from pathlib import Path
from datetime import datetime
from uuid import uuid4

import pandas as pd
import streamlit as st
from PIL import Image

from comparador import categoria, comparar, superposicion
from procesamiento import CSV_DIVISION, DATASET, NIVELES, TIEMPOS


# ---------------------------------------------------------
# 1. CONFIGURACIÓN GENERAL
# ---------------------------------------------------------

NOMBRES_NIVEL = {
    "facil": "Fácil",
    "intermedio": "Intermedio",
    "dificil": "Difícil"
}

NOMBRES_MOD = {
    "mandalas": "Mandalas",
    "siluetas": "Siluetas"
}

st.set_page_config(
    page_title="TraceLab | Memoria visual",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ---------------------------------------------------------
# 2. ESTILOS VISUALES
# ---------------------------------------------------------

st.markdown("""
<style>
:root{--ivory:#F6F1E9;--paper:#FFFCF7;--plum:#492C52;--plum2:#684574;--violet:#876A91;--lav:#DCCCE8;--terra:#BC735B;--ink:#302633;--muted:#827782;--line:#E9DFE8;}
.stApp{background:radial-gradient(circle at 8% 12%,rgba(220,204,232,.34),transparent 28%),radial-gradient(circle at 92% 42%,rgba(188,115,91,.10),transparent 25%),var(--ivory);color:var(--ink)}
.block-container{max-width:1180px;padding-top:2rem;padding-bottom:4rem}
[data-testid="stHeader"]{background:transparent}#MainMenu,footer{visibility:hidden}
.trace-header{display:flex;align-items:center;justify-content:space-between;padding:23px 30px;margin:4px 0 30px;background:rgba(255,252,247,.96);border:1px solid var(--line);border-radius:22px;box-shadow:0 12px 35px rgba(73,44,82,.07)}
.trace-brand{color:var(--plum);font-size:29px;font-weight:850;letter-spacing:-1.4px}.trace-subbrand{color:var(--muted);font-size:10px;letter-spacing:1.8px;margin-top:5px}.trace-pill{background:#F0E7F2;color:var(--plum);padding:11px 18px;border-radius:40px;font-size:10px;letter-spacing:1.2px;font-weight:800}
h1,h2,h3{color:var(--ink)!important;letter-spacing:-.8px}h1{font-weight:850!important}h2,h3{font-weight:780!important}p{color:#716673;line-height:1.75}
.stepper{display:flex;justify-content:center;gap:9px;flex-wrap:wrap;margin:8px 0 32px}.step{background:#EAE3EA;color:#887B89;padding:10px 16px;border-radius:40px;font-size:11px;font-weight:750;letter-spacing:.2px}.step.active{background:var(--plum);color:white;box-shadow:0 5px 15px rgba(73,44,82,.18)}
.hero-card{position:relative;isolation:isolate;overflow:hidden;background:linear-gradient(118deg,#492C52 0%,#684574 60%,#876A91 100%);padding:45px 46px;border-radius:30px;color:white;box-shadow:0 22px 55px rgba(73,44,82,.19);margin:12px 0 38px;min-height:330px}
.hero-card:after{content:"";position:absolute;z-index:-1;width:340px;height:340px;right:-95px;top:-80px;border-radius:50%;border:1px solid rgba(255,255,255,.24);box-shadow:0 0 0 22px rgba(255,255,255,.035),0 0 0 48px rgba(255,255,255,.035),0 0 0 78px rgba(255,255,255,.025)}
.hero-card h1{color:white!important;font-size:clamp(35px,4.4vw,56px);line-height:1.08;max-width:650px;margin:20px 0}.hero-card p{color:#F4EAF4!important;font-size:15px;line-height:1.85;max-width:590px}.hero-tag{display:inline-block;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.3);color:white!important;padding:9px 15px;border-radius:40px;font-size:10px;letter-spacing:1.5px;font-weight:800}
.hero-layout{display:grid;grid-template-columns:1.25fr .75fr;align-items:center;gap:24px}.hero-art{display:flex;align-items:center;justify-content:center;min-height:230px}.hero-art svg{width:min(100%,290px);height:auto;filter:drop-shadow(0 14px 20px rgba(20,10,25,.16))}
.info-card{background:var(--paper);border:1px solid var(--line);border-radius:22px;padding:25px;min-height:155px;box-shadow:0 8px 25px rgba(73,44,82,.055);transition:transform .25s ease,box-shadow .25s ease}.info-card:hover{transform:translateY(-4px);box-shadow:0 16px 35px rgba(73,44,82,.11);border-color:#D5C0DC}.info-card h3{color:var(--plum)!important;font-size:18px;margin:8px 0 10px}.info-card p{color:var(--muted);font-size:13px;line-height:1.7;margin-bottom:0}
.art-card{background:var(--paper);border:1px solid var(--line);border-radius:24px;padding:22px;min-height:300px;box-shadow:0 8px 25px rgba(73,44,82,.055)}.art-card .art-visual{height:145px;border-radius:17px;display:flex;align-items:center;justify-content:center;margin-bottom:18px;overflow:hidden;background:linear-gradient(135deg,#EEE3F0,#F8EEE5)}.art-card .art-visual svg{height:135px;width:100%}.art-card h3{color:var(--plum)!important;margin:4px 0 8px}.art-card p{font-size:13px;color:var(--muted);line-height:1.65}
.level-card{background:var(--paper);border:1px solid var(--line);border-radius:22px;padding:25px 22px;min-height:190px;box-shadow:0 8px 25px rgba(73,44,82,.055)}.level-number{font-size:11px;letter-spacing:1.6px;color:var(--terra);font-weight:850}.level-time{display:inline-block;margin-top:12px;padding:7px 12px;border-radius:30px;background:#F0E7F2;color:var(--plum);font-size:11px;font-weight:800}
.stButton>button{border-radius:13px;min-height:47px;border:1px solid #DCCEDC;background:var(--paper);color:var(--plum)!important;font-weight:750;transition:all .22s ease}.stButton>button:hover{background:#F0E6F1;border-color:var(--violet);color:var(--plum)!important;transform:translateY(-2px)}
.stButton>button[kind="primary"],.stButton>button[data-testid="stBaseButton-primary"]{background:linear-gradient(110deg,#492C52,#795586)!important;color:white!important;border:0!important;box-shadow:0 7px 18px rgba(73,44,82,.19)}.stButton>button[kind="primary"] *, .stButton>button[data-testid="stBaseButton-primary"] *{color:white!important;fill:white!important}.stButton>button[kind="primary"]:hover,.stButton>button[data-testid="stBaseButton-primary"]:hover{background:linear-gradient(110deg,#39213F,#65436F)!important;transform:translateY(-2px)}
[data-testid="stImage"] img{border-radius:18px;box-shadow:0 8px 24px rgba(73,44,82,.09)}[data-testid="stMetric"]{background:var(--paper);border:1px solid var(--line);border-radius:20px;padding:22px;box-shadow:0 7px 20px rgba(73,44,82,.05)}.stProgress>div>div>div{background:linear-gradient(90deg,var(--terra),var(--violet))}[data-testid="stFileUploader"]{background:var(--paper);border:1px dashed #B99CBF;border-radius:18px;padding:12px}hr{border-color:var(--line)}
[data-testid="stExpander"]{background:var(--paper);border:1px solid var(--line);border-radius:16px}
@media(max-width:768px){.block-container{padding-left:1rem;padding-right:1rem}.trace-header{padding:17px}.trace-brand{font-size:23px}.trace-pill{display:none}.hero-card{padding:30px 24px}.hero-layout{grid-template-columns:1fr}.hero-art{min-height:160px}.hero-art svg{width:190px}.hero-card h1{font-size:34px}.stepper{justify-content:flex-start}.art-card{min-height:unset}}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# 3. ESTADO DE LA SESIÓN
# ---------------------------------------------------------

for clave, valor in {
    "pantalla": "bienvenida",
    "modalidad": None,
    "nivel": None,
    "ref": None,
    "resultado": None
}.items():
    st.session_state.setdefault(clave, valor)


def ir(pantalla, **cambios):
    st.session_state.update(cambios)
    st.session_state.pantalla = pantalla
    st.rerun()


# ---------------------------------------------------------
# 4. FUNCIONES DE APOYO
# ---------------------------------------------------------

@st.cache_data
def cargar_retos():
    if not CSV_DIVISION.exists():
        return None

    df = pd.read_csv(CSV_DIVISION)
    return df[df["split"] == "reto"]


def elegir_reto(modalidad, nivel):
    retos = cargar_retos()

    if retos is None:
        st.error(
            "No se encontró division_dataset_v2.csv. "
            "Ejecuta scripts/generar_division.py (o la sección 2 del notebook)."
        )
        st.stop()

    rutas = retos[
        (retos["modalidad"] == modalidad) &
        (retos["nivel"] == nivel)
    ]["ruta"].tolist()

    if not rutas:
        st.error("No hay retos disponibles para esta combinación.")
        st.stop()

    return random.choice(rutas)


def encabezado():
    st.markdown("""
    <div class="trace-header">
        <div>
            <div class="trace-brand">🎨 TraceLab</div>
            <div class="trace-subbrand">
                MEMORIA VISUAL · ARTE · PERCEPCIÓN
            </div>
        </div>
        <div class="trace-pill">EXPERIENCIA INTERACTIVA</div>
    </div>
    """, unsafe_allow_html=True)


def indicador_pasos(pantalla):
    pasos = [
        ("bienvenida", "Inicio"),
        ("modalidad", "Modalidad"),
        ("dificultad", "Nivel"),
        ("observacion", "Observación"),
        ("carga", "Dibujo"),
        ("resultados", "Resultados")
    ]

    actual = [p[0] for p in pasos].index(pantalla)

    html = '<div class="stepper">'

    for i, (_, nombre) in enumerate(pasos):
        clase = "step active" if i <= actual else "step"
        html += f'<div class="{clase}">{i + 1}. {nombre}</div>'

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)


# ---------------------------------------------------------
# 5. ENCABEZADO Y NAVEGACIÓN
# ---------------------------------------------------------

pantalla = st.session_state.pantalla

encabezado()
indicador_pasos(pantalla)


# ---------------------------------------------------------
# 6. BIENVENIDA
# ---------------------------------------------------------

if pantalla == "bienvenida":

    st.markdown("""
    <div class="hero-card">
      <div class="hero-layout">
        <div>
          <div class="hero-tag">EXPLORA TU MEMORIA VISUAL</div>
          <h1>El arte de recordar lo que ves.</h1>
          <p>Observa formas, reconstruye patrones y descubre cómo tu memoria transforma lo visual. Una experiencia que une arte, percepción y creatividad.</p>
        </div>
        <div class="hero-art">
          <svg viewBox="0 0 300 300" role="img" aria-label="Mandala geométrico decorativo">
            <defs><linearGradient id="petal" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#F2D8C7"/><stop offset="1" stop-color="#D9B9E3"/></linearGradient></defs>
            <circle cx="150" cy="150" r="133" fill="none" stroke="#F4E8F2" stroke-opacity=".42" stroke-width="1.5"/>
            <circle cx="150" cy="150" r="112" fill="none" stroke="#E7C9B8" stroke-opacity=".9" stroke-width="2"/>
            <g transform="translate(150 150)" fill="url(#petal)" stroke="#F8EBDD" stroke-width="1.5">
              <g id="p"><path d="M0,-105 C34,-83 34,-48 0,-25 C-34,-48 -34,-83 0,-105Z"/></g>
              <use href="#p"/><use href="#p" transform="rotate(30)"/><use href="#p" transform="rotate(60)"/><use href="#p" transform="rotate(90)"/><use href="#p" transform="rotate(120)"/><use href="#p" transform="rotate(150)"/><use href="#p" transform="rotate(180)"/><use href="#p" transform="rotate(210)"/><use href="#p" transform="rotate(240)"/><use href="#p" transform="rotate(270)"/><use href="#p" transform="rotate(300)"/><use href="#p" transform="rotate(330)"/>
            </g>
            <circle cx="150" cy="150" r="48" fill="#BC735B" stroke="#F8EBDD" stroke-width="3"/><circle cx="150" cy="150" r="30" fill="none" stroke="#F8EBDD" stroke-width="2"/><circle cx="150" cy="150" r="10" fill="#F8EBDD"/>
            <g fill="#F6E9E4"><circle cx="150" cy="22" r="4"/><circle cx="278" cy="150" r="4"/><circle cx="150" cy="278" r="4"/><circle cx="22" cy="150" r="4"/></g>
          </svg>
        </div>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:12px;margin:0 0 18px;color:#BC735B;font-size:10px;font-weight:850;letter-spacing:2px;">
      <span>EL PROCESO CREATIVO</span><span style="height:1px;flex:1;background:#E2D5DF;"></span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Una experiencia en tres momentos")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="info-card"><div style="color:#BC735B;font-size:11px;font-weight:850;letter-spacing:1.5px">01 / OBSERVACIÓN</div><h3>Observa</h3><p>Memoriza una imagen y descubre sus formas, proporciones y pequeños detalles.</p></div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="info-card"><div style="color:#BC735B;font-size:11px;font-weight:850;letter-spacing:1.5px">02 / RECREACIÓN</div><h3>Reproduce</h3><p>Reconstruye lo que recuerdas a través de tu propio dibujo, a mano o digital.</p></div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="info-card"><div style="color:#BC735B;font-size:11px;font-weight:850;letter-spacing:1.5px">03 / DESCUBRIMIENTO</div><h3>Descubre</h3><p>Explora las coincidencias y diferencias entre la referencia y tu creación.</p></div>
        """, unsafe_allow_html=True)

    st.write("")
    if st.button("Comenzar experiencia →", type="primary", use_container_width=True):
        ir("modalidad")


# 7. SELECCIÓN DE MODALIDAD
# ---------------------------------------------------------

elif pantalla == "modalidad":

    st.markdown("## Elige tu lenguaje visual")
    st.write("Cada colección propone una forma distinta de observar, recordar y recrear.")
    st.write("")
    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown("""
        <div class="art-card">
          <div class="art-visual"><svg viewBox="0 0 320 150" aria-label="Composición de mandala">
            <g transform="translate(160 75)" stroke="#795586" stroke-width="1.5" fill="none">
              <circle r="65" stroke="#BC735B"/><circle r="48"/><circle r="27" stroke="#BC735B"/>
              <g id="petal2"><path d="M0,-62 C22,-42 22,-20 0,-8 C-22,-20 -22,-42 0,-62Z" fill="#DCCCE8"/></g>
              <use href="#petal2"/><use href="#petal2" transform="rotate(30)"/><use href="#petal2" transform="rotate(60)"/><use href="#petal2" transform="rotate(90)"/><use href="#petal2" transform="rotate(120)"/><use href="#petal2" transform="rotate(150)"/><use href="#petal2" transform="rotate(180)"/><use href="#petal2" transform="rotate(210)"/><use href="#petal2" transform="rotate(240)"/><use href="#petal2" transform="rotate(270)"/><use href="#petal2" transform="rotate(300)"/><use href="#petal2" transform="rotate(330)"/>
              <circle r="9" fill="#BC735B" stroke="none"/>
            </g></svg></div>
          <div style="font-size:10px;letter-spacing:1.7px;color:#BC735B;font-weight:850">COLECCIÓN 01</div>
          <h3>Mandalas</h3><p>Explora simetrías, geometría y patrones concéntricos. Un desafío para recordar la composición y sus detalles.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Explorar mandalas →", key="mod_mandalas", use_container_width=True):
            ir("dificultad", modalidad="mandalas")

    with c2:
        st.markdown("""
        <div class="art-card">
          <div class="art-visual"><svg viewBox="0 0 320 150" aria-label="Silueta abstracta">
            <circle cx="160" cy="75" r="62" fill="#E8D9E9"/><path d="M123 116 C132 96 130 82 120 68 C111 55 117 36 133 32 C145 29 154 38 155 49 C156 58 150 65 143 69 C155 76 165 84 171 99 L190 108 C198 113 193 123 183 123 L139 123 C130 123 119 123 123 116Z" fill="#684574"/><path d="M185 43 C203 49 215 64 214 83" stroke="#BC735B" stroke-width="4" stroke-linecap="round" fill="none"/><circle cx="215" cy="38" r="5" fill="#BC735B"/><path d="M92 112 Q105 98 115 108" stroke="#BC735B" stroke-width="2" fill="none"/></svg></div>
          <div style="font-size:10px;letter-spacing:1.7px;color:#BC735B;font-weight:850">COLECCIÓN 02</div>
          <h3>Siluetas</h3><p>Reconoce contornos y figuras. Concéntrate en la estructura general y en las características que hacen única cada forma.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Explorar siluetas →", key="mod_siluetas", use_container_width=True):
            ir("dificultad", modalidad="siluetas")

    st.write("")
    if st.button("← Volver al inicio"):
        ir("bienvenida")


# 8. SELECCIÓN DE DIFICULTAD
# ---------------------------------------------------------

elif pantalla == "dificultad":

    modalidad = st.session_state.modalidad
    st.markdown(f"## {NOMBRES_MOD[modalidad]} · Elige tu nivel")
    st.write("Ajusta el tiempo de observación al desafío que quieras experimentar.")
    columnas = st.columns(3, gap="medium")
    descripciones = {
        "facil": "Un primer acercamiento para activar tu memoria visual.",
        "intermedio": "Más detalles y formas que deberás recordar.",
        "dificil": "Un desafío mayor para tu percepción y memoria."
    }
    etiquetas = {"facil":"01 / INICIO", "intermedio":"02 / EXPLORACIÓN", "dificil":"03 / DESAFÍO"}
    for col, nivel in zip(columnas, NIVELES):
        with col:
            st.markdown(f"""
            <div class="level-card"><div class="level-number">{etiquetas[nivel]}</div><h3 style="margin-top:13px">{NOMBRES_NIVEL[nivel]}</h3><p>{descripciones[nivel]}</p><span class="level-time">◷ {TIEMPOS[nivel]} segundos</span></div>
            """, unsafe_allow_html=True)
            if st.button(f"Elegir {NOMBRES_NIVEL[nivel]} →", key=f"nivel_{nivel}", use_container_width=True):
                ir("observacion", nivel=nivel, ref=None)
    st.write("")
    if st.button("← Cambiar modalidad"):
        ir("modalidad")


# 9. OBSERVACIÓN DE LA IMAGEN
# ---------------------------------------------------------

elif pantalla == "observacion":

    nivel = st.session_state.nivel
    modalidad = st.session_state.modalidad
    segundos = TIEMPOS[nivel]

    st.markdown("## Prepárate para observar")

    st.write(
        f"Modalidad: **{NOMBRES_MOD[modalidad]}** · "
        f"Dificultad: **{NOMBRES_NIVEL[nivel]}**"
    )

    if st.session_state.ref is None:

        st.markdown("""
        <div class="info-card">
            <h3>🧠 Activa tu memoria visual</h3>
            <p>
                Cuando estés listo, pulsa el botón para revelar la imagen.
                Obsérvala con atención: desaparecerá cuando termine
                el tiempo disponible.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        if st.button(
            "Mostrar imagen",
            type="primary",
            use_container_width=True
        ):
            st.session_state.ref = elegir_reto(modalidad, nivel)
            st.rerun()

        if st.button("← Volver a dificultad"):
            ir("dificultad")

    else:

        espacio_img = st.empty()
        espacio_t = st.empty()

        espacio_img.image(
            Image.open(DATASET / st.session_state.ref),
            use_container_width=True,
            caption="Memoriza la imagen. El tiempo está corriendo."
        )

        for s in range(segundos, 0, -1):
            espacio_t.progress(
                s / segundos,
                text=f"Tiempo restante: {s} segundos"
            )
            time.sleep(1)

        espacio_img.empty()
        espacio_t.empty()

        ir("carga")



# ---------------------------------------------------------
# 10. CARGA DEL DIBUJO
# ---------------------------------------------------------

elif pantalla == "carga":

    st.markdown("## ¡Es tu turno de dibujar!")

    st.write(
        "Reproduce la imagen que acabas de observar. "
        "Puedes dibujar en papel o en digital y cargar el resultado."
    )

    st.markdown("""
    <div class="info-card">
        <h3>📷 Recomendaciones para tu imagen</h3>
        <p>
            • Utiliza buena iluminación si tomas una fotografía.<br>
            • Procura que el dibujo completo aparezca en el encuadre.<br>
            • Usa JPG, JPEG o PNG.<br>
            • Evita sombras fuertes y fondos con demasiados elementos.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    archivo = st.file_uploader(
        "Carga aquí tu dibujo",
        type=["jpg", "jpeg", "png"]
    )

    consentimiento = st.checkbox(
        "Autorizo que mi dibujo se almacene de forma anónima "
        "para las pruebas académicas del proyecto TraceLab."
    )

    if archivo is not None:

        st.markdown("### Vista previa de tu dibujo")

        st.image(
            archivo,
            caption="Imagen cargada",
            width=420
        )

        if st.button(
            "Analizar mi dibujo ✨",
            type="primary",
            use_container_width=True
        ):

            try:
                with st.spinner(
                    "Procesando las imágenes y calculando la similitud..."
                ):

                    res = comparar(
                        DATASET / st.session_state.ref,
                        archivo,
                        st.session_state.modalidad,
                        foto=True
                    )

                # -----------------------------------------
                # GUARDADO OPCIONAL DE DIBUJO Y METADATOS
                # -----------------------------------------

                if consentimiento:

                    # Carpeta de dibujos según modalidad
                    carpeta_dibujos = (
                        Path(DATASET)
                        / "dibujos_usuarios"
                        / st.session_state.modalidad
                    )
                    carpeta_dibujos.mkdir(
                        parents=True,
                        exist_ok=True
                    )

                    # Carpeta de resultados experimentales
                    carpeta_resultados = (
                        Path(DATASET).parent / "resultados"
                    )
                    carpeta_resultados.mkdir(
                        parents=True,
                        exist_ok=True
                    )

                    # Identificador anónimo
                    participante = (
                        f"p{uuid4().int % 100000000:08d}"
                    )

                    # Nombre basado en la imagen de referencia
                    nombre_original = Path(
                        st.session_state.ref
                    ).stem

                    extension = Path(archivo.name).suffix.lower()

                    if extension not in [".jpg", ".jpeg", ".png"]:
                        extension = ".jpg"

                    nombre_dibujo = (
                        f"{nombre_original}__{participante}{extension}"
                    )

                    ruta_dibujo = (
                        carpeta_dibujos / nombre_dibujo
                    )

                    # Guardar imagen original cargada
                    ruta_dibujo.write_bytes(archivo.getvalue())

                    # Obtener métricas del análisis
                    metricas = res["metricas"]

                    registro = {
                        "participante": participante,
                        "fecha": datetime.now().astimezone().isoformat(
                            timespec="seconds"
                        ),
                        "modalidad": st.session_state.modalidad,
                        "nivel": st.session_state.nivel,
                        "referencia": st.session_state.ref,
                        "archivo": nombre_dibujo,
                        "puntaje": res["puntaje"],
                        "categoria": categoria(res["puntaje"]),
                        "precision": metricas["precision"],
                        "cobertura": metricas["cobertura"],
                        "f_trazos": metricas["f_trazos"],
                        "chamfer_px": metricas["chamfer_px"],
                        "estructura": metricas["estructura"],
                        "consentimiento": True
                    }

                    ruta_csv = (
                        carpeta_resultados
                        / "registros_participantes.csv"
                    )

                    df_registro = pd.DataFrame([registro])

                    df_registro.to_csv(
                        ruta_csv,
                        mode="a",
                        header=not ruta_csv.exists(),
                        index=False,
                        encoding="utf-8"
                    )

                    st.success(
                        "Tu dibujo fue guardado de forma anónima. "
                        "¡Gracias por colaborar con las pruebas!"
                    )

                ir("resultados", resultado=res)

            except ValueError as e:
                st.error(str(e))

            except Exception as e:
                st.error(
                    f"Ocurrió un problema al procesar o guardar "
                    f"tu dibujo: {e}"
                )

    if st.button("← Volver al inicio"):
        ir("bienvenida")



# ---------------------------------------------------------
# 11. RESULTADOS DEL ANÁLISIS
# ---------------------------------------------------------

elif pantalla == "resultados":

    res = st.session_state.resultado
    p = res["puntaje"]

    st.markdown("## Tu resultado")

    st.write(
        "Este es el análisis visual de tu reproducción frente a la imagen "
        "de referencia."
    )

    st.write("")

    st.metric(
        label="Similitud visual",
        value=f"{p:.1f} %",
        delta=categoria(p)
    )

    st.progress(min(max(p / 100, 0.0), 1.0))

    st.write("")

    st.markdown("### Comparación de imágenes")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.image(
            res["gris_ref"],
            caption="Imagen original",
            use_container_width=True
        )

    with c2:
        st.image(
            res["gris_dib"],
            caption="Tu reproducción",
            use_container_width=True
        )

    with c3:
        st.image(
            superposicion(res),
            caption="Mapa de diferencias",
            use_container_width=True
        )

    st.markdown("""
    <div class="info-card">
        <h3>¿Cómo interpretar los colores?</h3>
        <p>
            🟢 Verde: trazos que coinciden.<br>
            🔴 Rojo: trazos de la referencia que faltan en tu dibujo.<br>
            🔵 Azul: trazos adicionales presentes en tu dibujo.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    st.markdown("### Interpretación del análisis")

    for linea in res["explicacion"]:
        st.write("• " + linea)

    with st.expander("Conoce cómo se calcula la similitud"):

        s = res["subpuntajes"]
        m = res["metricas"]

        st.write(
            "El sistema realiza un preprocesamiento y una alineación "
            "de las imágenes para comparar sus características visuales."
        )

        st.write(
            f"**Coincidencia de trazos (50 %):** "
            f"{s['trazos']*100:.1f} %"
        )

        st.write(
            f"**Distancia Chamfer (30 %):** "
            f"{s['chamfer']*100:.1f} % "
            f"(distancia media: {m['chamfer_px']:.1f} px)"
        )

        st.write(
            f"**Estructura SSIM (20 %):** "
            f"{s['estructura']*100:.1f} %"
        )

    st.write("")
    st.markdown("---")

    st.markdown("### ¿Quieres realizar otro reto?")

    c1, c2 = st.columns(2)

    with c1:
        if st.button(
            "Jugar de nuevo",
            type="primary",
            use_container_width=True
        ):
            ir("dificultad", ref=None, resultado=None)

    with c2:
        if st.button(
            "Cambiar modalidad",
            use_container_width=True
        ):
            ir("modalidad", ref=None, resultado=None)


# ---------------------------------------------------------
# 12. PIE DE PÁGINA
# ---------------------------------------------------------

st.markdown("---")

st.markdown("""
<div style="text-align:center;padding:22px 0 8px;border-top:1px solid #E9DFE8;">
    <div style="font-family:Georgia,serif;font-weight:700;color:#492C52;font-size:21px;letter-spacing:-.5px;">TraceLab</div>
    <div style="font-size:10px;color:#827782;letter-spacing:1.6px;margin-top:7px;">MEMORIA VISUAL · ARTE · PERCEPCIÓN</div>
    <div style="font-size:11px;color:#A195A1;margin-top:9px;">Procesamiento Digital de Imágenes · Proyecto académico</div>
</div>
""", unsafe_allow_html=True)
