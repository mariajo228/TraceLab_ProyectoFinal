# Datos de TraceLab

Esta carpeta replica la estructura de la carpeta de Drive del proyecto
(`Proyecto Final - Tracelab`). **Las imágenes no se suben a GitHub**: pesan mucho, las
siluetas tienen otro propietario en Drive y los dibujos de usuarios son datos personales.

## Dónde descargar el dataset

- Dataset (1.200 imágenes): **[COMPLETAR: enlace de Drive con permiso de lectura]**

## Estructura esperada

```
data/
├── Dataset/
│   ├── mandalas/   facil/  intermedio/  dificil/   (300 imágenes por nivel)
│   ├── siluetas/   facil/  intermedio/  dificil/   (100 imágenes por nivel)
│   └── dibujos_usuarios/<modalidad>/               (se crea sola si el usuario consiente guardar)
├── documentacion/
│   └── division_dataset_v2.csv                     (partición train/val/test/reto)
└── resultados/
    └── registros_participantes.csv                 (se crea sola; NO se versiona)
```

## Cómo obtener `division_dataset_v2.csv`

- **Opción A:** copiar el archivo original desde Drive (`documentacion/`) a `data/documentacion/`.
- **Opción B:** generarlo con `python scripts/generar_division.py` (semilla 42, umbral Hamming 69).

Con otra ubicación para los datos, define la variable de entorno `TRACELAB_RAIZ`
apuntando a la carpeta que contiene `Dataset/`, `documentacion/` y `resultados/`.

## Nombres de los dibujos de usuarios

`<original_sin_extensión>__<participante>.<ext>`, por ejemplo `mandala_facil_004__p01234567.png`.
