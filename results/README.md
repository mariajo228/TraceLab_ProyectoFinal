# Resultados

Todas las cifras de esta carpeta provienen de la ejecución del notebook
(`notebooks/ProyectoFinal_TraceLab.ipynb`) y son de **reproducciones sintéticas** (simuladas),
no de dibujos humanos.

## Archivos

| Archivo | Contenido |
|---|---|
| `tablas/auc_test.csv` | AUC final sobre el conjunto `test` |
| `figuras/duplicados_casi_identicos.png` | Los 14 pares de casi duplicados (distancia de Hamming ≤ 69) |
| `figuras/preprocesamiento_pasos.png` | Gris → binaria (Otsu) → encuadrada 256×256 → trazos de 1 px |
| `figuras/verificacion_comparador.png` | Misma imagen vs. imagen distinta, con mapa de diferencias |
| `figuras/ejemplos_perturbaciones.png` | Ejemplos de alteraciones sintéticas y su puntaje |
| `pruebas_sinteticas_val.csv`, `pruebas_sinteticas_test.csv` | **[COMPLETAR: copiar desde `resultados/` de Drive]** |

## 1. Partición del dataset

| Modalidad | Nivel | reto | test | train | val | Total |
|---|---|---|---|---|---|---|
| mandalas | cada nivel | 60 | 45 | 150 | 45 | 300 |
| siluetas | cada nivel | 20 | 15 | 50 | 15 | 100 |
| **Total** | | **240** | **180** | **600** | **180** | **1.200** |

Casi duplicados del mismo estrato en conjuntos distintos: **0**.

## 2. Verificación básica

| Comparación | Puntaje |
|---|---|
| Misma imagen | 100,0 % |
| Imagen distinta | 50,8 % |

## 3. Puntaje medio por tipo de alteración (`val`)

| Tipo | Mandalas | Siluetas |
|---|---|---|
| identica | 100,0 | 100,0 |
| ruido | 99,4 | 99,8 |
| escalado_pequeno | 97,7 | 99,3 |
| rotado | 96,7 | 93,5 |
| desplazado | 95,0 | 99,6 |
| trazos_omitidos | 93,9 | 92,3 |
| trazo_grueso | 92,9 | 93,9 |
| temblor | 77,9 | 79,0 |
| combinado | 66,8 | 68,9 |
| escalado_grande | 61,3 | 93,7 |
| **otra_imagen (control negativo)** | **58,6** | **36,2** |

## 4. Separación en `val` (alteraciones leves vs. imagen distinta)

Margen = mínimo de las alteraciones leves − máximo de "imagen distinta" (positivo = separación completa).

| Modalidad | Nivel | Máx. imagen distinta | Mín. alteración leve | Margen |
|---|---|---|---|---|
| mandalas | difícil | 75,5 | 75,0 | −0,5 |
| mandalas | fácil | 57,5 | 88,9 | 31,4 |
| mandalas | intermedio | 72,6 | 81,6 | 9,0 |
| siluetas | difícil | 68,2 | 85,5 | 17,3 |
| siluetas | fácil | 36,8 | 88,9 | 52,1 |
| siluetas | intermedio | 45,1 | 80,5 | 35,4 |

## 5. Efecto de la tolerancia (mandalas, `val`)

| Tolerancia (px) | AUC fácil | AUC intermedio | AUC difícil |
|---|---|---|---|
| 2 | 1,000 | 0,999 | 1,000 |
| 3 | 1,000 | 1,000 | 1,000 |
| 4 | 1,000 | 1,000 | 0,998 |

## 6. Evaluación final en `test`

| Modalidad | Nivel | AUC | Puntaje medio positivos | Puntaje medio negativos |
|---|---|---|---|---|
| mandalas | difícil | 0,906 | 89,3 | 70,1 |
| mandalas | fácil | 0,936 | 87,1 | 51,1 |
| mandalas | intermedio | 0,937 | 88,2 | 58,7 |
| siluetas | difícil | 0,994 | 92,0 | 48,4 |
| siluetas | fácil | 1,000 | 92,1 | 30,0 |
| siluetas | intermedio | 1,000 | 91,5 | 33,9 |

Cada fila usa 150 positivos (10 alteraciones × 15 imágenes, **incluida `identica`**) y 15 negativos.

## 7. Lectura honesta de los resultados

- Las siluetas se separan casi perfectamente; los mandalas difíciles son el caso más débil (AUC 0,906 en `test`, margen negativo en `val`).
- `escalado_grande` y `combinado` bajan mucho el puntaje de los mandalas (61,3 y 66,8 de media en `val`); conviene revisar la causa antes de la entrega.
- Como los positivos incluyen `identica`, el AUC es algo optimista.
- **Dibujos humanos reales:** pendientes. `pruebas_reales.csv` y la correlación de Spearman con valoración humana
  (celdas 6.1 y 6.2) se calculan cuando existan dibujos en `Dataset/dibujos_usuarios/`.
