"""Comparador de similitud visual de TraceLab (procesamiento clásico, sin entrenamiento)."""
from itertools import product

import cv2
import numpy as np
from skimage.metrics import structural_similarity

from procesamiento import LADO, preparar

TOLERANCIA = 4
ESCALA_CHAMFER = 8.0
PESOS = {"trazos": 0.5, "chamfer": 0.3, "estructura": 0.2}
ANGULOS = (-4, 0, 4)
DESPLAZAMIENTOS = (-5, 0, 5)
ESCALAS = (0.95, 1.0, 1.05)


def _distancia(trazos):
    """Mapa con la distancia de cada píxel al trazo más cercano."""
    if not trazos.any():
        return np.full(trazos.shape, 1e3, np.float32)
    return cv2.distanceTransform((~trazos).astype(np.uint8), cv2.DIST_L2, 3)


def _transformar(trazos, angulo, dx, dy, escala):
    c = LADO / 2
    M = cv2.getRotationMatrix2D((c, c), angulo, escala)
    M[:, 2] += (dx, dy)
    sal = cv2.warpAffine(trazos.astype(np.uint8), M, (LADO, LADO), flags=cv2.INTER_NEAREST)
    return sal > 0


def _f_trazos(ref, dib, d_ref):
    d_dib = _distancia(dib)
    p = float((d_ref[dib] <= TOLERANCIA).mean())
    c = float((d_dib[ref] <= TOLERANCIA).mean())
    return 2 * p * c / (p + c + 1e-9)


def alinear(ref, dib):
    """Busca el ajuste fino (giro, desplazamiento, escala pequeños) que mejor
    encaja el dibujo con la referencia. Parte de la identidad para que, en empate,
    no se mueva nada."""
    if not ref.any() or not dib.any():
        return dib
    d_ref = _distancia(ref)
    mejor, mejor_f = dib, _f_trazos(ref, dib, d_ref)
    for a, dx, dy, s in product(ANGULOS, DESPLAZAMIENTOS, DESPLAZAMIENTOS, ESCALAS):
        if (a, dx, dy, s) == (0, 0, 0, 1.0):
            continue
        cand = _transformar(dib, a, dx, dy, s)
        if not cand.any():
            continue
        f = _f_trazos(ref, cand, d_ref)
        if f > mejor_f + 1e-9:
            mejor, mejor_f = cand, f
    return mejor


def calcular_metricas(ref, dib):
    if not ref.any() or not dib.any():
        return {"precision": 0.0, "cobertura": 0.0, "f_trazos": 0.0,
                "chamfer_px": float(LADO), "estructura": 0.0}
    d_ref, d_dib = _distancia(ref), _distancia(dib)
    precision = float((d_ref[dib] <= TOLERANCIA).mean())
    cobertura = float((d_dib[ref] <= TOLERANCIA).mean())
    f = 2 * precision * cobertura / (precision + cobertura + 1e-9)
    chamfer = 0.5 * (float(d_ref[dib].mean()) + float(d_dib[ref].mean()))
    a = cv2.GaussianBlur(ref.astype(np.float32), (0, 0), 3)
    b = cv2.GaussianBlur(dib.astype(np.float32), (0, 0), 3)
    a /= max(float(a.max()), 1e-9)
    b /= max(float(b.max()), 1e-9)
    estructura = float(np.clip(structural_similarity(a, b, data_range=1.0, win_size=11), 0, 1))
    return {"precision": precision, "cobertura": cobertura, "f_trazos": f,
            "chamfer_px": chamfer, "estructura": estructura}


def puntaje(m):
    sub = {"trazos": m["f_trazos"],
           "chamfer": float(np.exp(-m["chamfer_px"] / ESCALA_CHAMFER)),
           "estructura": m["estructura"]}
    return 100 * sum(PESOS[k] * sub[k] for k in PESOS), sub


def categoria(p):
    if p >= 85: return "muy alta"
    if p >= 70: return "alta"
    if p >= 50: return "media"
    if p >= 30: return "baja"
    return "muy baja"


def explicar(m, info_ref, info_dib, p):
    t = [f"Similitud {categoria(p)} ({p:.0f} %).",
         f"Cobertura: {m['cobertura']*100:.0f} % de los trazos del original aparecen en tu dibujo "
         f"(tolerancia de ±{TOLERANCIA} px sobre un lienzo de {LADO} px).",
         f"Precisión: {m['precision']*100:.0f} % de tus trazos coincide con el original; "
         f"el resto son trazos que no están en la imagen."]
    r = info_dib["aspecto"] / max(info_ref["aspecto"], 1e-9)
    if abs(r - 1) > 0.15:
        t.append("Proporciones: tu dibujo es " + ("más ancho" if r > 1 else "más alto")
                 + " de lo que es el original.")
    else:
        t.append("Proporciones: el ancho y el alto generales son parecidos a los del original.")
    q = info_dib["tinta"] / max(info_ref["tinta"], 1e-9)
    if q > 1.8:
        t.append("Trazo: tu dibujo tiene bastante más tinta (trazos más gruesos o más elementos).")
    elif q < 0.55:
        t.append("Trazo: tu dibujo tiene bastante menos tinta (trazos más finos o menos elementos).")
    if m["cobertura"] < 0.5 and m["precision"] >= 0.6:
        t.append("Te faltaron partes del original, pero lo que dibujaste sí corresponde.")
    elif m["precision"] < 0.5 and m["cobertura"] >= 0.6:
        t.append("Reprodujiste gran parte del original, pero añadiste varios trazos que no estaban.")
    t.append("El porcentaje mide similitud visual de trazos y estructura tras normalizar posición y "
             "tamaño. No es una medida de memoria, inteligencia ni calidad artística.")
    return t


def comparar_preparadas(ref, dib):
    trazos_dib = alinear(ref["trazos"], dib["trazos"])
    m = calcular_metricas(ref["trazos"], trazos_dib)
    p, sub = puntaje(m)
    return {"puntaje": p, "subpuntajes": sub, "metricas": m,
            "trazos_ref": ref["trazos"], "trazos_dib": trazos_dib,
            "gris_ref": ref["gris"], "gris_dib": dib["gris"],
            "explicacion": explicar(m, ref["info"], dib["info"], p)}


def comparar(fuente_ref, fuente_dib, modalidad, foto=True):
    """Compara original y dibujo. foto=True para dibujos subidos por el usuario."""
    ref = preparar(fuente_ref, modalidad, foto=False)
    dib = preparar(fuente_dib, modalidad, foto=foto)
    if not dib["trazos"].any():
        raise ValueError("No se detectaron trazos en el dibujo. Revisa el contraste y la imagen.")
    return comparar_preparadas(ref, dib)


def superposicion(res):
    """Imagen RGB: verde = coincide, rojo = falta en tu dibujo, azul = sobra."""
    ref, dib = res["trazos_ref"], res["trazos_dib"]
    d_ref, d_dib = _distancia(ref), _distancia(dib)
    ok_ref = ref & (d_dib <= TOLERANCIA)
    ok_dib = dib & (d_ref <= TOLERANCIA)
    img = np.full((LADO, LADO, 3), 255, np.uint8)
    k = np.ones((3, 3), np.uint8)

    def pintar(mascara, color):
        img[cv2.dilate(mascara.astype(np.uint8), k) > 0] = color

    pintar(ref & ~ok_ref, (214, 39, 40))
    pintar(dib & ~ok_dib, (31, 119, 180))
    pintar(ok_ref | ok_dib, (44, 160, 44))
    return img
