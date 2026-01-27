"""
机器学习模型集成单元测试
"""
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.ml import FeatureBuilder, SimpleScoreModel, StockMLScorer


def test_feature_builder_shape():
    vec = FeatureBuilder.build({
        "pe_ratio": 20,
        "pb_ratio": 5,
        "roe": 0.2,
        "gross_margin": 0.6,
        "free_cash_flow": 1_000_000,
        "debt_ratio": 0.3,
    })
    assert isinstance(vec, np.ndarray)
    assert vec.shape == (6,)


def test_simple_score_model_predict():
    model = SimpleScoreModel()
    x = np.array([20, 5, 0.2, 0.6, 1_000_000, 0.3], dtype=float)
    score = model.predict_score(x)
    assert 0.0 <= score <= 10.0


def test_stock_ml_scorer_output():
    scorer = StockMLScorer()
    out = scorer.score_stock("600519", {
        "pe_ratio": 20,
        "pb_ratio": 5,
        "roe": 0.2,
        "gross_margin": 0.6,
        "free_cash_flow": 1_000_000,
        "debt_ratio": 0.3,
    })
    assert out["stock_code"] == "600519"
    assert "ml_score" in out
    assert "features" in out
