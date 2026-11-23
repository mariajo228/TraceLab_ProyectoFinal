# Documentación técnica de TraceLab

## 1. Objetivo y decisiones de diseño

TraceLab compara una imagen de referencia (mandala o silueta) con el dibujo que una persona hace de memoria
y devuelve un porcentaje de **similitud visual** explicable.

| Decisión | Justificación |
|---|---|
| **No se entrena una CNN** clasificadora mandala/silueta | La persona ya elige la modalidad en la interfaz. |
| **Comparador clásico** (sin aprendizaje) | Aún no existían dibujos humanos para entrenar una red siamesa, y el método clásico permite mostrar *qué* coincide. |
| **Partición sin fuga de datos** | Los casi duplicados se agrupan y cada grupo queda en un solo conjunto. |
| **Evaluación sintética etiquetada como tal** | Solo valida robustez; la validez real exige dibujos humanos. |

## 2. Arquitectura

```
Imagen de referencia ─┐                                   ┌─ F-score de trazos (50 %)
                      ├─► preparar() ─► alinear() ─► métricas ─► Chamfer (30 %) ─► puntaje 0–100
Dibujo de la persona ─┘  (procesamiento.py)   (comparador.py)   └─ SSIM (20 %)
                                                                  └─► explicar() · superposicion()
app.py (Streamlit) usa comparador.py y procesamiento.py sin duplicar lógica.
```

| Módulo | Responsabilidad |
|---|---|
| `app/procesamiento.py` | Carga, binarización, encuadre y esqueletización. Define rutas, niveles y tiempos. |
| `app/comparador.py` | Alineación fina, métricas, puntaje, categoría, texto explicativo y mapa de diferencias. |
| `app/app.py` | Interfaz: estado de sesión, selección de reto, temporizador, carga, resultados, guardado opcional. |
| `scripts/generar_division.py` | Casi duplicados (dHash) y partición estratificada. |

## 3. Dataset y partición

- 1.200 imágenes: mandalas (300 por nivel) y siluetas (100 por nivel); niveles `facil`, `intermedio`, `dificil`.
- **Casi duplicados:** dHash de 32×32 (1.024 bits) y distancia de Hamming. Umbral = **69**; con ese umbral hay 14 pares.
- Los pares del mismo estrato (modalidad + nivel) se unen con *union-find*; el grupo más grande tiene 7 imágenes.
- **Reparto** estratificado por modalidad y nivel, con semilla **42**:

| Conjunto | Proporción | Uso |
|---|---|---|
| `train` | 50 % | Explorar y diseñar el comparador |
| `val` | 15 % | Ajustar parámetros (tolerancia, pesos) |
| `test` | 15 % | Evaluación final, una sola vez |
| `reto` | 20 % | Banco de imágenes que ve el usuario en la app |

Resultado: 600 / 180 / 180 / 240 imágenes y **0 casi duplicados** del mismo estrato en conjuntos distintos.
El archivo resultante es `data/documentacion/division_dataset_v2.csv`.

## 4. Preprocesamiento (`procesamiento.preparar`)

| Paso | Función | Parámetros | Problema que resuelve |
|---|---|---|---|
| Lectura | `cargar_gris` | Corrige EXIF; compone transparencia sobre blanco; escala de grises | Fotos giradas, PNG con alfa |
| Reducción | `preparar` | Lado máximo 1.600 px | Costo de cómputo |
| Suavizado y polaridad | `binarizar` | Gauss 3×3; invierte si el borde es oscuro | Fondos oscuros |
| Iluminación | `_quitar_fondo_desigual` | Solo con `foto=True`; cierre morfológico + división | Sombras en fotos de papel |
| Binarización | `binarizar` | Otsu; descarta imágenes casi uniformes (σ < 3) | Separar tinta y fondo |
| Limpieza | `binarizar` | Elimina componentes con área < `max(6, 0,00005·píxeles)` | Ruido |
| Encuadre | `encuadrar` | Recorta al contenido, escala a 224 px y centra en 256×256 | Desplazamiento y tamaño |
| Trazos | `extraer_trazos` | Esqueletización (`skimage.morphology.skeletonize`) | Trazos gruesos o finos |

