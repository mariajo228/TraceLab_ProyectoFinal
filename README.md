# TraceLab

**Memoria visual, arte y percepción.** Aplicación web (Streamlit) que muestra una imagen
(mandala o silueta) durante unos segundos, deja que la persona la dibuje de memoria y calcula
un **porcentaje de similitud visual** con una explicación y un mapa de diferencias.

> Proyecto Final · Procesamiento Digital de Imágenes 2026-2 · Universidad Autónoma de Occidente
> Tema: Análisis de la Expresión Humana en el Arte y la Cultura
> Autores: **[COMPLETAR: nombres]** · Profesor: Nicolas Llanos Neuta

## ¿Cómo funciona?

1. La persona elige **modalidad** (mandalas / siluetas) y **nivel** (fácil 10 s, intermedio 15 s, difícil 20 s).
2. La app muestra un reto al azar del banco `reto` y lo oculta al terminar el tiempo.
3. La persona sube una foto o imagen de su dibujo.
4. TraceLab aplica **procesamiento digital clásico** (binarización de Otsu, esqueletización,
   alineación fina, F-score de trazos con tolerancia, distancia Chamfer y SSIM) y devuelve
   el porcentaje, una explicación en lenguaje natural y un mapa verde / rojo / azul.

No se entrena ninguna red neuronal: el comparador es explicable y no requiere pares de
entrenamiento. El porcentaje mide **similitud visual de trazos**, no memoria, inteligencia
ni calidad artística. Detalles en [`docs/DOCUMENTACION_TECNICA.md`](docs/DOCUMENTACION_TECNICA.md).

## Estructura del repositorio

```
TraceLab/
├── app/                    Código fuente de la aplicación
│   ├── app.py              Interfaz Streamlit (6 pantallas)
│   ├── procesamiento.py    Preprocesamiento: gris → Otsu → encuadre → esqueleto
│   └── comparador.py       Alineación, métricas, puntaje, explicación y superposición
├── scripts/
│   └── generar_division.py Casi duplicados + partición train/val/test/reto
├── notebooks/
│   └── ProyectoFinal_TraceLab.ipynb   Notebook de desarrollo y evaluación (Colab)
├── data/                   Estructura de datos (las imágenes NO se versionan) → data/README.md
├── results/                Figuras y tablas de la evaluación → results/README.md
├── docs/
│   ├── DOCUMENTACION_TECNICA.md
│   ├── INSTRUCCIONES_EJECUCION.md
│   ├── GUIA_GUI.md
│   └── img/                Capturas de la interfaz
└── requirements.txt
```

## Inicio rápido

```bash
git clone [COMPLETAR: URL del repositorio]
cd TraceLab
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 1) Descarga el dataset (ver data/README.md) y colócalo en data/Dataset/
# 2) Genera la partición del dataset (o copia el CSV desde Drive)
python scripts/generar_division.py

# 3) Lanza la interfaz
streamlit run app/app.py
```

Para ejecutarlo en Google Colab, consulta [`docs/INSTRUCCIONES_EJECUCION.md`](docs/INSTRUCCIONES_EJECUCION.md).

## Datos

| Recurso | Dónde |
|---|---|
| Dataset de 1.200 imágenes (900 mandalas: 300 por nivel · 300 siluetas: 100 por nivel) | **[COMPLETAR: enlace de Drive]** |
| Partición `division_dataset_v2.csv` | `data/documentacion/` (se genera con `scripts/generar_division.py`) |
| Resultados de las pruebas sintéticas | `results/` |

## Resultados principales

Evaluación **sintética** (reproducciones simuladas) sobre el conjunto *test*, AUC al separar
"misma imagen alterada" de "imagen distinta":

| Modalidad | Fácil | Intermedio | Difícil |
|---|---|---|---|
| Mandalas | 0,936 | 0,937 | 0,906 |
| Siluetas | 1,000 | 1,000 | 0,994 |

Tabla completa, figuras y limitaciones en [`results/README.md`](results/README.md).
**Aún no hay validación con dibujos humanos reales** (ver limitaciones).

## Guía de uso de la GUI

Paso a paso con capturas en [`docs/GUIA_GUI.md`](docs/GUIA_GUI.md).

## Limitaciones

- La validez con dibujos humanos reales está pendiente: lo sintético solo prueba robustez.
- El comparador es sensible a cambios grandes de escala en mandalas (ver `results/README.md`).
- El porcentaje es una medida de similitud visual, no de memoria ni de calidad artística.

## Privacidad

El guardado del dibujo es **opcional** (casilla de consentimiento) y anónimo (`p########`).
`data/Dataset/` y `data/resultados/registros_participantes.csv` están en `.gitignore`.
