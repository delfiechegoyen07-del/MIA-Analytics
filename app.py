
import streamlit as st
import pandas as pd
import plotly.express as px
import json
from pathlib import Path
from google import genai

# CONFIGURACIÓN
st.set_page_config(
    page_title="MÍA Analytics | MÍA Store",
    page_icon="🤎",
    layout="wide"
)

# DISEÑO CREMA Y CHOCOLATE
st.markdown("""
<style>
.stApp {
    background-color: #F6F1E9;
    color: #382E2B;
}
h1, h2, h3 {
    color: #382E2B !important;
}
div[data-testid="stMetric"] {
    background: #FFFFFF;
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #E7DED3;
}
div[data-testid="stMetricLabel"] {
    color: #806653;
}
div[data-testid="stMetricValue"] {
    color: #382E2B;
}
.stButton > button {
    background-color: #382E2B;
    color: white;
    border-radius: 12px;
    border: none;
    padding: 10px 20px;
}
.stButton > button:hover {
    background-color: #806653;
    color: white;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 16px;
}
</style>
""", unsafe_allow_html=True)

# ENCABEZADO
st.title("MÍA Analytics")
st.caption("CUSTOMER INTELLIGENCE · MÍA STORE")
st.markdown(
    "Transformamos los comentarios de nuestros clientes "
    "en información útil para mejorar su experiencia."
)

st.divider()

# CARGAR LOS 50 COMENTARIOS AUTOMÁTICAMENTE
ruta = Path(__file__).parent / "MIA_Analytics_Resultados.xlsx"

if ruta.exists():
    df = pd.read_excel(ruta)
else:
    st.warning("No se encontró el archivo de resultados.")
    df = pd.DataFrame()

if not df.empty:
    df.columns = df.columns.str.strip()

    # INDICADORES
    total = len(df)
    negativos = (
        df["Sentimiento"].astype(str).str.strip().str.lower()
        == "negativo"
    ).sum()
    urgentes = (
        df["Urgencia"].astype(str).str.strip().str.lower()
        == "alta"
    ).sum()

    st.subheader("Resumen general")

    c1, c2, c3 = st.columns(3)
    c1.metric("Comentarios analizados", total)
    c2.metric("Comentarios negativos", int(negativos))
    c3.metric("Reclamos urgentes", int(urgentes))

    st.divider()

    # GRÁFICOS
    st.subheader("Comportamiento de los clientes")

    g1, g2 = st.columns(2)

    with g1:
        sentimiento = (
            df["Sentimiento"].value_counts()
            .reset_index()
        )
        sentimiento.columns = ["Sentimiento", "Cantidad"]

        fig1 = px.pie(
            sentimiento,
            names="Sentimiento",
            values="Cantidad",
            hole=0.55,
            title="Sentimiento de los clientes",
            color_discrete_sequence=[
                "#806653", "#D9C6B0", "#B7A08B"
            ]
        )
        fig1.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#382E2B"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with g2:
        categorias = (
            df["Categoría"].value_counts()
            .reset_index()
        )
        categorias.columns = ["Categoría", "Cantidad"]

        fig2 = px.bar(
            categorias,
            x="Cantidad",
            y="Categoría",
            orientation="h",
            title="Temas más mencionados",
            color_discrete_sequence=["#806653"]
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#382E2B",
            yaxis={"categoryorder": "total ascending"}
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # RECLAMOS URGENTES
    st.subheader("🚨 Reclamos que requieren atención")

    reclamos = df[
        df["Urgencia"].astype(str).str.strip().str.lower()
        == "alta"
    ]

    st.write(
        f"Se identificaron **{len(reclamos)} comentarios** "
        "que requieren atención prioritaria."
    )

    st.dataframe(
        reclamos,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # EXPLORADOR DE COMENTARIOS
    st.subheader("Explorar comentarios")

    opciones = ["Todos"] + sorted(
        df["Sentimiento"].dropna().astype(str).unique()
    )

    filtro = st.selectbox(
        "Filtrar por sentimiento",
        opciones
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

# ANÁLISIS EN VIVO
st.divider()
st.subheader("🤖 Analizar un comentario con Gemini")

st.write(
    "Ingresá un comentario nuevo y la inteligencia artificial "
    "identificará su categoría, sentimiento y urgencia, "
    "además de sugerir una respuesta."
)

comentario = st.text_area(
    "Comentario del cliente",
    placeholder="Escribí acá el comentario...",
    height=130
)

if st.button("✨ Analizar comentario", type="primary"):
    if not comentario.strip():
        st.warning("Primero escribí un comentario.")
    else:
        try:
            with st.spinner("Analizando con Gemini..."):
                client = genai.Client(
                    api_key=st.secrets["GEMINI_API_KEY"]
                )

                prompt = """
                Sos el analista de clientes de MÍA Store,
                una tienda online uruguaya de ropa y accesorios.

                Analizá este comentario y devolvé
                únicamente un JSON válido con las claves:
                "categoria", "sentimiento", "urgencia", "respuesta".

                Categorías posibles: Envíos, Talles, Calidad,
                Cambios y devoluciones, Atención u Otros.

                Sentimientos: Positivo, Negativo o Neutral.
                Urgencias: Alta, Media o Baja.

                Marcá urgencia alta ante reclamos graves,
                demoras importantes o clientes muy molestos.

                La respuesta debe ser breve, amable,
                personalizada y en español rioplatense.
                No inventes información ni prometas
                soluciones que no estén confirmadas.

                Comentario del cliente:
                """

                respuesta = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt + comentario,
                    config={
                        "response_mime_type": "application/json"
                    }
                )

                analisis = json.loads(respuesta.text)

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

st.divider()
st.caption(
    "MÍA Analytics · Proyecto académico de eCommerce "
    "· Datos simulados · Análisis asistido por Gemini"
)

