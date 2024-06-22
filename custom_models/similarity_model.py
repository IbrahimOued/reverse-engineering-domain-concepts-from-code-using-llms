import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer, util

import mlflow
from mlflow.models.signature import infer_signature
from mlflow.pyfunc import PythonModel


class SimilarityModel(PythonModel):
    def load_context(self, context):
        """Load the model context for inference."""
        from sentence_transformers import SentenceTransformer

        try:
            self.model = SentenceTransformer.load(context.artifacts["model_path"])
        except Exception as e:
            raise ValueError(f"Error loading model: {e}")

    def predict(self, context, model_input, params):
        """Predict method for comparing similarity between two sentences."""
        from sentence_transformers import util

        if isinstance(model_input, pd.DataFrame):
            if model_input.shape[1] != 2:
                raise ValueError("DataFrame input must have exactly two columns.")
            sentence_1, sentence_2 = model_input.iloc[0, 0], model_input.iloc[0, 1]
        elif isinstance(model_input, dict):
            sentence_1 = model_input.get("sentence_1")
            sentence_2 = model_input.get("sentence_2")
            if sentence_1 is None or sentence_2 is None:
                raise ValueError(
                    "Both 'sentence_1' and 'sentence_2' must be provided in the input dictionary."
                )
        else:
            raise TypeError(
                f"Unexpected type for model_input: {type(model_input)}. Must be either a Dict or a DataFrame."
            )

        embedding_1 = self.model.encode(sentence_1)
        embedding_2 = self.model.encode(sentence_2)

        return np.array(util.cos_sim(embedding_1, embedding_2).tolist())