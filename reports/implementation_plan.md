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

### Fase 2: Motor Léxico-Morfológico (Capa "Sparse")
> **Estado:** ⏳ `PLANIFICADO`
Construiremos el cerebro léxico puro diseñado para resistir las peores pesadillas ortográficas logísticas de los tickets como "B. CAL. ESP" o trunques masivos.
*   **Archivos:** `src/features/sparse_engine.py` o módulo dentro de un notebook estructurado.
*   **Acciones Técnicas:**
    *   **TF-IDF N-grams (Palabras):** Garantiza que cada token fuerte ("VINO") adquiera un índice matricial transparente para justificar matemáticamente cualquier corte (explicabilidad extrema).
    *   **Modelo fastText (N-gramas de caracteres):** Captura sub-palabras. Si la base conoce "LECHE", acercará al vector de espacio cualquier "LCH", "LECH" mitigando dinámicamente las palabras fuera de vocabulario (OOV) sin diccionarios a patadas.

---

### Fase 3: Fusión Semántica Destilada (Capa "Dense")
> **Estado:** ⏳ `PLANIFICADO`
Para aquellas oraciones polisémicas donde las reglas básicas fallan, usamos la potencia del espacio topológico.
*   **Archivos:** `src/features/dense_engine.py`
*   **Acciones Técnicas:**
    *   **Small Language Models (SLM):** Instanciación de un encoder Transformer ligero (ej. `paraphrase-multilingual-MiniLM-L12-v2`).
    *   **Destilación Estática (`Model2Vec`):** Requisito absoluto. Reduciremos la huella RAM del transformer topológico a menos de `~40MB` para el entorno de Google Colab, ganando hasta un `x500` en latencia pero logrando codificar incrustaciones densas (Embeddings) de alto nivel que concatenaremos matricialmente con el sub-vector de la Fase 2.

---

### Fase 4a: Modelado (Entrenamiento del Clasificador Híbrido)
> **Estado:** ⏳ `PLANIFICADO`
*   **Archivos:** `notebooks/03_modeling.ipynb`
*   **Acciones Técnicas:**
    *   **Inferencia NLP Pura:** Entrenamiento **exclusivo con `DESCRIPCION_ARTICULO`**, modelo 100% agnóstico al proveedor.
    *   **Clasificador Explicable Lineal:** `LinearSVC` o `Logistic Regression` sobre tensores Sparse+Dense.
    *   **Cost-Sensitive Learning:** `class_weight='balanced'` para penalizar errores en la clase minoritaria.

---

### Fase 4b: Evaluación, XAI y Human-In-The-Loop
> **Estado:** ⏳ `PLANIFICADO`
*   **Archivos:** `notebooks/04_evaluation.ipynb`
*   **Acciones Técnicas:**
    *   **Evaluación (Stratified K-Fold):** Curva PR-AUC, Recall minoritario, F1-Macro.
    *   **Explicabilidad (XAI):** Coeficientes del modelo lineal, importancia por n-grama.
    *   **Enrutamiento REVISAR:** Umbrales de certeza `< 0.75` y `< 0.95` para delegación forzosa a revisión humana.


## User Review Required

Revisa esta arquitectura del proyecto. 

*   ¿Estás de acuerdo con el esquema general diseñado para cubrir todas las fases de los algoritmos (y sus tácticas técnicas adaptativas a Google Colab)?
*   Si estás conforme, mi primera orden de trabajo inmediata será iniciar la codificación del embudo del sistema y limpieza, es decir, el Notebook `02_data_preparation.ipynb`.
