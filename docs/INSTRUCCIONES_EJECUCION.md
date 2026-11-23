# Instrucciones de ejecución

Hay dos formas de ejecutar TraceLab: **en local** (recomendada para la entrega) o **en Google Colab**
(como se desarrolló).

## A. Ejecución local

**Requisitos:** Python 3.10 o superior y `git`.

1. **Clonar e instalar**
   ```bash
   git clone [COMPLETAR: URL del repositorio]
   cd TraceLab
   python -m venv .venv
   source .venv/bin/activate          # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. **Descargar el dataset** desde el enlace de `data/README.md` y dejarlo en `data/Dataset/`
   con la estructura `mandalas|siluetas / facil|intermedio|dificil`.
3. **Obtener la partición del dataset** (cualquiera de las dos):
   - copiar `division_dataset_v2.csv` de Drive a `data/documentacion/`, o
   - generarlo: `python scripts/generar_division.py`
     (imprime la tabla de reparto y verifica que no haya fuga de datos; debe decir `0`).
4. **Lanzar la interfaz**
   ```bash
   streamlit run app/app.py
   ```
   Se abre en `http://localhost:8501`.

**Datos en otra ubicación:** `export TRACELAB_RAIZ=/ruta/a/carpeta` (Windows PowerShell:
`$env:TRACELAB_RAIZ="C:\ruta\carpeta"`). Esa carpeta debe contener `Dataset/`, `documentacion/` y `resultados/`.

## B. Ejecución en Google Colab

1. Sube la carpeta del proyecto a Drive como `Proyecto Final - Tracelab`
   (con `Dataset/`, `documentacion/`, `resultados/`).
2. Abre `notebooks/ProyectoFinal_TraceLab.ipynb` en Colab.
3. Ejecuta las celdas **en orden**. La sección 7 escribe `app.py`, `procesamiento.py` y `comparador.py`
   en `/content/tracelab_app/` y lanza Streamlit con un túnel de Cloudflare.
4. La última celda imprime la URL pública (`https://...trycloudflare.com`). Ábrela en el navegador.

## C. Reproducir la evaluación

La evaluación sintética y el cálculo de AUC están en las secciones **5** y **6** del notebook
(Colab, con el dataset en Drive). Cada celda indica qué conjunto usa:

| Celdas | Conjunto | Salida |
|---|---|---|
| 5.1 – 5.5 | `val` | `resultados/pruebas_sinteticas_val.csv` |
| Evaluación final + AUC | `test` (se usa una sola vez) | `resultados/pruebas_sinteticas_test.csv` |
| 6.1 – 6.2 | dibujos reales | `resultados/pruebas_reales.csv` (vacío hasta recolectar dibujos) |

## Problemas frecuentes

| Síntoma | Causa y solución |
|---|---|
| `No se encontró division_dataset_v2.csv` | Falta el paso 3. Copia el CSV o ejecuta `scripts/generar_division.py`. |
| `No existe .../Dataset/mandalas/facil` | El dataset no está en `data/Dataset/` o `TRACELAB_RAIZ` apunta mal. |
| `No hay retos disponibles para esta combinación` | El CSV no tiene filas `split == reto` para esa modalidad y nivel. |
| `No se detectaron trazos en el dibujo` | Imagen casi uniforme o con poco contraste: mejora la luz y el contraste. |
| Error por `use_container_width` | Versión de Streamlit demasiado nueva: instala con `requirements.txt` o cambia a `width="stretch"`. |
