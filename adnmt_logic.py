import io
import re
from itertools import combinations
from typing import Iterable, List, Sequence, Tuple, Optional

import pandas as pd


# -----------------------------
# Utilidades de columnas/entrada
# -----------------------------

COLUMNAS_REQUERIDAS = ["Sample Name", "Rango de lectura"]


def _obtener_columnas_mutacion(df: pd.DataFrame) -> List[str]:
    """Devuelve todas las columnas de mutaciones (todas menos las requeridas).

    Asume que las columnas requeridas existen con esos nombres exactos.
    """
    return [col for col in df.columns if col not in COLUMNAS_REQUERIDAS]


def _concatenar_columnas_mutacion(df: pd.DataFrame) -> pd.DataFrame:
    """Une las columnas de mutaciones en una única lista por fila.

    - Elimina NaN.
    - Mantiene únicamente `Sample Name`, `Rango de lectura` y `Sec` (lista de mutaciones).
    """
    columnas_mutacion = _obtener_columnas_mutacion(df)
    df_copia = df.copy()
    # Aseguramos strings y removemos NaN antes de join
    df_copia[columnas_mutacion] = df_copia[columnas_mutacion].applymap(
        lambda v: str(v) if pd.notna(v) else None
    )
    df_copia["Secuencia"] = df_copia[columnas_mutacion].apply(
        lambda fila: ",".join([v for v in fila if v]), axis=1
    )
    df_copia = df_copia.reset_index(drop=True)

    listas_sec: List[List[str]] = []
    for secuencia in df_copia["Secuencia"].tolist():
        listas_sec.append(secuencia.split(",") if secuencia else [])

    df_salida = pd.DataFrame(
        {
            "Sample Name": df_copia["Sample Name"],
            "Rango de lectura": df_copia["Rango de lectura"],
            "Sec": listas_sec,
        }
    )
    return df_salida


# -----------------------------
# Manejo de rangos de lectura
# -----------------------------

RANGO_COMPLETO_LITERAL = "16024-576"


def _extraer_digitos_de_cadena(texto: str) -> List[int]:
    return list(map(int, re.findall(r"\d+", texto)))


def _extraer_digitos_profundo(valor: Iterable) -> List[int]:
    """Extrae todos los enteros desde estructuras anidadas (listas/strings/enteros)."""
    numeros: List[int] = []
    for elemento in valor:
        if isinstance(elemento, int):
            numeros.append(elemento)
        elif isinstance(elemento, list):
            numeros.extend(_extraer_digitos_profundo(elemento))
        elif isinstance(elemento, str):
            numeros.extend(_extraer_digitos_de_cadena(elemento))
    numeros.sort()
    return numeros


def _dividir_literal_rango(rango_literal: str) -> List[List[int]]:
    """Convierte el literal de rango en dos sub-rangos.

    - "16024-576" -> [[1, 576], [16024, 16569]]
    - "16024-16480/50-430" -> [[16024, 16480], [50, 430]]
    """
    if rango_literal == RANGO_COMPLETO_LITERAL:
        return [[1, 576], [16024, 16569]]
    numeros = _extraer_digitos_de_cadena(rango_literal)
    # Esperado: a-b/c-d => [a,b,c,d]
    return [[numeros[0], numeros[1]], [numeros[2], numeros[3]]]


def _combinar_rangos(rango1: Sequence[int], rango2: Sequence[int]) -> List[List[int]]:
    """Combina dos rangos (a-b y c-d para HV2/HV1) tomando la intersección componente a componente."""
    # Entradas esperadas: [a,b,c,d] para cada rango
    return [
        [max(rango1[0], rango2[0]), min(rango1[1], rango2[1])],
        [max(rango1[2], rango2[2]), min(rango1[3], rango2[3])],
    ]


# -----------------------------
# Filtrado de diferencias y heteroplasmias
# -----------------------------

_PATRONES_HOMOPOLIMEROS = [
    r"309.*C",
    r"C313DEL",
    r"C314DEL",
    r"C315DEL",
    r"455.*T",
    r"463.*C",
    r"524.*A",
    r"524.*C",
    r"573.*C",
    r"16193.*C",
    r"A523DEL",
    r"C524DEL",
]
_REGEX_HOMOPOLIMEROS = re.compile("|".join(_PATRONES_HOMOPOLIMEROS))

_IUPAC = {
    "R": ["A", "G"],
    "Y": ["C", "T"],
    "S": ["G", "C"],
    "W": ["A", "T"],
    "K": ["G", "T"],
    "M": ["A", "C"],
}


def _extraer_posiciones(lista_mutaciones: Sequence[str]) -> List[float]:
    """Extrae posiciones numéricas desde mutaciones (enteros o decimales)."""
    numeros: List[float] = []
    patron = re.compile(r"\d+(?:\.\d+)?")
    for s in lista_mutaciones:
        coincidencia = patron.search(s)
        if not coincidencia:
            continue
        texto_num = coincidencia.group(0)
        if "." in texto_num:
            numeros.append(float(texto_num))
        else:
            numeros.append(int(texto_num))
    return numeros


