"""
数据集加载与准备 - 支持从 CSV/Dict 构建训练数据
"""
import logging
from typing import List, Dict, Any, Tuple, Optional
import csv
import numpy as np

logger = logging.getLogger(__name__)

FEATURE_KEYS = [
    "pe_ratio", "pb_ratio", "roe", "gross_margin",
    "free_cash_flow", "debt_ratio"
]


def load_csv(file_path: str) -> Tuple[np.ndarray, np.ndarray]:
    """从 CSV 文件加载特征与标签
    需要列包含 FEATURE_KEYS + label
    """
    X: List[List[float]] = []
    y: List[float] = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                features = [float(row.get(k, 0) or 0) for k in FEATURE_KEYS]
                label = float(row.get("label", 0) or 0)
            except Exception:
                continue
            X.append(features)
            y.append(label)
    return np.array(X, dtype=float), np.array(y, dtype=float)


def from_dicts(items: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
    """从字典列表构建 (X, y)，每项应含 FEATURE_KEYS 和 label"""
    X: List[List[float]] = []
    y: List[float] = []
    for it in items:
        try:
            features = [float(it.get(k, 0) or 0) for k in FEATURE_KEYS]
            label = float(it.get("label", 0) or 0)
        except Exception:
            continue
        X.append(features)
        y.append(label)
    return np.array(X, dtype=float), np.array(y, dtype=float)
