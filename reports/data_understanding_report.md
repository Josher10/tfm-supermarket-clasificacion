# Data Understanding — TFM BÁSICO CARM-FSE+
## Reporte Consolidado de Análisis Exploratorio

---

## Resumen Ejecutivo

Este reporte consolida los hallazgos de los dos notebooks de Entendimiento de Datos:
- **`01_data_understanding.ipynb`** — EDA orientado al negocio y storytelling para el tribunal.
- **`01b_data_understanding_technical.ipynb`** — EDA técnico-estadístico orientado a los datos.

Ambos operan sobre el fichero crudo `Dataset.csv` (separador `;`, formato europeo con comas decimales).

---

## Indicadores Clave del Dataset

| Indicador | Valor |
|---|---|
| **Total de registros (transacciones)** | ~643.880 filas |
| **Columnas** | 18 |
| **Supermercados participantes** | 5 |
| **PERMITIDO** | ~641.504 (99,63%) |
| **NO PERMITIDO** | ~2.376 (0,37%) |
| **Ratio de desbalance** | **270:1** |

> [!CAUTION]
> Un ratio 270:1 sitúa este problema en la categoría de **Extreme Imbalanced Classification**. Un clasificador naïve que prediga siempre "PERMITIDO" obtendría 99,63% de Accuracy, siendo operativamente inútil. La métrica Accuracy queda **descartada** como indicador de éxito.

---

## Diccionario de Datos (Schema)

| Columna | Descripción de Negocio | Rol en el Pipeline |
|---|---|---|
| `NOMBRE_EMPRESA` | Nombre del supermercado (5 distintos, cada uno con taxonomía propia) | Contexto de des-duplicación. **No se usa como feature de entrenamiento** |
| `ID_TARJETA` | Número de tarjeta de compra del cliente | Identificador operativo (no predictivo) |
| `COD_EAN` | Código de barras del producto | Weak predictor — EANs internos/irregulares y nulos reducen su fiabilidad |
| `ID_TICKETS` | Número del ticket del supermercado | Trazabilidad operativa |
| `DESCRIPCION_ARTICULO` | Descripción literal del producto comprado | **Feature exclusiva de entrenamiento del modelo NLP** |
| `UNIDAD_MEDIDA` | Medida de venta del producto | Feature auxiliar (no usada en entrenamiento) |
| `UNIDADES_ARTICULO` | Cantidad de artículos comprados | Feature auxiliar (no usada en entrenamiento) |
| `GRUPO` | Categoría principal (1=alimentación, 2=no alimentación) | Jerarquía taxonómica nivel 1 |
| `ID_SECCION` / `SECCION` | Partición de más alto nivel. Contexto global | Jerarquía taxonómica nivel 2 |
| `ID_FAMILIA` / `FAMILIA` | Agrupación por caso de uso o naturaleza | Feature taxonómica (solo Fase 1 determinista) |
| `ID_SUBFAMILIA` / `SUBFAMILIA` | Máxima resolución categórica. **Aquí reside la regla de negocio dura** | Target proxy para Listas Negras (Fase 1) |
| `IMPORTE_BRUTO` | Precio unitario antes de descuentos (coma decimal) | Feature económica — baja correlación con target |
| `IMPORTE_BASE` | Precio unitario después de descuentos (coma decimal) | Feature económica — baja correlación con target |
| `TIPO_IMPUESTOS` | IVA aplicado (entero, no porcentaje) | Feature auxiliar de impuestos |
| `ESTADO` | Define si el producto es Permitido o No Permitido | **Variable Target** |

---

## Hallazgos del EDA de Negocio (Notebook 01)

### Hallazgo 1 — Volumen y Viabilidad Computacional
Con ~643.000 transacciones, el volumen descarta el uso de LLMs genéricos o procesamiento masivo en la nube. Justifica empíricamente la arquitectura híbrida frugal ejecutable en Google Colab Free.

### Hallazgo 2 — Desbalance Extremo (270:1)
La inmensa mayoría de compras son lícitas. Un modelo que apruebe todo "por defecto" alcanza 99,6% de Accuracy pero falla en el 100% del fraude. Las métricas válidas son: **PR-AUC**, **Recall de NO PERMITIDO** y **F1-Macro**.

### Hallazgo 3 — Torre de Babel Taxonómica
Cada supermercado tiene su propia clasificación interna de familias y subfamilias. No existe un estándar interproveedor. Esto justifica que el modelo NLP se entrene **exclusivamente sobre el texto** (`DESCRIPCION_ARTICULO`), ya que es la única variable semánticamente comparable entre proveedores.

### Hallazgo 4 — Ruido Textual Extremo
Las descripciones de tickets presentan truncamientos ("LCH DESN T"), abreviaturas logísticas ("DET. LIQ. P/ROPA"), barras, puntos y descripciones de menos de 10 caracteres. Esto exige **N-gramas de caracteres (FastText)** para mitigar el problema de palabras fuera de vocabulario (OOV).

### Hallazgo 5 — Errores Humanos en el Etiquetado
Existen descripciones idénticas (dentro del mismo supermercado) catalogadas como PERMITIDO y NO PERMITIDO en diferentes ocasiones. Esto prueba que el sistema de IA **nunca debe actuar como juez autónomo**: toda incertidumbre se enruta forzosamente a la categoría **REVISAR** mediante umbrales probabilísticos (0.75 – 0.95).

---

## Hallazgos del EDA Técnico (Notebook 01b)

### Hallazgo 6 — Variables Numéricas con Baja Correlación
La matriz de correlación confirma que `IMPORTE_BRUTO`, `IMPORTE_BASE`, `UNIDADES_ARTICULO` y `TIPO_IMPUESTOS` tienen **baja correlación con el target**. Valida la decisión arquitectónica de entrenar exclusivamente con texto.

### Hallazgo 7 — Fiabilidad Limitada del COD_EAN
- Porcentaje significativo de EANs nulos o internos (no estándar 8/13 dígitos).
- Existencia de EANs con etiqueta contradictoria (mismo EAN → PERMITIDO y NO PERMITIDO).
- **Decisión:** El EAN se trata como *weak predictor* en la Fase 1, no como identificador fiable.

### Hallazgo 8 — Concentración Taxonómica de NO PERMITIDO
La `SUBFAMILIA` concentra reglas de negocio duras. Existen subfamilias donde el 100% de artículos son NO PERMITIDO (ej. bebidas alcohólicas, suavizantes, quitamanchas, ropa). Estas se explotan como **reglas deterministas previas al clasificador NLP**.

### Hallazgo 9 — Duplicados Masivos
La inmensa mayoría de las filas son transacciones repetidas del mismo producto. La des-duplicación por la tupla `[NOMBRE_EMPRESA, DESCRIPCION_ARTICULO, ESTADO, SUBFAMILIA]` reducirá dramáticamente el dataset sin perder información semántica.

### Hallazgo 10 — Distribución Textual por Clase
Las distribuciones de longitud (caracteres y tokens) de las descripciones son similares entre clases PERMITIDO y NO PERMITIDO. No existe un sesgo de longitud explotable — el modelo debe aprender patrones semánticos, no morfológicos.

---

## Estructura de los Notebooks

### `01_data_understanding.ipynb` — EDA de Negocio

| Sección | Contenido |
|---|---|
| Intro | Contexto FSE+ y objetivo para el tribunal |
| 1 | Volumen de datos y problema de memoria |
| 2 | Desbalance extremo y descarte de Accuracy |
| 3 | Asimetría semántica inter-supermercados |
| 4 | Ruido textual y justificación de FastText |
| 5 | Conflictos de etiquetado y Human-In-The-Loop |

