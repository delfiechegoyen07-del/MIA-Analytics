
import streamlit as st
import pandas as pd
import plotly.express as px
import json
from pathlib import Path
from google import genai

st.set_page_config(
    page_title="MÍA Analytics | MÍA Store",
    page_icon="🤎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# COLORES Y ESTILO
CHOCOLATE = "#4A342B"
CREMA = "#F5F0E8"
MARRON = "#755647"
ARENA = "#C8AC96"

st.markdown("""
<style>
.stApp {
    background-color: #F5F0E8;
    color: #4A342B;
}
.block-container {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
h1, h2, h3, p {
    color: #4A342B;
}
div[data-testid="stMetric"] {
    background: #FFFFFF;
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #E9DFD4;
}
div[data-testid="stMetricValue"] {
    color: #4A342B;
}
div[data-testid="stMetricLabel"] {
    color: #806653;
}
.stButton > button[kind="primary"] {
    background: #4A342B;
    color: white;
    border: none;
    border-radius: 12px;
}
.stButton > button[kind="primary"]:hover {
    background: #755647;
    color: white;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 18px;
}
@media (max-width: 768px) {
    .block-container {
        padding: 1rem;
    }
    div[data-testid="stMetric"] {
        padding: 12px;
    }
}

/* Botón Analizar comentario */
div.stButton > button[kind="primary"] {
    background-color: #4A342B !important;
    color: #FFFFFF !important;
    border-color: #4A342B !important;
}

div.stButton > button[kind="primary"] p {
    color: #FFFFFF !important;
}

div.stButton > button[kind="primary"]:hover {
    background-color: #755647 !important;
    color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)

# ENCABEZADO
st.markdown("""
<div style="
    background:#4A342B;
    padding:32px;
    border-radius:22px;
    margin-bottom:25px;
">
    <p style="color:#EADBCD;font-size:12px;
    letter-spacing:2px;margin:0;">
    MÍA STORE / CUSTOMER INTELLIGENCE
    </p>
    <div style="
    color:#FFFFFF;
    font-size:38px;
    font-weight:800;
    line-height:1.3;
    margin:12px 0;
">
    MÍA Analytics
</div>
    <p style="color:#EADBCD;margin:0;">
    Entendé a tus clientes. Mejorá su experiencia.
    </p>
</div>
""", unsafe_allow_html=True)

# DATOS
ruta = Path(__file__).parent / "MIA_Analytics_Resultados.xlsx"

if ruta.exists():
    df = pd.read_excel(ruta)
    df.columns = df.columns.str.strip()
else:
    st.error("No se encontró el archivo de resultados.")
    st.stop()

# RESUMEN
st.subheader("Resumen general")

total = len(df)
negativos = (
    df["Sentimiento"].astype(str).str.strip().str.lower()
    == "negativo"
).sum()
urgentes = (
    df["Urgencia"].astype(str).str.strip().str.lower()
    == "alta"
).sum()

c1, c2, c3 = st.columns(3)

c1.metric("Comentarios analizados", total)
c2.metric("Comentarios negativos", int(negativos))
c3.metric("Reclamos urgentes", int(urgentes))

st.write("")

# GRAFICOS
st.subheader("Comportamiento de los clientes")

sentimientos = (
    df["Sentimiento"].value_counts()
    .reset_index()
)
sentimientos.columns = ["Sentimiento", "Cantidad"]

categorias = (
    df["Categoría"].value_counts()
    .reset_index()
)
categorias.columns = ["Categoría", "Cantidad"]

g1, g2 = st.columns(2)

with g1:
    with st.container(border=True):
        fig1 = px.pie(
            sentimientos,
            names="Sentimiento",
            values="Cantidad",
            hole=0.62,
            title="Sentimiento de los clientes",
            color="Sentimiento",
            color_discrete_map={
                "Negativo": "#755647",
                "Neutral": "#C8AC96",
                "Positivo": "#E5D6C7"
            }
        )
        fig1.update_layout(
            height=330,
            margin=dict(l=10, r=10, t=55, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            font_color=CHOCOLATE,
            legend=dict(orientation="h", y=-0.05)
        )
        fig1.update_traces(
            textinfo="percent",
            textposition="inside"
        )
        st.plotly_chart(fig1, use_container_width=True)

with g2:
    with st.container(border=True):
        fig2 = px.bar(
            categorias,
            x="Cantidad",
            y="Categoría",
            orientation="h",
            title="Temas más mencionados",
            color_discrete_sequence=[MARRON]
        )
        fig2.update_layout(
            height=330,
            margin=dict(l=10, r=10, t=55, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color=CHOCOLATE,
            yaxis={"categoryorder": "total ascending"}
        )
        st.plotly_chart(fig2, use_container_width=True)

# RECLAMOS URGENTES
st.write("")
st.subheader("🚨 Reclamos prioritarios")

reclamos = df[
    df["Urgencia"].astype(str).str.strip().str.lower()
    == "alta"
]

st.markdown(
    f"**{len(reclamos)} comentarios** requieren "
    "atención prioritaria."
)

with st.container(border=True):
    for _, fila in reclamos.iterrows():
        st.markdown(
            f"**Cliente #{fila['ID']} · {fila['Categoría']}**"
        )
        st.write(f"💬 {fila['Comentario del cliente']}")
        with st.expander("Ver respuesta sugerida"):
            st.write(fila["Respuesta sugerida"])
        st.divider()

# EXPLORAR COMENTARIOS
st.write("")
st.subheader("Explorar comentarios")

filtro = st.selectbox(
    "Filtrar por sentimiento",
    ["Todos", "Positivo", "Neutral", "Negativo"]
)

filtrados = (
    df if filtro == "Todos"
    else df[df["Sentimiento"] == filtro]
)

st.dataframe(
    filtrados,
    use_container_width=True,
    hide_index=True
)

# GUARDAR LOS COMENTARIOS NUEVOS DURANTE LA SESIÓN
if "comentarios_nuevos" not in st.session_state:
    st.session_state.comentarios_nuevos = []

# CONCLUSIONES Y RECOMENDACIONES
st.subheader("📋 Conclusiones y recomendaciones")

with st.container(border=True):
    total_comentarios = len(df)

    cantidad_negativos = (
        df["Sentimiento"].astype(str).str.strip().str.lower()
        == "negativo"
    ).sum()

    cantidad_urgentes = (
        df["Urgencia"].astype(str).str.strip().str.lower()
        == "alta"
    ).sum()

    porcentaje_negativos = (
        cantidad_negativos / total_comentarios * 100
        if total_comentarios else 0
    )

    categorias_frecuentes = (
        df["Categoría"]
        .astype(str)
        .value_counts()
    )

    if not categorias_frecuentes.empty:
        principal_categoria = categorias_frecuentes.index[0]
    else:
        principal_categoria = "Sin datos"

    st.markdown("#### 🔎 ¿Qué está pasando en MÍA Store?")

    st.write(
        f"El {porcentaje_negativos:.0f}% de los comentarios "
        "analizados son negativos. "
        f"Además, se identificaron {cantidad_urgentes} "
        "comentarios de alta urgencia que requieren "
        "atención prioritaria."
    )

    st.write(
        f"La categoría con mayor cantidad de comentarios "
        f"es **{principal_categoria}**, por lo que "
        "conviene analizarla para detectar posibles "
        "oportunidades de mejora."
    )

    st.markdown("#### 💡 ¿Qué debería hacer la empresa?")

    if cantidad_urgentes > 0:
        st.write(
            "🚨 **Priorizar los reclamos urgentes:** "
            "contactar a esos clientes y ofrecer "
            "soluciones personalizadas."
        )

    if porcentaje_negativos >= 30:
        st.write(
            "📉 **Mejorar la experiencia del cliente:** "
            "revisar las causas de los comentarios "
            "negativos para evitar que se repitan."
        )

    st.write(
        f"📊 **Revisar la categoría {principal_categoria}:** "
        "analizar los comentarios de esta categoría "
        "para identificar problemas recurrentes."
    )

    st.write(
        "🤎 **Dar seguimiento a los clientes:** "
        "utilizar las respuestas sugeridas por Gemini "
        "como punto de partida, revisándolas antes "
        "de enviarlas."
    )

st.divider()

# ANALISIS EN VIVO
st.write("")
st.subheader("✨ Analizar con inteligencia artificial")

with st.container(border=True):
    st.write(
        "Ingresá un comentario nuevo y Gemini identificará "
        "su categoría, sentimiento y urgencia."
    )

    comentario = st.text_area(
        "Comentario del cliente",
        placeholder="Escribí acá el comentario...",
        height=120
    )

    if st.button(
        "🤎 Analizar comentario",
        type="primary",
        use_container_width=True
    ):
        if not comentario.strip():
            st.warning("Primero escribí un comentario.")
        else:
            try:
                with st.spinner("Gemini está analizando..."):
                    client = genai.Client(
                        api_key=st.secrets["GEMINI_API_KEY"]
                    )

                    prompt = """
                    Sos el analista de clientes de MÍA Store,
                    una tienda online uruguaya.

                    Analizá el comentario y devolvé
                    únicamente un JSON con:
                    "categoria", "sentimiento",
                    "urgencia", "respuesta".

                    Categorías: Envíos, Talles, Calidad,
                    Cambios y devoluciones, Atención, Otros.
                    Sentimientos: Positivo, Negativo, Neutral.
                    Urgencias: Alta, Media, Baja.

                    La respuesta debe ser breve, amable
                    y personalizada en español rioplatense.
                    No inventes información sobre pedidos
                    ni prometas soluciones no confirmadas.

                    Comentario:
                    """

                    
respuesta = None

for intento in range(3):
    try:
        respuesta = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt + comentario,
            config={"response_mime_type": "application/json"}
        )
        break

    except Exception as error:
        codigo_error = getattr(error, "code", None)

        if codigo_error not in (429, 500, 502, 503, 504):
            raise

        if intento == 2:
            raise

        import time
        time.sleep(2 * (intento + 1))


                    analisis = json.loads(respuesta.text)

                nuevo_resultado = {
                    "ID": len(df) + len(
                        st.session_state.comentarios_nuevos
                    ) + 1,
                    "Comentario del cliente": comentario,
                    "Categoría": analisis["categoria"],
                    "Sentimiento": analisis["sentimiento"],
                    "Urgencia": analisis["urgencia"],
                    "Respuesta sugerida": analisis["respuesta"]
                }

                st.session_state.comentarios_nuevos.append(
                    nuevo_resultado
                )

                st.success("¡Análisis completado!")

                a, b, c = st.columns(3)
                a.metric("Categoría", analisis["categoria"])
                b.metric("Sentimiento", analisis["sentimiento"])
                c.metric("Urgencia", analisis["urgencia"])

                st.markdown("#### Respuesta sugerida")
                st.info(analisis["respuesta"])

            except Exception as error:
                st.error("No se pudo analizar el comentario.")
                st.caption(str(error))


# DESCARGAR RESULTADOS ACTUALIZADOS
if st.session_state.comentarios_nuevos:
    st.subheader("📥 Descargar análisis")

    st.write(
        f"Analizaste {len(st.session_state.comentarios_nuevos)} "
        "comentarios nuevos en esta sesión."
    )

    nuevos_df = pd.DataFrame(
        st.session_state.comentarios_nuevos
    )

    resultados_actualizados = pd.concat(
        [df, nuevos_df],
        ignore_index=True
    )

    from io import BytesIO

    archivo_excel = BytesIO()

    with pd.ExcelWriter(
        archivo_excel,
        engine="openpyxl"
    ) as writer:
        resultados_actualizados.to_excel(
            writer,
            index=False,
            sheet_name="Analisis de clientes"
        )

    st.download_button(
        label="📥 Descargar Excel actualizado",
        data=archivo_excel.getvalue(),
        file_name="MIA_Analytics_Actualizado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

st.divider()
st.caption(
    "MÍA Analytics · Proyecto académico de eCommerce "
    "· Datos simulados · Powered by Gemini"
)
