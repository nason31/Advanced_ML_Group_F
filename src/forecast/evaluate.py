import numpy as np


def wrmsse(y_true: np.ndarray, y_pred: np.ndarray, weights: np.ndarray) -> float:
    """Weighted Root Mean Squared Scaled Error (simplified single-series form).

    weights is accepted for API compatibility but ignored in this single-series stub.
    """
    errors = y_true - y_pred
    scale = np.mean(np.diff(y_true) ** 2) + 1e-8
    return float(np.sqrt(np.mean(errors ** 2) / scale))