`encuadrar` también devuelve `aspecto`, `tinta` y `tamano`, que usa la explicación textual.

## 5. Comparador (`comparador.py`)

1. **Alineación fina** (`alinear`): prueba giros ±4°, desplazamientos ±5 px y escalas ±5 % (81 combinaciones, incluida la identidad) y conserva la de mayor F-score. En empate no mueve nada.
2. **Métricas** sobre trazos de 1 px, con la transformada de distancia:
   - *Precisión*: fracción de trazos del dibujo a ≤ `TOLERANCIA` (4 px) de un trazo del original.
   - *Cobertura*: fracción de trazos del original a ≤ 4 px de un trazo del dibujo.
   - *F-score de trazos*: media armónica de ambas.
   - *Chamfer*: media de las distancias medias en los dos sentidos.
   - *Estructura*: SSIM entre los trazos suavizados (σ = 3), ventana 11, recortado a [0, 1].
3. **Puntaje** = `100 · (0,5·F + 0,3·exp(−chamfer/8) + 0,2·SSIM)`.
4. **Categoría:** ≥ 85 muy alta · ≥ 70 alta · ≥ 50 media · ≥ 30 baja · < 30 muy baja.
5. **Explicación** (`explicar`): cobertura, precisión, proporciones, cantidad de tinta, y si faltaron o sobraron trazos.
6. **Mapa de diferencias** (`superposicion`): verde = coincide, rojo = falta en el dibujo, azul = sobra.

Los parámetros iniciales (tolerancia 4 px, pesos 0,5/0,3/0,2, escala Chamfer 8) se revisaron con `val`
(tolerancias 2, 3 y 4, sobre mandalas); los resultados están en `results/README.md`.

## 6. Interfaz (`app.py`)

Seis pantallas controladas por `st.session_state.pantalla`:
`bienvenida → modalidad → dificultad → observacion → carga → resultados`.
El reto se elige al azar solo entre filas con `split == "reto"` del CSV. La imagen se muestra con un
temporizador (10/15/20 s) y se oculta al terminar. Guía de uso: [`GUIA_GUI.md`](GUIA_GUI.md).

**Guardado opcional (con consentimiento):** el dibujo se guarda como
`Dataset/dibujos_usuarios/<modalidad>/<original>__p########.<ext>` y las métricas en
`resultados/registros_participantes.csv` con un identificador anónimo.

## 7. Validación

- **Sintética** (`perturbar` en el notebook): idéntica, desplazada, escala pequeña/grande, rotada, trazo grueso,
  ruido, trazos omitidos, temblor, combinada, y el control negativo *otra imagen*. Se usa 15 imágenes por estrato.
- **Ajuste en `val`** y **evaluación final en `test`**, con AUC entre alteraciones (positivos) e imágenes distintas (negativos).
- **Dibujos humanos reales:** celdas 6.1 y 6.2 listas (puntaje y correlación de Spearman con valoración humana de 1 a 5),
  pero **todavía sin datos**.

## 8. Limitaciones

- No hay validación con dibujos humanos reales; las cifras actuales son sintéticas.
- En el AUC de `test` los positivos incluyen la perturbación `identica` (10 tipos × 15 imágenes = 150 por estrato), lo que lo vuelve algo optimista.
- En mandalas difíciles el margen en `val` entre "imagen distinta" y alteración leve es ≈ 0 (−0,5 puntos).
- `escalado_grande` y `combinado` bajan mucho el puntaje en mandalas (ver `results/README.md`).
- La alineación fina cubre cambios pequeños (±4°, ±5 px, ±5 %); el encuadre absorbe el resto.
- La similitud visual no mide memoria, inteligencia ni calidad artística.

## 9. Trabajo futuro

Recolectar dibujos reales y valoraciones humanas; recalibrar pesos y tolerancia con ellos; recalcular el AUC sin `identica`;
evaluar una red siamesa cuando existan pares reales.
