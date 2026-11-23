"""Genera la división del dataset (train / val / test / reto) sin fuga de datos.

Equivale a la sección 2 del notebook: detecta casi duplicados con dHash + distancia de
Hamming, los agrupa y reparte cada grupo completo en un único conjunto, de forma
estratificada por modalidad y nivel.

Uso:
    python scripts/generar_division.py                 # usa data/ (o TRACELAB_RAIZ)
    python scripts/generar_division.py --sobrescribir  # reemplaza el CSV existente

Salida: <raiz>/documentacion/division_dataset_v2.csv
Nota: no mueve ni modifica ninguna imagen.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
from procesamiento import (CSV_DIVISION, DATASET, EXTENSIONES, MODALIDADES,  # noqa: E402
                           NIVELES)

LADO_HASH = 32
UMBRAL_HAMMING = 69
SEMILLA = 42
FRACCIONES = {"train": 0.50, "val": 0.15, "test": 0.15, "reto": 0.20}


def listar_imagenes(carpeta):
    return sorted(p for p in carpeta.iterdir() if p.suffix.lower() in EXTENSIONES)


def dhash(ruta, lado=LADO_HASH):
    img = Image.open(ruta).convert("L").resize((lado + 1, lado), Image.LANCZOS)
    a = np.asarray(img, dtype=np.int16)
    return (a[:, 1:] > a[:, :-1]).flatten()


def main(sobrescribir=False):
    filas = []
    for mod in MODALIDADES:
        for nivel in NIVELES:
            carpeta = DATASET / mod / nivel
            if not carpeta.exists():
                sys.exit(f"No existe {carpeta}. Revisa data/README.md.")
            for p in listar_imagenes(carpeta):
                filas.append({"ruta": p.relative_to(DATASET).as_posix(), "modalidad": mod,
                              "nivel": nivel, "hash": dhash(p)})
    df = pd.DataFrame(filas)
    print(f"Imágenes encontradas: {len(df)}")

    # Distancia de Hamming entre todos los pares
    H = np.stack(df["hash"].values).astype(np.float32)
    suma = H.sum(1)
    dist = suma[:, None] + suma[None, :] - 2 * (H @ H.T)
    iu, ju = np.where(np.triu(dist <= UMBRAL_HAMMING, k=1))
    pares = pd.DataFrame({"i": iu, "j": ju, "distancia": dist[iu, ju].astype(int)})
    pares = pares.sort_values("distancia").reset_index(drop=True)
    print(f"Pares con distancia <= {UMBRAL_HAMMING}: {len(pares)}")

    # Agrupar casi duplicados del mismo estrato (union-find)
    padre = list(range(len(df)))

    def raiz(x):
        while padre[x] != x:
            padre[x] = padre[padre[x]]
            x = padre[x]
        return x

    for i, j in zip(pares.i, pares.j):
        a, b = df.loc[i], df.loc[j]
        if (a.modalidad, a.nivel) == (b.modalidad, b.nivel):
            padre[raiz(i)] = raiz(j)
    df["grupo"] = [raiz(i) for i in range(len(df))]

    # Reparto estratificado por (modalidad, nivel) manteniendo cada grupo completo
    df["split"] = ""
    for (mod, nivel), sub in df.groupby(["modalidad", "nivel"]):
        tamanos = sub.groupby("grupo").size().sample(frac=1, random_state=SEMILLA)
        tamanos = tamanos.sort_values(ascending=False, kind="stable")
        objetivo = {s: f * len(sub) for s, f in FRACCIONES.items()}
        asignado = {s: 0 for s in FRACCIONES}
        for g, tam in tamanos.items():
            s = max(FRACCIONES, key=lambda k: objetivo[k] - asignado[k])
            df.loc[sub.index[sub["grupo"] == g], "split"] = s
            asignado[s] += tam

    print(pd.crosstab([df.modalidad, df.nivel], df.split, margins=True))

    # Verificación de fuga de datos
    mismo = pares[(df.loc[pares.i, ["modalidad", "nivel"]].values ==
                   df.loc[pares.j, ["modalidad", "nivel"]].values).all(1)]
    fuga = (df.loc[mismo.i, "split"].values != df.loc[mismo.j, "split"].values).sum()
    print(f"Casi duplicados del mismo estrato en conjuntos distintos: {fuga} (debe ser 0)")

    if CSV_DIVISION.exists() and not sobrescribir:
        sys.exit(f"Ya existe {CSV_DIVISION}; usa --sobrescribir para reemplazarlo.")
    CSV_DIVISION.parent.mkdir(parents=True, exist_ok=True)
    (df.drop(columns="hash")
       .assign(semilla=SEMILLA, umbral_hamming=UMBRAL_HAMMING, lado_hash=LADO_HASH)
       .to_csv(CSV_DIVISION, index=False))
    print(f"Guardado: {CSV_DIVISION}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sobrescribir", action="store_true")
    main(ap.parse_args().sobrescribir)
