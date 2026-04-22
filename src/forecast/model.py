import numpy as np
import lightgbm as lgb


def train(X: np.ndarray, y: np.ndarray) -> lgb.Booster:
    dtrain = lgb.Dataset(X, label=y)
    params = {"objective": "regression", "num_leaves": 31, "verbose": -1}
    return lgb.train(params, dtrain, num_boost_round=50)


def predict(model: lgb.Booster, X: np.ndarray) -> np.ndarray:
    return model.predict(X)
