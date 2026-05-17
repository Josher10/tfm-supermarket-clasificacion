"""
Motor Léxico-Morfológico (Capa Sparse) — Fase 2 del TFM
=========================================================
Genera representaciones vectoriales dispersas (sparse) a partir
del texto corto de los tickets de supermercado.

Estrategia dual:
  1. TF-IDF con n-gramas de PALABRAS  → Explicabilidad directa (pesos por token).
  2. TF-IDF con n-gramas de CARACTERES → Robustez ante abreviaturas y OCR roto
     (ej. "LCH PASC" ~ "LECHE PASCUAL").

Restricciones de diseño:
  - Frugalidad: matrices sparse nativas (scipy.sparse), sin cargar en RAM densa.
  - Explicabilidad: cada dimensión del vector tiene un n-grama legible asociado.
  - Colab-safe: todo funciona en CPU con < 1GB de RAM.
"""

import numpy as np
import scipy.sparse as sp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from sklearn.base import BaseEstimator, TransformerMixin
import joblib
import os


class SparseEngine(BaseEstimator, TransformerMixin):
    """
    Motor de vectorización sparse dual (palabras + caracteres).

    Genera una matriz sparse concatenando horizontalmente:
      [TF-IDF palabras | TF-IDF caracteres]

    Parameters
    ----------
    word_ngram_range : tuple, default=(1, 2)
        Rango de n-gramas a nivel de palabra. (1,2) captura unigramas y bigramas
        como "LECHE" y "LECHE ENTERA".

    char_ngram_range : tuple, default=(3, 5)
        Rango de n-gramas a nivel de carácter. (3,5) captura sub-cadenas
        como "LEC", "LECH", "LECHE" para robustez ante truncamientos.

    max_features_word : int, default=10000
        Máximo de features del vectorizador de palabras.
        Limita la RAM en Colab.

    max_features_char : int, default=15000
        Máximo de features del vectorizador de caracteres.

    min_df : int, default=2
        Frecuencia mínima de documento. Elimina tokens que aparecen
        en menos de 2 descripciones (ruido / erratas únicas).

    max_df : float, default=0.95
        Frecuencia máxima de documento. Elimina tokens presentes
        en >95% de documentos (stop words implícitas como "DE", "CON").

    sublinear_tf : bool, default=True
        Aplica log(1 + tf) para suavizar la dominancia de tokens
        muy frecuentes dentro de una descripción.

    use_char : bool, default=True
        Si False, desactiva el vectorizador de caracteres (solo palabras).
    """

    def __init__(
        self,
        word_ngram_range=(1, 2),
        char_ngram_range=(3, 5),
        max_features_word=10_000,
        max_features_char=15_000,
        min_df=2,
        max_df=0.95,
        sublinear_tf=True,
        use_char=True,
    ):
        self.word_ngram_range = word_ngram_range
        self.char_ngram_range = char_ngram_range
        self.max_features_word = max_features_word
        self.max_features_char = max_features_char
        self.min_df = min_df
        self.max_df = max_df
        self.sublinear_tf = sublinear_tf
        self.use_char = use_char

        # Vectorizadores internos (se crean en fit)
        self._word_vec = None
        self._char_vec = None

    def fit(self, X, y=None):
        """
        Ajusta los vectorizadores TF-IDF al corpus.

        Parameters
        ----------
        X : array-like of str
            Descripciones de artículos (ej. "LECHE PASCUAL ENTERA 1L").
        """
        texts = self._validate_input(X)

        # --- Vectorizador de PALABRAS ---
        self._word_vec = TfidfVectorizer(
            analyzer='word',
            ngram_range=self.word_ngram_range,
            max_features=self.max_features_word,
            min_df=self.min_df,
            max_df=self.max_df,
            sublinear_tf=self.sublinear_tf,
            dtype=np.float32,  # float32 para ahorrar RAM en Colab
        )
        self._word_vec.fit(texts)

        # --- Vectorizador de CARACTERES ---
        if self.use_char:
            self._char_vec = TfidfVectorizer(
                analyzer='char_wb',  # char_wb respeta fronteras de palabra
                ngram_range=self.char_ngram_range,
                max_features=self.max_features_char,
                min_df=self.min_df,
                max_df=self.max_df,
                sublinear_tf=self.sublinear_tf,
                dtype=np.float32,
            )
            self._char_vec.fit(texts)

        return self

    def transform(self, X):
        """
        Transforma textos en matriz sparse [palabras | caracteres].

        Returns
        -------
        scipy.sparse.csr_matrix
            Matriz sparse de dimensión (n_samples, n_word_features + n_char_features).
        """
        texts = self._validate_input(X)

        X_word = self._word_vec.transform(texts)

        if self.use_char and self._char_vec is not None:
            X_char = self._char_vec.transform(texts)
            X_combined = sp.hstack([X_word, X_char], format='csr')
            # Normalización L2 post-concatenación: equilibra la contribución
            # de ambos sub-espacios para que el clasificador lineal no
            # ignore el sub-espacio con magnitudes TF-IDF más bajas.
            return normalize(X_combined, norm='l2')

        return X_word

    def get_feature_names(self):
        """Retorna nombres de features concatenados (palabras + caracteres)."""
        names = list(self._word_vec.get_feature_names_out())
        if self.use_char and self._char_vec is not None:
            names += [f'CHAR_{n}' for n in self._char_vec.get_feature_names_out()]
        return names

    @property
    def n_features_word(self):
        """Número de features del vectorizador de palabras."""
        if self._word_vec is None:
            return 0
        return len(self._word_vec.vocabulary_)

    @property
    def n_features_char(self):
        """Número de features del vectorizador de caracteres."""
        if self._char_vec is None:
            return 0
        return len(self._char_vec.vocabulary_)

    @property
    def n_features_total(self):
        """Número total de features (palabras + caracteres)."""
        return self.n_features_word + self.n_features_char

    def get_top_features_for_text(self, text, top_n=10):
        """
        Dado un texto, retorna los n-gramas con mayor peso TF-IDF.
        Útil para explicabilidad (XAI): "¿POR QUÉ se clasificó así?"

        Parameters
        ----------
        text : str
            Descripción del artículo.
        top_n : int
            Número de features a retornar.

        Returns
        -------
        list of tuple (feature_name, tfidf_weight)
        """
        vec = self.transform([text])
        feature_names = self.get_feature_names()
        row = vec.toarray().flatten()
        top_idx = row.argsort()[-top_n:][::-1]
        return [(feature_names[i], round(float(row[i]), 4)) for i in top_idx if row[i] > 0]

    def report(self):
        """Imprime un resumen del motor sparse."""
        print('=' * 55)
        print('  MOTOR SPARSE — Resumen de Vectorización')
        print('=' * 55)
        print(f'  Features de palabras:    {self.n_features_word:>8,}')
        print(f'  Features de caracteres:  {self.n_features_char:>8,}')
        print(f'  TOTAL dimensiones:       {self.n_features_total:>8,}')
        print(f'  Word n-grams:            {self.word_ngram_range}')
        print(f'  Char n-grams:            {self.char_ngram_range}')
        print(f'  min_df={self.min_df}, max_df={self.max_df}')
        print(f'  sublinear_tf={self.sublinear_tf}')
        print('=' * 55)

    def save(self, path):
        """Persiste el motor completo a disco (joblib)."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self, path)
        size_mb = os.path.getsize(path) / (1024 * 1024)
        print(f'✅ Motor sparse guardado: {path} ({size_mb:.1f} MB)')

    @staticmethod
    def load(path):
        """Carga un motor sparse desde disco."""
        engine = joblib.load(path)
        print(f'✅ Motor sparse cargado: {engine.n_features_total:,} features')
        return engine

    @staticmethod
    def _validate_input(X):
        """Asegura que el input sea una lista de strings."""
        if hasattr(X, 'tolist'):
            X = X.tolist()
        return [str(x) if not isinstance(x, str) else x for x in X]
