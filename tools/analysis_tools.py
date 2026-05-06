"""
数据分析工具集
用于 AnalysisAgent 执行具体分析任务，生成图表
"""
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import json
import os

DATA_PATH = "data/sales_data.csv"
FIGURES_PATH = "out/figures"

# 设置中文字体
plt.rcParams['axes.unicode_minus'] = False
try:
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
except:
    pass


def _load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def _ensure_figures_dir():
    os.makedirs(FIGURES_PATH, exist_ok=True)


# ── 分析工具1：销售趋势分析 ───────────────────────────────
def analyze_sales_trend(input: str = "") -> str:
    """按时间维度分析销售趋势，生成折线图"""
    df = _load_data()
    _ensure_figures_dir()

    # 尝试找时间列
    date_col = None
    for col in df.columns:
        if any(k in col.lower() for k in ['date', 'time', '日期', '时间', '月', 'month']):
            date_col = col
            break

    # 找销售额列
    amount_col = None
    for col in df.columns:
        if any(k in col.lower() for k in ['amount', 'sales', 'revenue', '销售', '金额', '收入', 'price', 'total']):
            amount_col = col
            break

    if not date_col or not amount_col:
        # 没有日期列就用索引分组
        result = {"总销售额": float(df.select_dtypes(include='number').iloc[:, 0].sum())}
        return json.dumps(result, ensure_ascii=False)

    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col])
    df['month'] = df[date_col].dt.to_period('M')
    monthly = df.groupby('month')[amount_col].sum().reset_index()
    monthly['month'] = monthly['month'].astype(str)

    # 画图
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly['month'], monthly[amount_col], marker='o', color='#2563eb', linewidth=2)
    ax.fill_between(range(len(monthly)), monthly[amount_col], alpha=0.1, color='#2563eb')
    ax.set_title('月度销售趋势', fontsize=14, pad=15)
    ax.set_xlabel('月份')
    ax.set_ylabel('销售额')
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()

    fig_path = f"{FIGURES_PATH}/sales_trend.png"
    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    plt.close()

    result = {
        "月度销售数据": monthly.to_dict(orient='records'),
        "总销售额": float(monthly[amount_col].sum()),
        "最高月份": str(monthly.loc[monthly[amount_col].idxmax(), 'month']),
        "最低月份": str(monthly.loc[monthly[amount_col].idxmin(), 'month']),
        "图表路径": fig_path
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


# ── 分析工具2：商品品类分析 ───────────────────────────────
def analyze_category_performance(input: str = "") -> str:
    """分析各商品品类的销售表现，生成柱状图和饼图"""
    df = _load_data()
    _ensure_figures_dir()

    # 找品类列
    cat_col = None
    for col in df.columns:
        if any(k in col.lower() for k in ['category', 'type', '类别', '品类', '分类', 'product']):
            cat_col = col
            break

    if not cat_col:
        return json.dumps({"错误": "未找到品类相关列"}, ensure_ascii=False)

    # 找数值列
    num_col = df.select_dtypes(include='number').columns
    if len(num_col) == 0:
        return json.dumps({"错误": "未找到数值列"}, ensure_ascii=False)
    val_col = num_col[0]

    cat_stats = df.groupby(cat_col)[val_col].agg(['sum', 'mean', 'count']).round(2)
    cat_stats.columns = ['总额', '均值', '数量']
    cat_stats = cat_stats.sort_values('总额', ascending=False)

    # 柱状图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    colors = ['#2563eb', '#16a34a', '#ea580c', '#7c3aed', '#dc2626', '#0891b2']
    bars = ax1.bar(cat_stats.index, cat_stats['总额'],
                   color=colors[:len(cat_stats)])
    ax1.set_title('各品类销售总额', fontsize=13)
    ax1.set_xlabel('品类')
    ax1.set_ylabel('销售总额')
    ax1.tick_params(axis='x', rotation=30)
    for bar, val in zip(bars, cat_stats['总额']):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                f'{val:.0f}', ha='center', va='bottom', fontsize=9)

    # 饼图
    ax2.pie(cat_stats['总额'], labels=cat_stats.index,
            colors=colors[:len(cat_stats)], autopct='%1.1f%%', startangle=90)
    ax2.set_title('各品类销售占比', fontsize=13)

    plt.tight_layout()
    fig_path = f"{FIGURES_PATH}/category_performance.png"
    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    plt.close()

    result = {
        "品类销售统计": cat_stats.reset_index().to_dict(orient='records'),
        "销售最高品类": str(cat_stats.index[0]),
        "销售最低品类": str(cat_stats.index[-1]),
        "图表路径": fig_path
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


# ── 分析工具3：用户消费分析 ───────────────────────────────
def analyze_customer_behavior(input: str = "") -> str:
    """分析用户消费行为分布，生成直方图"""
    df = _load_data()
    _ensure_figures_dir()

    # 找用户相关列
    customer_col = None
    for col in df.columns:
        if any(k in col.lower() for k in ['customer', 'user', '用户', '客户', '买家', 'age', '年龄']):
            customer_col = col
            break

    num_cols = df.select_dtypes(include='number').columns.tolist()
    if len(num_cols) == 0:
        return json.dumps({"错误": "未找到数值列"}, ensure_ascii=False)

    val_col = num_cols[0]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 消费分布直方图
    axes[0].hist(df[val_col].dropna(), bins=20, color='#2563eb', edgecolor='white', alpha=0.8)
    axes[0].set_title(f'{val_col} 分布', fontsize=13)
    axes[0].set_xlabel(val_col)
    axes[0].set_ylabel('频次')

    # 如果有用户分组列，做分组箱线图
    if customer_col and df[customer_col].dtype == 'object':
        top_groups = df[customer_col].value_counts().head(6).index
        group_data = [df[df[customer_col]==g][val_col].dropna().values
                     for g in top_groups]
        bp = axes[1].boxplot(group_data, labels=top_groups, patch_artist=True)
        colors = ['#2563eb', '#16a34a', '#ea580c', '#7c3aed', '#dc2626', '#0891b2']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        axes[1].set_title(f'各{customer_col}消费分布', fontsize=13)
        axes[1].tick_params(axis='x', rotation=30)
    else:
        # 无分组列，画累积分布
        sorted_vals = df[val_col].dropna().sort_values()
        cumulative = [i/len(sorted_vals) for i in range(len(sorted_vals))]
        axes[1].plot(sorted_vals, cumulative, color='#16a34a', linewidth=2)
        axes[1].set_title('累积分布曲线', fontsize=13)
        axes[1].set_xlabel(val_col)
        axes[1].set_ylabel('累积比例')

    plt.tight_layout()
    fig_path = f"{FIGURES_PATH}/customer_behavior.png"
    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    plt.close()

    stats = df[val_col].describe().round(2).to_dict()
    result = {
        "消费统计": stats,
        "图表路径": fig_path
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


# ── 分析工具4：地区销售分析 ───────────────────────────────
def analyze_regional_sales(input: str = "") -> str:
    """分析各地区销售情况，生成水平柱状图"""
    df = _load_data()
    _ensure_figures_dir()

    region_col = None
    for col in df.columns:
        if any(k in col.lower() for k in ['region', 'location', 'area', '地区', '区域', '省', 'city', '城市']):
            region_col = col
            break

    if not region_col:
        return json.dumps({"提示": "数据中未找到地区相关列，跳过地区分析"}, ensure_ascii=False)

    num_cols = df.select_dtypes(include='number').columns
    if len(num_cols) == 0:
        return json.dumps({"错误": "未找到数值列"}, ensure_ascii=False)
    val_col = num_cols[0]

    regional = df.groupby(region_col)[val_col].sum().sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#2563eb' if v == regional.max() else '#93c5fd' for v in regional.values]
    bars = ax.barh(regional.index, regional.values, color=colors)
    ax.set_title('各地区销售总额', fontsize=13)
    ax.set_xlabel('销售总额')
    for bar, val in zip(bars, regional.values):
        ax.text(bar.get_width(), bar.get_y() + bar.get_height()/2.,
                f' {val:.0f}', va='center', fontsize=9)
    plt.tight_layout()

    fig_path = f"{FIGURES_PATH}/regional_sales.png"
    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    plt.close()

    result = {
        "地区销售数据": regional.reset_index().to_dict(orient='records'),
        "销售最高地区": str(regional.idxmax()),
        "销售最低地区": str(regional.idxmin()),
        "图表路径": fig_path
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


# ── 分析工具5：相关性分析 ─────────────────────────────────
def analyze_correlation(input: str = "") -> str:
    """分析数值列之间的相关性，生成热力图"""
    df = _load_data()
    _ensure_figures_dir()

    numeric_df = df.select_dtypes(include='number')
    if len(numeric_df.columns) < 2:
        return json.dumps({"提示": "数值列少于2列，无法做相关性分析"}, ensure_ascii=False)

    corr = numeric_df.corr().round(3)

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(corr.values, cmap='RdBu_r', vmin=-1, vmax=1)
    plt.colorbar(im, ax=ax)
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=45, ha='right')
    ax.set_yticklabels(corr.columns)
    for i in range(len(corr.columns)):
        for j in range(len(corr.columns)):
            ax.text(j, i, f'{corr.values[i, j]:.2f}',
                   ha='center', va='center', fontsize=9,
                   color='white' if abs(corr.values[i, j]) > 0.5 else 'black')
    ax.set_title('数值列相关性热力图', fontsize=13)
    plt.tight_layout()

    fig_path = f"{FIGURES_PATH}/correlation_heatmap.png"
    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    plt.close()

    result = {
        "相关性矩阵": corr.to_dict(),
        "强相关对": [],
        "图表路径": fig_path
    }
    # 找出强相关对
    for i in range(len(corr.columns)):
        for j in range(i+1, len(corr.columns)):
            val = corr.values[i][j]
            if abs(val) > 0.5:
                result["强相关对"].append({
                    "列1": corr.columns[i],
                    "列2": corr.columns[j],
                    "相关系数": val
                })
    return json.dumps(result, ensure_ascii=False, indent=2)


def create_analysis_registry():
    """创建数据分析工具注册表"""
    from tool_registry import ToolRegistry
    registry = ToolRegistry()

    registry.register(
        "analyze_sales_trend",
        "按时间维度分析销售趋势，输出月度销售数据和折线图"
    )(analyze_sales_trend)

    registry.register(
        "analyze_category_performance",
        "分析各商品品类的销售表现，输出品类销售统计和柱状图/饼图"
    )(analyze_category_performance)

    registry.register(
        "analyze_customer_behavior",
        "分析用户消费行为分布，输出消费统计和分布图"
    )(analyze_customer_behavior)

    registry.register(
        "analyze_regional_sales",
        "分析各地区销售情况，输出地区销售排名和水平柱状图"
    )(analyze_regional_sales)

    registry.register(
        "analyze_correlation",
        "分析数值列之间的相关性，输出相关性矩阵和热力图"
    )(analyze_correlation)

    return registry
