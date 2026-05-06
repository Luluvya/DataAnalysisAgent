"""
数据探查工具集
用于 PlanningAgent 了解数据结构
"""
import pandas as pd
import json
import os

DATA_PATH = "data/sales_data.csv"

def _load_data() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"数据文件不存在: {DATA_PATH}")
    return pd.read_csv(DATA_PATH)


def get_data_overview(input: str = "") -> str:
    """获取数据概况：行数、列数、字段名、数据类型"""
    df = _load_data()
    info = {
        "行数": len(df),
        "列数": len(df.columns),
        "字段列表": list(df.columns),
        "数据类型": df.dtypes.astype(str).to_dict(),
        "前3行样本": df.head(3).to_dict(orient="records")
    }
    return json.dumps(info, ensure_ascii=False, indent=2)


def check_data_quality(input: str = "") -> str:
    """检查数据质量：缺失值、重复行、异常值"""
    df = _load_data()
    quality = {
        "缺失值统计": df.isnull().sum().to_dict(),
        "重复行数": int(df.duplicated().sum()),
        "各列唯一值数量": df.nunique().to_dict()
    }
    return json.dumps(quality, ensure_ascii=False, indent=2)


def get_numeric_stats(input: str = "") -> str:
    """获取数值列的统计特征：均值、中位数、最大最小值"""
    df = _load_data()
    numeric_cols = df.select_dtypes(include='number')
    if numeric_cols.empty:
        return "数据中没有数值列"
    stats = numeric_cols.describe().round(2).to_dict()
    return json.dumps(stats, ensure_ascii=False, indent=2)


def get_categorical_stats(input: str = "") -> str:
    """获取类别列的分布统计"""
    df = _load_data()
    cat_cols = df.select_dtypes(include='object')
    result = {}
    for col in cat_cols.columns:
        vc = df[col].value_counts().head(10)
        result[col] = vc.to_dict()
    return json.dumps(result, ensure_ascii=False, indent=2)


def create_exploration_registry():
    """创建数据探查工具注册表"""
    from tool_registry import ToolRegistry
    registry = ToolRegistry()

    registry.register(
        "get_data_overview",
        "获取数据概况，包括行数、列数、字段名和数据类型"
    )(get_data_overview)

    registry.register(
        "check_data_quality",
        "检查数据质量，包括缺失值统计、重复行数、各列唯一值数量"
    )(check_data_quality)

    registry.register(
        "get_numeric_stats",
        "获取数值列的统计特征，包括均值、中位数、最大最小值、分位数"
    )(get_numeric_stats)

    registry.register(
        "get_categorical_stats",
        "获取类别列的分布统计，显示各类别的频次"
    )(get_categorical_stats)

    return registry
