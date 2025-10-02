import time
from typing import Optional
import pandas as pd
import streamlit as st

from adnmt_logic import comparacion_masiva, resultados_a_excel
st.set_page_config(page_title="Comparación masiva ADNmt", page_icon="🧬", layout="wide")


st.markdown(
    """
    <style>
    :root {
        --primary: #2563eb;
        --primary-600: #1d4ed8;
        --bg: #ffffff;
    }
    .stApp {
        background: var(--bg);
    }
    .main > div {
        padding-top: 0rem;
    }
        /* Jerarquía de títulos más equilibrada */
        .stApp h1 {
            font-size: 2.4rem; /* encabezado más grande */
            font-weight: 800;
            margin: 0 0 .6rem 0;
        }
        .stApp h2 {
            font-size: 1.3rem;
            font-weight: 600;
            margin: .2rem 0 .4rem 0;
        }
        .stApp h3 {
            font-size: 1.05rem;
            font-weight: 600;
        }
        /* Sidebar: encabezados un poco más pequeños */
        section[data-testid="stSidebar"] h2 {
            font-size: 1.1rem;
        }
    .metric-card {
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1rem;
        background: #fff;
    }
    .stButton > button {
        background-color: var(--primary);
        color: #fff;
        border: none;
        padding: 0.6rem 1rem;
        border-radius: 8px;
    }
        .stButton > button:hover {
        background-color: var(--primary-600);
    }

        /* Uploader: reemplazo de textos a español */
        [data-testid="stFileUploadDropzone"] {
            position: relative;
        }
        /* Texto principal "Arrastrá y soltá el archivo aquí" */
        [data-testid="stFileUploadDropzone"]::before {
            content: "Arrastrá y soltá el archivo aquí";
            position: absolute;
            top: 18px;
            left: 18px;
            color: #111827;
            font-weight: 500;
            pointer-events: none;
        }
        /* Oculta línea de límite y tipo para evitar inglés duplicado */
        [data-testid="stFileUploadDropzone"] small {
            display: none !important;
        }
        /* Cambia texto del botón "Browse files" */
        [data-testid="stFileUploadDropzone"] button span {
            visibility: hidden;
        }
        [data-testid="stFileUploadDropzone"] button::after {
            content: "Buscar archivo";
            visibility: visible;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🧬 Comparación masiva de haplotipos de ADNmt 🧬")

# Sidebar
st.sidebar.header("📁 Entrada")
uploaded_file = st.sidebar.file_uploader("Seleccionar archivo .xlsx", type=["xlsx"])
st.sidebar.caption("Arrastrá y soltá, o hacé clic para seleccionar el archivo (.xlsx).")

# Filtro opcional por cantidad máxima de diferencias
aplicar_filtro = st.sidebar.checkbox("Filtrar por máximo de diferencias", value=False)
if aplicar_filtro:
    max_diffs = st.sidebar.number_input("Máximo de diferencias (≤ N)", min_value=0, step=1, value=1)
else:
    max_diffs = None

with st.sidebar.expander("Formato esperado del Excel"):
    st.markdown(
        """
        - Columnas requeridas: **`Sample Name`**, **`Rango de lectura`**.
        - Las mutaciones deben estar en columnas adicionales (por ejemplo `0, 1, 2, ...`).
        - Rango de lectura:
          - D-Loop completo: `16024-576`
          - HV1/HV2: `16024-16480/50-430`
        """
    )

st.write(
    "Subí un archivo Excel (.xlsx) con las columnas 'Sample Name', 'Rango de lectura' y las columnas de mutaciones."
)

st.markdown(
    """
    1. Subí el archivo Excel.
    2. Ejecutá la comparación.
    3. Descargá los resultados.
    """
)

if uploaded_file is not None:
    try:
        df_input = pd.read_excel(uploaded_file)
    except Exception as exc:  
        st.error(f"No se pudo leer el Excel: {exc}")
        st.stop()

    st.subheader("Vista previa de datos")
    st.dataframe(df_input.head(20), use_container_width=True)

    if st.button("Ejecutar comparación"):
        start = time.perf_counter()
        with st.spinner("Ejecutando comparación masiva. Esto puede tardar unos minutos..."):
            try:
                if max_diffs is not None:
                    results_df = comparacion_masiva(df_input, max_diferencias=int(max_diffs))
                else:
                    results_df = comparacion_masiva(df_input)
            except Exception as exc:  
                st.error(f"Error durante la comparación: {exc}")
                st.stop()

        elapsed = time.perf_counter() - start

        if results_df.empty:
            if max_diffs is not None:
                st.info(f"No se encontraron pares con ≤ {int(max_diffs)} diferencias.")
            else:
                st.info("No se encontraron pares.")
        else:
            st.success(f"Comparación completa en {elapsed:.2f} s")
            st.subheader("Resultados")
            st.dataframe(results_df, use_container_width=True)

            excel_bytes = resultados_a_excel(results_df)
            st.download_button(
                label="Descargar resultados",
                data=excel_bytes,
                file_name="Resultados Comparación Masiva.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )


