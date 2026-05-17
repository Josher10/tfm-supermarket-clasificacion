# Plan de Implementación Maestro: Proyecto TFM BÁSICO CARM-FSE+

## Descripción y Visión General
Este documento sirve como hoja de ruta técnica completa del proyecto. El sistema a desarrollar no es un clasificador binario simple, sino un **Pipeline Híbrido Multiestrato (Record Linkage + Machine Learning)** diseñado para ejecutarse frugalmente en un entorno restringido (Google Colab gratuito) mientras es capaz de dictaminar rigurosamente qué líneas de producto de los supermercados financiados incurren en prohibiciones regulatorias del fondo europeo.

La base estratégica es la protección drástica contra el riesgo "Falso Negativo" (validar fraude sin querer) y la garantía de **explicabilidad matemática** frente a tribunales o auditores.

---

## 🏗️ Fases del Desarrollo

### Fase 0a: Entendimiento de Negocio (EDA Storytelling)
> **Estado:** ✅ `COMPLETADO`
*   **Archivos:** `notebooks/01_data_understanding.ipynb`
*   **Resultados Logrados:** Análisis orientado al tribunal: contexto FSE+, desbalance extremo (270:1), justificación de la arquitectura híbrida.

### Fase 0b: Entendimiento de Datos (EDA Técnico-Estadístico)
> **Estado:** 🚧 `EN DESARROLLO`
*   **Archivos:** `notebooks/01b_data_understanding_technical.ipynb`
*   **Acciones Técnicas:**
    *   Análisis de schema, tipos de dato, nulos y cardinalidad por columna.
    *   Distribución estadística de variables numéricas (`IMPORTE_BRUTO`, `IMPORTE_BASE`, `UNIDADES_ARTICULO`) segmentadas por `ESTADO`.
    *   Análisis de longitud textual (`DESCRIPCION_ARTICULO`): histogramas de caracteres y tokens.
    *   Cobertura y fiabilidad de `COD_EAN` (% nulos, EANs internos vs estándar).
    *   Mapa de calor de nulos, correlaciones numéricas y heatmap de concentración taxonómica.
    *   Top tokens discriminantes de la clase NO PERMITIDO (frecuencia diferencial).
    *   Detección de duplicados exactos y conflictos de etiquetado.

---

### Fase 1: Depuración Inteligente y Reglas Deterministas (Data Preparation)
> **Estado:** 🚧 `SIGUIENTE PASO`
El objetivo es transformar cientos de miles de transacciones ruidosas en un corpus manejable que Colab pueda procesar ágilmente.
*   **Archivos:** `notebooks/02_data_preparation.ipynb`
*   **Acciones Técnicas:**
    *   **Des-duplicación Conservadora:** Reducción del dataset masivo (`640k` filas) a un vocabulario maestro único agrupando la tupla de contexto: `[NOMBRE_EMPRESA, DESCRIPCION_ARTICULO, ESTADO, SUBFAMILIA]`.
    *   **Extracción de Inconsistencias:** Guardar directamente el "conflicto" (misma descripción con dos "Estados" opuestos) en `data/interim/conflictos_visto_bueno.csv` para auditoría experta.
    *   **Bloqueo Léxico (RapidFuzz):** Extracción automatizada de diccionarios de Listas Blancas/Negras usando como anclajes subfamilias flagrantes y palabras prohibidas por ley (ej. el agua, el alcohol, y el suavizante comercial).
*   **Salidas Esperadas:** `data/processed/diccionario_maestro.csv`, además de los mapas JSON por supermercado estandarizados.

