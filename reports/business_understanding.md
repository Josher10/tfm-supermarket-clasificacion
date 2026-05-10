# Fase 1: Comprensión del Negocio (Business Understanding)

## 1. Contexto del Proyecto y Antecedentes
El presente proyecto (TFM) se desarrolla en el marco normativo de un **programa de asistencia social**. Este programa proporciona asistencia y fondos para la adquisición de bienes de primera necesidad a familias y personas en situación de vulnerabilidad, requiriendo una justificación técnica estricta de cómo se está empleando el dinero público.

Parte crítica de esta justificación recae en la auditoría manual de los tickets de compra de supermercado (los cuales se consolidan en lo que denominamos el **"Fichero 03"**). Cada número de línea o producto adquirido y reportado debe ser evaluado sistemáticamente para asegurar que el uso de los fondos se ajusta a la legalidad y se destina de forma exclusiva a los artículos normativamente elegibles, apartando y bloqueando productos improcedentes (ej. alcohol, tabaco, ciertos lujos o productos no financiables).

## 2. Objetivos del Negocio (Business Objectives)
El objetivo primordial es concebir, diseñar e implementar un **sistema experto de apoyo a decisiones fundamentado en Inteligencia Artificial**. Este sistema debe servir de respaldo cognitivo directo a los auditores humanos en la clasificación constante de las líneas de producto del Fichero 03.
Sus utilidades principales derivadas son:
*   **Eficiencia Operativa:** Reducir en gran medida el tiempo humano en la validación al catalogar automáticamente los ítems obvios y frecuentes (tanto permitidos como prohibidos), concentrando la atención de los auditores exclusivamente sobre casos fronterizos o atípicos.
*   **Trazabilidad / Compliance Extremo:** Prevenir devoluciones o penalizaciones del programa. Las determinaciones arrojadas por la máquina han de ser racionales, legibles y sobre todo explicables ante una supervisión oficial. 
*   **Estabilidad en Criterios:** Asegurar consistencia, minorando el sesgo de clasificación y la disparidad de interpretaciones sobre las abreviaturas cortas de supermercado de diferentes validadores.

## 3. Criterios de Éxito del Negocio
*   Constatar la deducción de carga horaria global requerida por registro de cada "Fichero 03".
*   Procurar el filtrado severo de incidencias de clase `NO PERMITIDO`, acarreando un factor disuasorio ante auditorías.
*   Construir una herramienta interpretada positivamente, logrando la confianza de un usuario funcional no técnico gracias a una explicabilidad transparente y nítida.

## 4. Objetivos de Ciencia de Datos (Data Mining Objectives)
En base a la problemática expuesta, el enfoque a nivel de Datos se traduce como una tarea estructurada de NLP (Análisis de Textos Cortos) y Clasificación Multiclase.
*   **Taxonomía de Salida (3 Clases):** Todo producto o línea de texto será inyectado a la canalización y deberá proyectarse obligatoriamente respecto a las etiquetas meta:
    1.  `PERMITIDO` (Ítem subvencionable normal).
    2.  `NO PERMITIDO` (Veto normativo claro).
    3.  `REVISAR` (Escenarios no obvios por ambigüedad donde se emite una orden de delegación al humano).
*   **Enfoque Frugal Híbrido:** Elaborar un pipeline ad-hoc alejándonos de la dependencia o coste directo de LLMs genéricos, unificando bloqueos por reglas heurísticas y ML (Embeddings escasos + Claficadores interpretables lineales).
*   **Interpretación Activa:** Obtener junto con la etiqueta predicha, la cuantificación real o la palabra/n-grama de mayor propulsión a la clasificación final para dar soporte forense al caso.

## 5. Criterios de Éxito Técnico
*   **Evaluación sobre el Desbalance:** Como es un set real, se prevén abundantes items 'PERMITIDOS' contra ínfimos 'NO PERMITIDOS'. La Métrica Accuracy es un espejismo no aceptado. Todo se regirá por la búsqueda del mayor **F1-Score, F2-Score y PR-AUC**, maximizando el enfoque en la casuística de las clases minoritarias.
*   **Alta Sensibilidad (Recall) a la Denegación:** Prevalece fallar prediciendo un falso negativo que implique auditar humanos `REVISAR`, antes de permitir automáticamente algo del tipo `NO PERMITIDO`. 
*   **Viabilidad (Frugality Computacional):** Las iteraciones formativas, re-entrenamientos o inferencia global deben ser ejecutables sin provocar desbordamiento de memoria ni tiempos desorbitados, respetando el hardware facilitado por defecto de un entorno **Google Colab** (condiciones CPU/GPU estándares).

## 6. Restricciones, Limitaciones y Riesgos
*   **Restricción Infraestructural:** Ninguna dependencia de infra local pesada o créditos inasumibles de Cloud. Dependencia al 100% en las políticas temporales/hardware de Colab estándar.
*   **Datos Crudos Hostiles:** Las abreviaturas extremas, los tickets que unen la "marca" comercial y la tipología de manera indescifrable (ej: "G. PR. 500 CC"), el ruido inherente a los OCR si están presentes, y los errores propios por cajeros.
*   **Restricción por Reglamento Audit (Explicabilidad Obligada):** Sistemas que representen meras "cajas negras" tipo arquitecturas neuronales muy opacas (Transformers end-to-end sin LIME/SHAP explicativo nativo) corren gran riesgo académico. Se prefirirán invariablemente vías lineales de inspección de la ponderación de las características extraídas.

## 7. Directriz Tecnológica / Arquitectura Propuesta (High Level)
Se articulará la siguiente canalización tri-estado para certificar el proyecto bajo todo lo establecido:
1.  **Barrera Exigente por Reglas léxicas (Regex & Diccionarios):** Purgado automático y sin coste computacional (alta penalidad explicable) antes de pasar al motor ML.
2.  **Motor Vectorizador Escalable:** Transformación de las líneas alfabéticas sin incurrir a sobrecargas, vía embeddings escasos y clásicos TF-IDF o modelos densos livianos que procesen eficazmente texto corto.
3.  **Clasificador Lineal:** Enrutamiento hacia capas de machine learning clásico como Regresiones logísticas o SVM Lineales que habilitan la impresión de "pesos" del modelo asegurando transparencia total en las auditorías.
