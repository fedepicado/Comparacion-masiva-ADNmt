# Comparacion-masiva-ADNmt

Este proyecto permite realizar una comparación masiva de haplotipos de ADNmt a partir de un archivo .xlsx, teniendo en cuenta los rangos de lectura de las muestras, excluyendo de la comparacion regiones homopolimericas y teniendo en cuenta heteroplasmias. 

## Aplicación Web (Streamlit)

El repositorio incluye una aplicación en Streamlit que realiza exactamente la misma comparación a partir de un Excel de entrada.

### Prerrequisitos
- Python 3.9 o superior
- pip actualizado (`pip install --upgrade pip`)
- Sistema operativo probado: Windows 10/11

### Cómo instalar y ejecutar

1. Crear y activar un entorno virtual (opcional pero recomendado):

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Ejecutar la app:

```bash
streamlit run app.py
```

Si el comando anterior no abre la app, probar:

```bash
python -m streamlit run app.py
```

4. En el navegador (normalmente `http://localhost:8501`), subí el archivo Excel y presioná "Ejecutar comparación". Podrás descargar los resultados en Excel.

### Formato del Excel esperado

- Columnas requeridas: `**Sample Name**`, `**Rango de lectura**`.
- Las mutaciones deben estar en columnas adicionales (por ejemplo `0, 1, 2, ...`) con valores tipo `A73G`, `C151S`, etc.
- El rango de lectura debe expresarse como:
  - D-Loop completo: `16024-576`
  - HV1/HV2: `16024-16480/50-430` (usar `-` para inicio/fin y `/` para separar regiones)
- La primera columna debe contener el nombre de las muestras y la segunda el rango de lectura.

### Parámetro opcional: máximo de diferencias

En la barra lateral podés activar un filtro para exportar y visualizar solo los pares con una cantidad máxima de diferencias (≤ N). Si no activás el filtro, se mostrarán todos los pares calculados con su número de diferencias.

### Lógica del algoritmo (resumen)

1. Agrupa las columnas de mutaciones en una sola lista por muestra.
2. Calcula el rango de lectura consenso entre pares (intersección de rangos).
3. Calcula diferencias entre haplotipos, descartando regiones homopoliméricas y mutaciones fuera del rango.
4. Considera heteroplasmias usando nomenclatura IUPAC (`R,Y,S,W,K,M`).
5. Reporta sólo pares con 0 o 1 diferencias.

### Resultados

La app genera una tabla con:
- `INDIVIDUO 1`, `INDIVIDUO 2`: nombres de las muestras comparadas
- `Diferencias`: conteo de diferencias (límite <= 1)
- `Rango de lectura`: rango analizado en formato literal

Podés descargar los resultados en un archivo `Resultados Comparación Masiva.xlsx`. 










