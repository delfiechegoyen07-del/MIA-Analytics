import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="MÍA Analytics",
    page_icon="🛍️",
    layout="wide"
)

st.title("🛍️ MÍA Analytics")
st.subheader("Analista inteligente de clientes")
st.write("Panel de análisis de comentarios de MÍA Store")

archivo = st.file_uploader(
    "Subí el Excel con los comentarios analizados",
    type=["xlsx"]
)

if archivo is not None:
    df = pd.read_excel(archivo)

    total = len(df)
    negativos = (df["Sentimiento"] == "Negativo").sum()
    urgentes = (df["Urgencia"] == "Alta").sum()

    col1, col2, col3 = st.columns(3)

    col1.metric("Comentarios analizados", total)
    col2.metric("Comentarios negativos", negativos)
    col3.metric("Reclamos urgentes", urgentes)

    st.divider()
    st.subheader("📊 Resultados del análisis")

    col4, col5 = st.columns(2)

    with col4:
        fig1 = px.pie(
            df,
            names="Sentimiento",
            title="Sentimiento de los clientes"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col5:
        fig2 = px.histogram(
            df,
            x="Categoría",
            title="Principales temas de los comentarios"
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🚨 Reclamos urgentes")
    st.dataframe(
        df[df["Urgencia"] == "Alta"],
        use_container_width=True
    )

    st.subheader("💬 Todos los comentarios")
    st.dataframe(df, use_container_width=True)

else:
    st.info("Subí el archivo MIA_Analytics_Resultados.xlsx para visualizar el análisis.")

st.divider()
st.subheader("🤖 Analizar un comentario nuevo con IA")

comentario_nuevo = st.text_area(
    "Escribí el comentario de un cliente:",
    placeholder="Ejemplo: Hace dos semanas que espero mi pedido y nadie me responde."
)

if st.button("✨ Analizar con Gemini"):
    if not comentario_nuevo.strip():
        st.warning("Primero escribí un comentario.")
    else:
        import json
        from google import genai

        try:
            with st.spinner("Gemini está analizando el comentario..."):
                cliente_ia = genai.Client(
                    api_key=st.secrets["GEMINI_API_KEY"]
                )

                instrucciones_ia = """
                Sos el analista de clientes de MÍA Store,
                una tienda online uruguaya de ropa y accesorios.

                Analizá el siguiente comentario y devolvé
                exclusivamente un JSON válido con estas claves:

                "categoria": Envíos, Talles, Calidad,
                Cambios y devoluciones, Atención u Otros.
                "sentimiento": Positivo, Negativo o Neutral.
                "urgencia": Alta, Media o Baja.
                "respuesta": mensaje breve, amable y
                personalizado en español rioplatense.

                No inventes datos sobre pedidos ni prometas
                soluciones que no estén confirmadas.

                Comentario:
                """

                resultado_ia = cliente_ia.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=instrucciones_ia + comentario_nuevo,
                    config={
                        "response_mime_type": "application/json"
                    }
                )

                analisis = json.loads(resultado_ia.text)

            st.success("¡Comentario analizado!")

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Categoría", analisis["categoria"])
            col_b.metric("Sentimiento", analisis["sentimiento"])
            col_c.metric("Urgencia", analisis["urgencia"])

            st.subheader("💬 Respuesta sugerida")
            st.info(analisis["respuesta"])

        except Exception as error:
            st.error("No se pudo completar el análisis.")
            st.caption(str(error))
