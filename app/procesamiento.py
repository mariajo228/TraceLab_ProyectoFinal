"""Preprocesamiento de imágenes de TraceLab."""
import os
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps
from skimage.morphology import skeletonize

# Carpeta de datos. Por defecto: <repositorio>/data (misma estructura que la carpeta de Drive:
# Dataset/, documentacion/, resultados/). Se puede cambiar con la variable TRACELAB_RAIZ.
RAIZ = Path(os.environ.get("TRACELAB_RAIZ", Path(__file__).resolve().parent.parent / "data"))
DATASET = RAIZ / "Dataset"
DOCUMENTACION = RAIZ / "documentacion"
RESULTADOS = RAIZ / "resultados"
CSV_DIVISION = DOCUMENTACION / "division_dataset_v2.csv"

MODALIDADES = ["mandalas", "siluetas"]
NIVELES = ["facil", "intermedio", "dificil"]
TIEMPOS = {"facil": 10, "intermedio": 15, "dificil": 20}
EXTENSIONES = {".jpg", ".jpeg", ".png"}

LADO = 256
CONTENIDO = 224
LADO_MAX_ENTRADA = 1600


def cargar_gris(fuente):
    """Lee una imagen (ruta o archivo subido) y la devuelve en escala de grises."""
    img = ImageOps.exif_transpose(Image.open(fuente))
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        fondo = Image.new("RGBA", img.size, (255, 255, 255, 255))
        fondo.alpha_composite(img)
        img = fondo
    return np.array(img.convert("L"))


def _quitar_fondo_desigual(gris):
    """Corrige sombras/iluminación despareja (útil en fotos de dibujos en papel)."""
    k = max(15, (min(gris.shape) // 8) | 1)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    fondo = cv2.morphologyEx(gris, cv2.MORPH_CLOSE, kernel)
    fondo = cv2.GaussianBlur(fondo, (0, 0), k / 3)
    return cv2.divide(gris, np.maximum(fondo, 1), scale=255)


def binarizar(gris, normalizar_fondo=False):
    """Devuelve una máscara uint8 con la tinta en 255 y el fondo en 0."""
    g = cv2.GaussianBlur(gris, (3, 3), 0)
    borde = np.concatenate([g[0, :], g[-1, :], g[:, 0], g[:, -1]])
    if np.median(borde) < 127:
        g = 255 - g
    if normalizar_fondo:
        g = _quitar_fondo_desigual(g)
    if g.std() < 3:
        return np.zeros_like(g)
    _, bw = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    _, etiquetas, stats, _ = cv2.connectedComponentsWithStats(bw, connectivity=8)
    area_min = max(6, int(0.00005 * bw.size))
    conservar = stats[:, cv2.CC_STAT_AREA] >= area_min
    conservar[0] = False
    return np.where(conservar[etiquetas], 255, 0).astype(np.uint8)


def encuadrar(mascara):
    """Recorta al contenido, lo escala y lo centra en un lienzo LADO x LADO.

    Así el desplazamiento y el tamaño del dibujo no penalizan la comparación.
    """
    lienzo = np.zeros((LADO, LADO), np.uint8)
    ys, xs = np.nonzero(mascara)
    if xs.size == 0:
        return lienzo, {"aspecto": 1.0, "tinta": 0.0, "tamano": 0.0}
    recorte = mascara[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = recorte.shape
    info = {
        "aspecto": w / h,
        "tinta": float((recorte > 0).mean()),
        "tamano": max(h, w) / max(mascara.shape),
    }
    f = CONTENIDO / max(h, w)
    nuevo = cv2.resize(recorte, (max(1, round(w * f)), max(1, round(h * f))),
                       interpolation=cv2.INTER_AREA)
    nuevo = np.where(nuevo > 40, 255, 0).astype(np.uint8)
    h2, w2 = nuevo.shape
    y0, x0 = (LADO - h2) // 2, (LADO - w2) // 2
    lienzo[y0:y0 + h2, x0:x0 + w2] = nuevo
    return lienzo, info

def extraer_trazos(mascara, modalidad=None):
    """Convierte la máscara en trazos de 1 píxel."""

    m = mascara > 0

    if not m.any():
        return m

    return skeletonize(m)


def preparar(fuente, modalidad, foto=False):
    """Pipeline completo. `fuente` puede ser ruta, archivo subido o arreglo gris.

    foto=True activa la corrección de iluminación (dibujos fotografiados).
    """
    gris = fuente if isinstance(fuente, np.ndarray) else cargar_gris(fuente)
    if max(gris.shape) > LADO_MAX_ENTRADA:
        f = LADO_MAX_ENTRADA / max(gris.shape)
        gris = cv2.resize(gris, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
    bw = binarizar(gris, normalizar_fondo=foto)
    mascara, info = encuadrar(bw)
    return {"gris": gris, "mascara": mascara,
            "trazos": extraer_trazos(mascara, modalidad), "info": info}
