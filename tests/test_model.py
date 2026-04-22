import pytest
import numpy as np
from src.forecast.model import train, predict
from src.forecast.evaluate import wrmsse


def test_train_predict_shape():
    X = np.random.rand(100, 5).astype("float32")
    y = np.random.rand(100).astype("float32")
    model = train(X, y)
    preds = predict(model, X[:10])
    assert preds.shape == (10,)


def test_wrmsse_perfect():
    y = np.array([1.0, 2.0, 3.0])
    assert wrmsse(y, y, np.ones(3)) == pytest.approx(0.0, abs=1e-6)
