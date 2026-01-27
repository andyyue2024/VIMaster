"""
机器学习模型集成 - 使用现有财务指标训练简单的评分模型
"""
import json
import logging
import os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple, Callable

import numpy as np

try:
    from sklearn.linear_model import LinearRegression, LogisticRegression
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class MLFeatureVector:
    stock_code: str
    features: np.ndarray
    label: Optional[float] = None  # 可选真实评分或收益


class FeatureBuilder:
    """将 FinancialMetrics 转换为可用于模型训练/预测的特征向量"""

    FEATURE_NAMES = [
        "pe_ratio", "pb_ratio", "roe", "gross_margin",
        "free_cash_flow", "debt_ratio"
    ]

    @staticmethod
    def build(features_dict: Dict[str, Any]) -> np.ndarray:
        def safe_float(x):
            try:
                return float(x)
            except Exception:
                return 0.0
        return np.array([
            safe_float(features_dict.get("pe_ratio")),
            safe_float(features_dict.get("pb_ratio")),
            safe_float(features_dict.get("roe")),
            safe_float(features_dict.get("gross_margin")),
            safe_float(features_dict.get("free_cash_flow")),
            safe_float(features_dict.get("debt_ratio")),
        ], dtype=float)


class SimpleScoreModel:
    """
    一个轻量级的线性评分模型（无需外部依赖），按权重计算综合分数。
    分数越高代表基本面越好：高 ROE、高毛利、正向自由现金流、低负债、合理估值。
    """

    def __init__(self, weights: Optional[np.ndarray] = None):
        # 默认权重（可调）
        # pe_ratio、pb_ratio 权重为负（估值高为劣），其余为正
        self.weights = weights if weights is not None else np.array([
            -0.25,  # pe_ratio
            -0.15,  # pb_ratio
            0.35,   # roe
            0.20,   # gross_margin
            0.30,   # free_cash_flow
            -0.25,  # debt_ratio
        ], dtype=float)
        self.bias = 0.0

    def predict_score(self, x: np.ndarray) -> float:
        if x.shape[0] != self.weights.shape[0]:
            raise ValueError("Feature vector length mismatch")
        score = float(np.dot(self.weights, x) + self.bias)
        # 将分数限制在 [-10, 10]，再映射到 [0, 10]
        score = max(-10.0, min(10.0, score))
        score = (score + 10.0) / 2.0
        return round(score, 2)

    def fit(self, X: np.ndarray, y: np.ndarray, lr: float = 0.001, epochs: int = 200) -> None:
        """
        简单的梯度下降拟合（可选）。若没有标签数据，可以跳过使用默认权重。
        """
        if X.shape[1] != self.weights.shape[0]:
            raise ValueError("Feature dimension mismatch")
        w = self.weights.copy()
        b = self.bias
        for _ in range(epochs):
            preds = X.dot(w) + b
            error = preds - y
            grad_w = X.T.dot(error) / X.shape[0]
            grad_b = float(np.mean(error))
            w -= lr * grad_w
            b -= lr * grad_b
        self.weights = w
        self.bias = b

    def save(self, path: str, version: str = "v1") -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = {
            "weights": self.weights.tolist(),
            "bias": float(self.bias),
            "version": version,
            "feature_names": FeatureBuilder.FEATURE_NAMES,
            "type": "simple_linear",
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load(path: str) -> "SimpleScoreModel":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        model = SimpleScoreModel(weights=np.array(data.get("weights", []), dtype=float))
        model.bias = float(data.get("bias", 0.0))
        return model


class SklearnScoreModel:
    """可选依赖的 sklearn 模型封装（线性回归/逻辑回归）"""
    def __init__(self, task: str = "regression"):
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn 不可用，请安装后使用")
        if task == "regression":
            self.model = LinearRegression()
            self.task = "regression"
        else:
            self.model = LogisticRegression(max_iter=1000)
            self.task = "classification"
        self.bias = 0.0

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(X, y)

    def predict_score(self, x: np.ndarray) -> float:
        if self.task == "regression":
            score = float(self.model.predict(x.reshape(1, -1))[0])
        else:
            proba = float(self.model.predict_proba(x.reshape(1, -1))[0][1])
            score = proba * 10.0  # 映射到 0-10
        return round(max(0.0, min(10.0, score)), 2)

    def save(self, path: str, version: str = "v1") -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # 以 JSON 记录元数据 + numpy 权重（线性回归）
        meta = {"version": version, "task": self.task, "type": "sklearn"}
        try:
            coef = getattr(self.model, "coef_", None)
            intercept = getattr(self.model, "intercept_", None)
            data = {
                "meta": meta,
                "coef": coef.tolist() if coef is not None else None,
                "intercept": float(intercept) if intercept is not None else None,
                "feature_names": FeatureBuilder.FEATURE_NAMES,
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load(path: str) -> "SklearnScoreModel":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        task = data.get("meta", {}).get("task", "regression")
        model = SklearnScoreModel(task=task)
        coef = data.get("coef")
        intercept = data.get("intercept")
        if coef is not None:
            model.model.coef_ = np.array(coef, dtype=float)
        if intercept is not None:
            model.model.intercept_ = float(intercept)
        return model


def train_simple_model_from_dataset(X: np.ndarray, y: np.ndarray, lr: float = 0.001, epochs: int = 500) -> SimpleScoreModel:
    model = SimpleScoreModel()
    model.fit(X, y, lr=lr, epochs=epochs)
    return model


def train_sklearn_model_from_dataset(X: np.ndarray, y: np.ndarray, task: str = "regression") -> Optional[SklearnScoreModel]:
    if not SKLEARN_AVAILABLE:
        logger.warning("scikit-learn 不可用，跳过 sklearn 模型训练")
        return None
    model = SklearnScoreModel(task=task)
    model.fit(X, y)
    return model


class StockMLScorer:
    """面向项目的封装：从基本面 dict 构建特征并计算机器学习评分"""

    def __init__(self, model: Optional[SimpleScoreModel] = None):
        self.model = model or SimpleScoreModel()

    def score_stock(self, stock_code: str, financial_metrics: Dict[str, Any]) -> Dict[str, Any]:
        x = FeatureBuilder.build(financial_metrics)
        score = self.model.predict_score(x)
        return {
            "stock_code": stock_code,
            "ml_score": score,
            "features": {k: float(financial_metrics.get(k) or 0.0) for k in FeatureBuilder.FEATURE_NAMES},
            "explanation": "线性权重评分：估值越低、ROE/毛利越高、自由现金流越好、负债越低评分越高",
        }

    def score_portfolio(self, items: List[Tuple[str, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        results = []
        for code, fm in items:
            try:
                results.append(self.score_stock(code, fm))
            except Exception as e:
                logger.warning(f"ML 评分失败 {code}: {e}")
        return results


def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray, task: str = "regression") -> Dict[str, float]:
    """评估指标：回归(MSE/MAE)；分类(AUC/ACC)"""
    metrics: Dict[str, float] = {}
    if task == "regression":
        mse = float(np.mean((y_true - y_pred) ** 2))
        mae = float(np.mean(np.abs(y_true - y_pred)))
        metrics["mse"] = round(mse, 6)
        metrics["mae"] = round(mae, 6)
    else:
        # 简易 AUC/ACC 计算（不依赖 sklearn.metrics）
        # 假设 y_true in {0,1}，y_pred 为概率或分数
        try:
            # ACC
            preds = (y_pred >= 0.5).astype(int)
            acc = float(np.mean((preds == y_true).astype(float)))
            metrics["acc"] = round(acc, 6)
            # 近似 AUC：阈值扫描
            thresholds = np.linspace(0, 1, 101)
            tprs = []
            fprs = []
            for th in thresholds:
                p = (y_pred >= th).astype(int)
                tp = float(np.sum((p == 1) & (y_true == 1)))
                fp = float(np.sum((p == 1) & (y_true == 0)))
                fn = float(np.sum((p == 0) & (y_true == 1)))
                tn = float(np.sum((p == 0) & (y_true == 0)))
                tpr = tp / (tp + fn + 1e-9)
                fpr = fp / (fp + tn + 1e-9)
                tprs.append(tpr)
                fprs.append(fpr)
            # 排序并近似积分
            order = np.argsort(fprs)
            auc = 0.0
            for i in range(1, len(order)):
                x1, x2 = fprs[order[i-1]], fprs[order[i]]
                y1, y2 = tprs[order[i-1]], tprs[order[i]]
                auc += (x2 - x1) * (y1 + y2) / 2.0
            metrics["auc"] = round(auc, 6)
        except Exception:
            metrics["acc"] = 0.0
            metrics["auc"] = 0.0
    return metrics


def sklearn_grid_search_cv(
    X: np.ndarray,
    y: np.ndarray,
    task: str = "regression",
    param_grid: Optional[Dict[str, Any]] = None,
    cv: int = 5
) -> Optional[SklearnScoreModel]:
    """使用 sklearn Pipeline/GridSearch 进行交叉验证与超参选择（若可用）"""
    if not SKLEARN_AVAILABLE:
        logger.warning("scikit-learn 不可用，跳过 GridSearchCV")
        return None
    try:
        from sklearn.model_selection import GridSearchCV
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
        if task == "regression":
            base = LinearRegression()
        else:
            base = LogisticRegression(max_iter=1000)
        pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("model", base),
        ])
        # 默认网格
        if param_grid is None:
            if task == "regression":
                param_grid = {"model__fit_intercept": [True, False]}
            else:
                param_grid = {"model__C": [0.1, 1.0, 10.0]}
        gs = GridSearchCV(pipe, param_grid=param_grid, cv=cv, n_jobs=None)
        gs.fit(X, y)
        best_pipe = gs.best_estimator_
        # 提取模型到 SklearnScoreModel
        skl = SklearnScoreModel(task=task)
        skl.model = best_pipe.named_steps["model"]
        return skl
    except Exception as e:
        logger.warning(f"GridSearchCV 失败: {e}")
        return None

