# Guía de uso de la interfaz (GUI)

**Ejecutar:** `streamlit run app/app.py` y abrir `http://localhost:8501` (ver [instrucciones](INSTRUCCIONES_EJECUCION.md)).
En la parte superior hay una barra de progreso con los seis pasos.

## 1. Inicio
![Inicio](img/01_bienvenida.png)

Explica la experiencia en tres momentos: **observar**, **reproducir** y **descubrir**.
Pulsa **Comenzar experiencia →**.

## 2. Modalidad
![Modalidad](img/02_modalidad.png)

Elige **Mandalas** (simetrías y patrones concéntricos) o **Siluetas** (contornos y figuras).
**← Volver al inicio** regresa a la pantalla anterior.

## 3. Nivel
![Nivel](img/03_dificultad.png)

| Nivel | Tiempo de observación |
|---|---|
| Fácil | 10 s |
| Intermedio | 15 s |
| Difícil | 20 s |

## 4. Observación
![Observación](img/04_observacion.png)

1. Pulsa **Mostrar imagen** cuando estés listo: aparece un reto al azar y empieza la cuenta regresiva.
2. Memorízala. Al terminar el tiempo la imagen **desaparece** y la app pasa sola a la siguiente pantalla.

No cambies de pantalla ni recargues la página mientras corre el tiempo.

## 5. Carga del dibujo
![Carga](img/05_carga.png)

1. Dibuja lo que recuerdas, en papel o en digital.
2. Sube el archivo (**JPG, JPEG o PNG**).
3. *(Opcional)* Marca la casilla para autorizar que tu dibujo se guarde de forma **anónima** para las pruebas académicas.
4. Revisa la vista previa y pulsa **Analizar mi dibujo ✨**.

**Para una foto de buena calidad:** buena iluminación, el dibujo completo en el encuadre, trazo oscuro sobre fondo claro
y sin sombras fuertes ni fondos recargados.

## 6. Resultados
![Resultados](img/06_resultados.png)

- **Similitud visual:** porcentaje y categoría (muy alta, alta, media, baja o muy baja).
- **Comparación de imágenes:** original, tu reproducción y **mapa de diferencias**.
- **Interpretación del análisis:** cobertura, precisión, proporciones y trazos faltantes o añadidos.
- **Conoce cómo se calcula la similitud:** subpuntajes de coincidencia de trazos (50 %), Chamfer (30 %) y SSIM (20 %).

| Color del mapa | Significado |
|---|---|
| 🟢 Verde | Trazos que coinciden |
| 🔴 Rojo | Trazos del original que faltan en tu dibujo |
| 🔵 Azul | Trazos de tu dibujo que no están en el original |

Al final, **Jugar de nuevo** (misma modalidad, eliges nivel otra vez) o **Cambiar modalidad**.

> El porcentaje mide similitud visual de trazos y estructura. **No** mide memoria, inteligencia ni calidad artística.

## Mensajes de error

| Mensaje | Qué hacer |
|---|---|
| *No se detectaron trazos en el dibujo* | Sube una imagen con más contraste y mejor iluminación. |
| *No hay retos disponibles para esta combinación* | Falta la partición del dataset; ver `data/README.md`. |
| *Ocurrió un problema al procesar o guardar tu dibujo* | Reintenta con otro archivo JPG/PNG; revisa permisos de escritura en `data/`. |