def _filtrar_homopolimericas(mutaciones: Sequence[str]) -> List[str]:
    return [m for m in mutaciones if not _REGEX_HOMOPOLIMEROS.match(m)]


def _filtrar_por_rango_lectura(
    rango_lectura: List[List[int]],
    posiciones_diferencia: Sequence[float],
    cadenas_diferencia: Sequence[str],
) -> Tuple[List[float], List[str]]:
    """Filtra posiciones/strings por pertenencia al rango de lectura (dos sub-rangos)."""
    posiciones_en_rango: List[int] = []
    a, b = rango_lectura[0], rango_lectura[1]
    for idx, pos in enumerate(map(int, posiciones_diferencia)):
        if (a[0] <= pos <= a[1]) or (b[0] <= pos <= b[1]):
            posiciones_en_rango.append(idx)

    nums_pos: List[float] = []
    strs_pos: List[str] = []
    for i in posiciones_en_rango:
        nums_pos.append(posiciones_diferencia[i])
        strs_pos.append(cadenas_diferencia[i])
    return nums_pos, strs_pos


def _indices_posiciones_duplicadas(valores: Sequence[float]) -> List[int]:
    vistos: dict = {}
    duplicados: List[int] = []
    for idx, val in enumerate(valores):
        if val in vistos:
            duplicados.append(vistos[val])
            duplicados.append(idx)
        else:
            vistos[val] = idx
    return duplicados


def _indices_posiciones_unicas(valores: Sequence[float]) -> List[int]:
    primer_indice: dict = {}
    conteos: dict = {}
    for idx, val in enumerate(valores):
        if val not in primer_indice:
            primer_indice[val] = idx
        conteos[val] = conteos.get(val, 0) + 1
    return [primer_indice[val] for val, cnt in conteos.items() if cnt == 1]


def _es_diferencia(grupos_letras: Sequence[Sequence[str]]) -> bool:
    """Devuelve True si NO hay letras repetidas en el aplanado; False si hay intersección.

    Interpretación basada en el notebook: si hay repetidos -> no diferencia (comparten base);
    si no los hay -> diferencia.
    """
    aplanado: List[str] = []
    for grupo in grupos_letras:
        aplanado += list(grupo)
    vistos: set = set()
    repetidos: set = set()
    for ch in aplanado:
        if ch in vistos:
            repetidos.add(ch)
        vistos.add(ch)
    return len(repetidos) == 0


def _contar_no_diferencias_unicas(mutaciones: Sequence[str], indices_unicos: Sequence[int]) -> int:
    """Cuenta cuántas mutaciones únicas NO deberían contarse como diferencia (por heteroplasmia)."""
    no_diferencias = 0
    for i in indices_unicos:
        mut = mutaciones[i]
        base_ref = mut[0]
        ultimo = mut[-1]
        grupos_letras: List[Sequence[str]] = []
        if ultimo in _IUPAC:
            grupos_letras.append(_IUPAC[ultimo])
            grupos_letras.append([base_ref])
        else:
            grupos_letras.append([ultimo])
        # True => diferencia; False => no diferencia
        es_dif = _es_diferencia(grupos_letras)
        if not es_dif:
            no_diferencias += 1
    return no_diferencias


def _contar_no_diferencias_pares(mutaciones: Sequence[str]) -> int:
    """Trabaja sobre pares de mutaciones repetidas en la misma posición (heteroplasmias en ambas muestras).

    Devuelve cuántas NO son diferencias (para restarlas del conteo total de diferencias).
    """
    no_diferencias = 0
    i = 0
    while i < len(mutaciones):
        mut1 = mutaciones[i]
        mut2 = mutaciones[i + 1]
        ultimo1 = mut1[-1]
        ultimo2 = mut2[-1]

        grupos_letras: List[Sequence[str]] = []
        grupos_letras.append(_IUPAC[ultimo1] if ultimo1 in _IUPAC else [ultimo1])
        grupos_letras.append(_IUPAC[ultimo2] if ultimo2 in _IUPAC else [ultimo2])

        es_dif = _es_diferencia(grupos_letras)
        if not es_dif:
            no_diferencias += 1
        i += 2
    return no_diferencias


