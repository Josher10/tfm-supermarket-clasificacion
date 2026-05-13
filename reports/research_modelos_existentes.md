# Investigación: Modelos Públicos Relacionados

> Fecha de investigación: 10 de mayo de 2026  
> Objetivo: Identificar modelos pre-entrenados públicos (Hugging Face, Kaggle, GitHub) que sean lo más cercano posible a nuestro problema de clasificación de ítems de tickets de supermercado en español.

---

## 🔑 Conclusión Ejecutiva

**No existe un modelo público listo para usar** (*off-the-shelf*) que clasifique productos de supermercado como PERMITIDO / NO PERMITIDO / REVISAR. Sin embargo, sí existen **piezas reutilizables** muy valiosas que pueden acelerar enormemente nuestro pipeline:

1. **Modelos base en español** para hacer fine-tuning sobre clasificación de texto.
2. **Modelos de embeddings multilingües ligeros** para vectorizar texto corto.
3. **Modelos zero-shot multilingües** para crear etiquetas sin datos de entrenamiento.

---

## 1. Modelos Base en Español (Fine-Tuning) — Hugging Face

Estos modelos no resuelven nuestro problema directamente, pero son los **cimientos ideales** para entrenar un clasificador con nuestros datos etiquetados.

| Modelo | Params | Descargas | Uso para el TFM | Link |
|---|---|---|---|---|
| `dccuchile/bert-base-spanish-wwm-cased` (BETO) | ~110M | Alto | Fine-tuning de clasificación texto corto en español. El más popular para NLP en español. | [🔗 HF](https://huggingface.co/dccuchile/bert-base-spanish-wwm-cased) |
| `PlanTL-GOB-ES/roberta-base-bne` | ~125M | Alto | Modelo del Plan TL del Gobierno de España, pre-entrenado con corpus de la Biblioteca Nacional. Excelente para texto formal español. | [🔗 HF](https://huggingface.co/PlanTL-GOB-ES/roberta-base-bne) |
| `microsoft/Multilingual-MiniLM-L12-H384` | ~117M | 35K+ | Versión compacta y multilingüe. **Ideal para Colab** por su bajo consumo de RAM. | [🔗 HF](https://huggingface.co/microsoft/Multilingual-MiniLM-L12-H384) |

> [!TIP]
> **Recomendación para el TFM:** `microsoft/Multilingual-MiniLM-L12-H384` es el mejor balance entre rendimiento y frugalidad para Colab. Si buscas máxima calidad en español y tienes GPU, usa `PlanTL-GOB-ES/roberta-base-bne`.

---

## 2. Modelos de Embeddings Multilingües Ligeros — Hugging Face

Estos modelos convierten texto corto a vectores numéricos. Son la **alternativa moderna a TF-IDF** y pueden alimentar directamente una Regresión Logística o SVM.

| Modelo | Params | Descargas | Uso para el TFM | Link |
|---|---|---|---|---|
| `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | ~118M | **46.7M** | ⭐ **TOP PICK.** Modelo de embeddings multilingüe más descargado. Ligero, rápido, excelente para texto corto. | [🔗 HF](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) |
| `intfloat/multilingual-e5-small` | ~118M | 7.7M | Alternativa competitiva. Buenos benchmarks en búsqueda semántica multilingüe. | [🔗 HF](https://huggingface.co/intfloat/multilingual-e5-small) |
| `sentence-transformers/distiluse-base-multilingual-cased-v2` | ~135M | 564K | Versión destilada. Más rápido en inferencia. | [🔗 HF](https://huggingface.co/sentence-transformers/distiluse-base-multilingual-cased-v2) |
| `hiiamsid/sentence_similarity_spanish_es` | ~118M | 62K | **Específico para español.** Fine-tuned sobre corpus en español. | [🔗 HF](https://huggingface.co/hiiamsid/sentence_similarity_spanish_es) |
| `ibm-granite/granite-embedding-107m-multilingual` | ~107M | 36K | IBM Granite. Ligero y moderno. Buen soporte multilingüe. | [🔗 HF](https://huggingface.co/ibm-granite/granite-embedding-107m-multilingual) |

> [!IMPORTANT]
> **Estrategia propuesta:** Usar `paraphrase-multilingual-MiniLM-L12-v2` para generar embeddings de cada línea de ticket → Alimentar esos vectores a una Regresión Logística con `class_weight='balanced'`. Esto combina la potencia semántica de un transformer con la explicabilidad de un modelo lineal.

---

## 3. Modelos Zero-Shot Multilingües — Hugging Face

Estos modelos pueden clasificar texto **sin necesitar datos de entrenamiento propios**. Funcionan dándoles etiquetas candidatas ("permitido", "no permitido", "revisar") y ellos predicen la más probable.

| Modelo | Params | Descargas | Uso para el TFM | Link |
|---|---|---|---|---|
| `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` | ~278M | **346K** | ⭐ **TOP PICK Zero-Shot.** El mejor modelo multilingual NLI público. Soporta español. | [🔗 HF](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7) |
| `MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli` | ~107M | 5.5K | Versión **mini** del anterior. Solo 107M params. **Ideal para Colab sin GPU.** | [🔗 HF](https://huggingface.co/MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli) |
| `Recognai/bert-base-spanish-wwm-cased-xnli` | ~110M | 3.1K | Zero-shot basado en BETO. **100% español nativo.** | [🔗 HF](https://huggingface.co/Recognai/bert-base-spanish-wwm-cased-xnli) |
| `Recognai/zeroshot_selectra_medium` | ~41M | 265 | Solo **41M params**. Extremadamente ligero. Español. | [🔗 HF](https://huggingface.co/Recognai/zeroshot_selectra_medium) |

> [!TIP]
> **Caso de uso inmediato:** Estos modelos son perfectos para una **Fase 0 de prototipado rápido.** Puedes, sin entrenar nada, pasarle "CERVEZA MAHOU 33CL" con las etiquetas `["producto permitido", "producto no permitido", "requiere revisión"]` y ver qué predice. Esto te da un baseline gratuito para comparar contra tu pipeline entrenado.



---

## 4. Estrategia Recomendada para el TFM

Basándome en la investigación, propongo esta combinación óptima:

```
┌─────────────────────────────────────────────────────────┐
│  FASE 0: BASELINE ZERO-SHOT (sin entrenamiento)        │
│  Modelo: Recognai/bert-base-spanish-wwm-cased-xnli     │
│  → Clasificación inmediata con etiquetas candidatas     │
├─────────────────────────────────────────────────────────┤
│  FASE 1: HEURÍSTICA LÉXICA (reglas)                    │
│  → Diccionario de palabras prohibidas (alcohol, etc.)   │
├─────────────────────────────────────────────────────────┤
│  FASE 2: EMBEDDINGS + CLASIFICADOR LINEAL              │
│  Vectorizador: paraphrase-multilingual-MiniLM-L12-v2   │
│  Clasificador: LogisticRegression(class_weight=balanced)│
│  → Combina potencia semántica + explicabilidad          │
├─────────────────────────────────────────────────────────┤
│  COMPARATIVA FINAL EN LA MEMORIA DEL TFM               │
│  Zero-Shot vs Heurística vs Embeddings+LR vs TF-IDF+LR │
└─────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> **Valor académico:** Incluir la comparativa de todas estas aproximaciones (zero-shot, reglas, TF-IDF clásico, embeddings densos) en la memoria del TFM demuestra criterio técnico y amplitud metodológica ante el tribunal.
