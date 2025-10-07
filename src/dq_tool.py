# dq_tools.py
from __future__ import annotations
from typing import Dict, Any
import pandas as pd
from src.register import register
import os
@register("inspect_schema", aliases=["tool:inspect_schema"])
def inspect_schema(*, dataset: pd.DataFrame) -> Dict[str, Any]:
    return {
        "rows": int(len(dataset)),
        "columns": list(dataset.columns),
        "dtypes": {c: str(t) for c, t in dataset.dtypes.items()},
        "summary": dataset.describe(include="all").fillna("").to_dict(),
    }

@register("check_missing", aliases=["tool:check_missing"])
def check_missing(*, dataset: pd.DataFrame) -> Dict[str, Any]:
    n_rows = int(len(dataset))
    if n_rows == 0:
        return {
            "rows": 0,
            "missing_per_column": {},
            "missing_pct_per_column": {},
            "all_complete": True,
            "columns_with_missing": [],
        }

    counts = dataset.isna().sum()
    pcts = (counts / n_rows * 100).round(2)

    return {
        "rows": n_rows,
        "missing_per_column": {col: int(counts[col]) for col in dataset.columns},
        "missing_pct_per_column": {col: float(pcts[col]) for col in dataset.columns},
        "all_complete": int(counts.sum()) == 0,
        "columns_with_missing": [col for col, c in counts.items() if int(c) > 0],
    }


@register("check_duplicates", aliases=["tool:check_duplicates"])
def check_duplicates(*, dataset: pd.DataFrame, id_col: str = "id") -> Dict[str, Any]:
    if id_col not in dataset.columns:
        raise ValueError(f"id_col '{id_col}' not in dataset")
    dup_mask = dataset.duplicated(subset=[id_col], keep=False)
    dup_rows = dataset[dup_mask]
    return {
        "duplicate_count": int(dup_rows.shape[0]),
        "duplicate_ids": dup_rows[id_col].tolist()[:200],  # cap to keep light
    }

@register("check_outliers", aliases=["tool:check_outliers"])
def check_outliers(*, dataset: pd.DataFrame, method: str = "iqr", z: float = 3.0) -> Dict[str, Any]:
    num = dataset.select_dtypes("number")
    if num.empty:
        return {"outliers_per_column": {}}

    out = {}
    if method == "iqr":
        q1, q3 = num.quantile(0.25), num.quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        for c in num.columns:
            mask = (num[c] < lower[c]) | (num[c] > upper[c])
            out[c] = int(mask.sum())
    else:  # z-score
        mean, std = num.mean(), num.std(ddof=0).replace(0, 1e-12)
        zscores = (num - mean) / std
        for c in num.columns:
            out[c] = int((zscores[c].abs() > z).sum())

    return {"method": method, "outliers_per_column": out}


if __name__ == "__main__":

    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    path = os.path.join(base_path,"data", "credit_risk_dataset.csv")
    
    data = pd.read_csv(path)
    
    print(inspect_schema(dataset=data))
    print(check_missing(dataset=data))
    print(check_outliers(dataset=data, method="z-score", z=3.0))