### `01b_data_understanding_technical.ipynb` — EDA Técnico

| Sección | Contenido |
|---|---|
| 1 | Schema, tipos, nulos y cardinalidad + mapa de calor |
| 2 | Target: frecuencia absoluta, relativa y ratio |
| 3 | Estadísticos descriptivos numéricas + boxplots por ESTADO |
| 4 | Longitud textual (chars/tokens) + tabla de ruido |
| 5 | Cobertura EAN: estándar vs internos, contradicciones |
| 6 | Taxonomía: tasa NP por SECCION/FAMILIA/SUBFAMILIA |
| 7 | Distribución por NOMBRE_EMPRESA |
| 8 | Top 20 tokens discriminantes de NO PERMITIDO |
| 9 | Duplicados exactos y conflictos de etiquetado |
| 10 | Matriz de correlación con target binarizado |
| 11 | Resumen ejecutivo técnico |

---

## Instrucciones de Ejecución en Google Colab

> [!IMPORTANT]
> Siga estos pasos en orden estricto para evitar errores de memoria (OOM) en Colab Free.

```
1. Abrir Google Colab: https://colab.research.google.com
2. Subir el notebook: Archivo → Subir notebook → seleccionar el .ipynb deseado
3. Subir el dataset: pestaña lateral "Archivos" → subir Dataset.csv a /content/
4. Ejecutar: Entorno de ejecución → Ejecutar todo (Ctrl+F9)
5. Tiempo estimado en Colab Free (CPU): ~3-5 minutos por notebook
```

> [!WARNING]
> El fichero `Dataset.csv` usa **separador `;`** y **comas decimales**. Todos los notebooks ya manejan esto con `sep=';'` en la carga. No modificar el formato del CSV.

---

## Implicaciones Técnicas para el Pipeline

### Implicación 1 — Métrica de Evaluación
La **Accuracy** queda descartada. Se utilizará:
- `PR-AUC` (Precision-Recall Area Under Curve) como métrica principal
- `Recall` de la clase NO PERMITIDO como métrica de negocio
- `F1-Score macro` como métrica de equilibrio general

### Implicación 2 — Gestión del Desequilibrio
- **SMOTE descartado** (alta dimensionalidad vectorial genera muestras sintéticas inválidas)
- **`class_weight='balanced'`** obligatorio en `LinearSVC` y `LogisticRegression`
- La des-duplicación masiva reducirá naturalmente el ratio sin necesidad de under-sampling artificial

### Implicación 3 — Validación Cruzada
- **`StratifiedKFold`** para proteger la proporción de la clase minoritaria
- El modelo se entrena exclusivamente con `DESCRIPCION_ARTICULO`, agnóstico al proveedor

### Implicación 4 — Reglas Deterministas (Fase 1)
- Subfamilias con 100% NO PERMITIDO → regla directa sin ML
- Listas Negras léxicas explícitas (agua, alcohol, suavizantes, ropa, quitamanchas)
- `COD_EAN` como weak predictor complementario (no decisivo)
- Reglas segregadas por `NOMBRE_EMPRESA` (taxonomía no estándar)

### Implicación 5 — Descripciones Conflictivas
- Mismo texto + mismo supermercado → estados distintos → aislamiento en `conflictos_para_visto_bueno.csv`
- Resolución por el experto de dominio antes del entrenamiento
- En producción, productos con incertidumbre se enrutan forzosamente a **REVISAR**

---

## Próxima Fase

**Notebook:** `02_data_preparation.ipynb` (ya creado y auditado)

Tareas cubiertas:
- [x] Normalización profunda de `DESCRIPCION_ARTICULO` (puntos, barras, espacios múltiples)
- [x] Aislamiento de conflictos de etiquetado por supermercado
- [x] Des-duplicación conservadora → `diccionario_maestro.csv`
- [x] Validación de integridad post-limpieza (retención de clase minoritaria)