### Fase 1.b: Análisis del Corpus Maestro Funcional (Post-Data Prep)
> **Estado:** 🚧 `SIGUIENTE PASO`
Una vez des-duplicado el fichero origen, y antes de entrenar la inteligencia artificial, generaremos un segundo análisis descriptivo para justificar el entorno de entreno.
*   **Archivos:** `notebooks/02b_data_understanding_post_prep.ipynb`
*   **Acciones Técnicas:**
    *   **EDA del Vocabulario Maestro:** Comprobar la espectacular reducción del volumen de filas y el nuevo ratio de desbalance real (único por clase) frente al tribunal.
    *   **Verificación Topológica:** Confirmar visualmente cuántos "conflictos" existían operativamente y cómo ha quedado la distribución real de artículos únicos por cada `NOMBRE_EMPRESA`.

---

### Fase 2: Vectorización — Motores de Representación Textual
> **Estado:** ⏳ `PLANIFICADO`

En lugar de fijar una arquitectura de concatenación Sparse+Dense a priori, se construirán **motores de vectorización independientes** que se evaluarán como candidatos separados en la Fase 4a. Que los datos decidan cuál es mejor.

#### 2.A — Motor Sparse (TF-IDF Dual)
*   **Archivos:** `src/features/sparse_engine.py`
*   **Estrategia:** TF-IDF con doble análisis:
    *   **N-gramas de palabras** `(1,2)` — Explicabilidad directa: cada dimensión del vector es un token legible ("VINO", "LECHE ENTERA").
    *   **N-gramas de caracteres** `(3,5)` con `char_wb` — Robustez ante truncamientos y abreviaturas ("LCH" ≈ "LECHE").
    *   Normalización L2 post-concatenación para equilibrar sub-espacios.
*   **Ventaja clave:** Explicabilidad total — los pesos del clasificador lineal señalan directamente qué n-gramas activaron la decisión.

#### 2.B — Motor Dense (Embeddings Semánticos)
*   **Archivos:** `src/features/dense_engine.py`
*   **Estrategia:** Encoder Transformer ligero (`paraphrase-multilingual-MiniLM-L12-v2`) para generar vectores densos de 384 dimensiones.
*   **Ventaja clave:** Captura sinonimia y semántica ("CERVEZA" ≈ "BIRRA") que TF-IDF no puede.
*   **Variante frugal (`Model2Vec`):** Destilación estática del Transformer a ~40MB, ganando hasta x500 en latencia manteniendo la semántica. Se evalúa como candidato adicional.

#### 2.C — Motor Zero-Shot (Baseline sin entrenamiento)
*   **Modelo:** `Recognai/bert-base-spanish-wwm-cased-xnli`
*   **Estrategia:** Clasificación inmediata con etiquetas candidatas `["producto permitido", "producto no permitido"]`, sin ningún entrenamiento.
*   **Ventaja clave:** Establece un baseline gratuito — si el sistema entrenado no supera significativamente al Zero-Shot, hay un problema de datos.

---

### Fase 3: Modelado — Ablation Study Comparativo
> **Estado:** ⏳ `PLANIFICADO`

**Cambio arquitectónico:** La arquitectura inicial planteaba concatenar Sparse+Dense en un clasificador único. Tras evaluar la naturaleza del dataset (~38K muestras, texto de 3-6 palabras, desbalance 47:1), se decidió **evaluar cada representación independientemente** para cuantificar la contribución real de cada componente.

*   **Archivos:** `notebooks/03_modeling.ipynb`

#### Modelos Candidatos

| ID | Representación | Clasificador | Explicable | RAM est. |
|---|---|---|---|---|
| M0 | Zero-Shot (sin entrenamiento) | Propio del modelo NLI | ⚠️ Parcial | ~500MB |
| M1 | TF-IDF word+char (Sparse) | LogisticRegression | ✅ Total | ~15MB |
| M2 | Embeddings MiniLM (Dense) | LogisticRegression | ⚠️ Vía LIME/SHAP | ~200MB |
| M3 | Model2Vec destilado (Dense frugal) | LogisticRegression | ⚠️ Vía LIME/SHAP | ~40MB |
| M4 | TF-IDF + Embeddings concatenados | LogisticRegression | ⚠️ Parcial | ~215MB |