def _comparacion_general(
    secuencia1: Sequence[str],
    secuencia2: Sequence[str],
    rango_sec1: str,
    rango_sec2: str,
    nombre1: str,
    nombre2: str,
) -> Tuple[str, str, int, List[List[int]]]:
    rango_int1 = _dividir_literal_rango(rango_sec1)
    rango_int2 = _dividir_literal_rango(rango_sec2)
    num_rango1 = _extraer_digitos_profundo(rango_int1)
    num_rango2 = _extraer_digitos_profundo(rango_int2)
    rango_lectura = _combinar_rangos(num_rango1, num_rango2)

    # Diferencias absolutas entre listas
    solo1 = list(set(secuencia1) - set(secuencia2))
    solo2 = list(set(secuencia2) - set(secuencia1))
    diferencias = solo1 + solo2

    # Descartar regiones homopoliméricas
    diferencias_filtradas = _filtrar_homopolimericas(diferencias)

    # A números
    posiciones_diferencias = _extraer_posiciones(diferencias_filtradas)

    # Filtrar por rango de lectura
    nums_pos, strs_pos = _filtrar_por_rango_lectura(rango_lectura, posiciones_diferencias, diferencias_filtradas)

    # Índices únicos y duplicados por posición
    indices_unicos = _indices_posiciones_unicas(nums_pos)
    indices_duplicados = _indices_posiciones_duplicadas(nums_pos)

    # De los únicos: ¿cuántos NO son diferencias por heteroplasmia compartida?
    no_diferencias_unicas = _contar_no_diferencias_unicas(strs_pos, indices_unicos)

    # De los duplicados: trabajar en pares en la misma posición
    mutaciones_duplicadas = [m for j, m in enumerate(strs_pos) if j in indices_duplicados]
    no_diferencias_pares = _contar_no_diferencias_pares(mutaciones_duplicadas)

    # Conteo total de diferencias reales
    total_diferencias = len(strs_pos) - (no_diferencias_unicas + no_diferencias_pares)

    return nombre1, nombre2, total_diferencias, rango_lectura


def _formatear_rango(rango_lectura: List[List[int]]) -> str:
    if rango_lectura == [[1, 576], [16024, 16569]]:
        return RANGO_COMPLETO_LITERAL
    hv1 = f"{rango_lectura[1][0]}-{rango_lectura[1][1]}"
    hv2 = f"{rango_lectura[0][0]}-{rango_lectura[0][1]}"
    return f"{hv2}/{hv1}"


# -----------------------------
# API principal
# -----------------------------

def comparacion_masiva(df_base: pd.DataFrame, max_diferencias: Optional[int] = None) -> pd.DataFrame:
    """Ejecuta la comparación masiva y devuelve un DataFrame de resultados.

    Requisitos del df_base:
    - Columnas: "Sample Name", "Rango de lectura" y N columnas de mutaciones.
    - El literal de rango respeta "-" para inicio/fin y "/" para separar regiones.
    """
    # Normalizar espacios en el literal del rango
    df_base_copia = df_base.copy()
    if "Rango de lectura" not in df_base_copia.columns or "Sample Name" not in df_base_copia.columns:
        raise ValueError(
            "El Excel debe contener las columnas 'Sample Name' y 'Rango de lectura'."
        )
    df_base_copia["Rango de lectura"] = (
        df_base_copia["Rango de lectura"].astype(str).str.replace(r"\s+", "", regex=True)
    )

    # Construir df compacto: Sample, Rango, Sec (lista)
    df_compacto = _concatenar_columnas_mutacion(df_base_copia)

    # Iterar sobre todas las combinaciones de pares de muestras
    resultados: List[Tuple[str, str, int, List[List[int]]]] = []
    muestras = df_compacto["Sample Name"].tolist()
    rangos = df_compacto["Rango de lectura"].tolist()
    secuencias = df_compacto["Sec"].tolist()

    for i, j in combinations(range(len(muestras)), 2):
        nombre1, nombre2 = muestras[i], muestras[j]
        rango1, rango2 = rangos[i], rangos[j]
        sec1, sec2 = secuencias[i], secuencias[j]
        nombre1, nombre2, diferencias, rango_lectura = _comparacion_general(
            sec1, sec2, rango1, rango2, nombre1, nombre2
        )
        # Siempre registramos el resultado; el filtrado (si corresponde) se aplica luego
        resultados.append((nombre1, nombre2, diferencias, rango_lectura))

    df_resultados = pd.DataFrame(
        resultados,
        columns=["INDIVIDUO 1", "INDIVIDUO 2", "Diferencias", "Rango de lectura"],
    )

    if df_resultados.empty:
        return df_resultados

    # Filtrar opcionalmente por cantidad máxima de diferencias (<= N)
    if max_diferencias is not None:
        df_resultados = df_resultados[df_resultados["Diferencias"] <= int(max_diferencias)]

    # Transformar rango a literal para salida
    df_resultados["Rango de lectura"] = df_resultados["Rango de lectura"].apply(_formatear_rango)

    # Ordenar y fijar índice
    df_resultados = df_resultados.sort_values(
        by=["INDIVIDUO 1", "Diferencias"], axis=0, na_position="last"
    ).set_index(["INDIVIDUO 1", "INDIVIDUO 2"]) .reset_index()

    return df_resultados


def resultados_a_excel(df_resultados: pd.DataFrame) -> bytes:
    """Serializa el DataFrame de resultados a un archivo Excel en memoria."""
    salida = io.BytesIO()
    # openpyxl suele estar disponible por defecto; explicitamos engine por claridad
    with pd.ExcelWriter(salida, engine="openpyxl") as escritor:
        df_resultados.to_excel(escritor, sheet_name="Resultados", index=False)
    salida.seek(0)
    return salida.getvalue()