#### Criterios de Selección (definidos a priori)

> **Estos criterios se fijan ANTES de ejecutar los experimentos para evitar sesgo de selección post-hoc.**

1.  **Métrica primaria:** `Recall de NO PERMITIDO` — El sistema debe detectar el máximo de productos prohibidos. Un Falso Negativo (aprobar fraude) es más grave que un Falso Positivo (bloquear algo permitido).
2.  **Métrica de desempate:** `F1-Macro` — Equilibrio general entre clases.
3.  **Umbral de significancia:** Diferencia > 2 puntos porcentuales. Si dos modelos difieren en < 2%, se consideran equivalentes.
4.  **Criterio de desempate final:** En caso de empate (< 2%), se selecciona el modelo con:
    *   Mayor **explicabilidad** (prioridad para auditoría de fondos públicos).
    *   Menor **huella computacional** (frugalidad para Colab Free).

#### Protocolo Experimental

*   **Validación:** `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)` — **Mismo split para TODOS los modelos**.
*   **Entrenamiento:** Exclusivo con `DESCRIPCION_ARTICULO` — modelo 100% agnóstico al proveedor.
*   **Cost-Sensitive Learning:** `class_weight='balanced'` en todos los clasificadores lineales.
*   **Significancia estadística:** Intervalos de confianza por bootstrap (1000 iteraciones) para validar que las diferencias no son varianza del fold.

---

### Fase 4: Evaluación, XAI y Human-In-The-Loop
> **Estado:** ⏳ `PLANIFICADO`
*   **Archivos:** `notebooks/04_evaluation.ipynb`
*   **Acciones Técnicas:**
    *   **Tabla comparativa final:** Recall NP, Precision NP, F1-Macro, PR-AUC, RAM, Explicabilidad para cada candidato.
    *   **Selección del modelo ganador** según los criterios pre-definidos en Fase 3.
    *   **Explicabilidad (XAI):** Coeficientes del modelo lineal (si Sparse gana), o LIME/SHAP (si Dense gana).
    *   **Enrutamiento REVISAR:** Umbrales de certeza `< 0.75` (REVISAR obligatorio) y `> 0.95` (decisión automática) para delegación forzosa a revisión humana.
    *   **Análisis de errores por FAMILIA/SECCION:** Diagnóstico post-hoc usando las columnas taxonómicas excluidas del entrenamiento para identificar patrones de fallo.

---

### Pipeline Final de Producción

```
Entrada: DESCRIPCION_ARTICULO (texto crudo del ticket)
    │
    ▼
┌──────────────────────────────────┐
│  CAPA 1: Reglas Deterministas    │  ← Listas Negras por SUBFAMILIA
│  (Alcohol, tabaco, etc.)         │     Explicabilidad: 100%
│  Resultado: NP directo           │
└────────────┬─────────────────────┘
             │ Si no matchea regla
             ▼
┌──────────────────────────────────┐
│  CAPA 2: Modelo ML Ganador       │  ← El mejor del Ablation Study
│  (TF-IDF / Embeddings / Model2Vec│     Seleccionado por datos
│   + LogisticRegression)          │
└────────────┬─────────────────────┘
             │ Probabilidad
             ▼
┌──────────────────────────────────┐
│  CAPA 3: Enrutamiento            │
│  > 0.95 → Decisión automática    │
│  0.75–0.95 → Sugerencia + humano │
│  < 0.75 → REVISAR (humano)       │
└──────────────────────────────────┘
```

> **Contribución académica:** La comparativa rigurosa entre técnicas simples (TF-IDF) y complejas (Transformers/Model2Vec) en un dominio real con fondos públicos demuestra criterio ingenieril y amplitud metodológica ante el tribunal. La contribución no es el algoritmo, sino el **pipeline auditable, frugal y explicable** diseñado para un caso operativo real.
