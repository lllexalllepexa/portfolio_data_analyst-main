"""
Разведочный анализ: Pandas, NumPy, Matplotlib.
Запуск: python -m superstore.analysis.eda
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from superstore.labels import CATEGORY_RU, COLUMNS_RU, translate_series
from superstore.labels import REGION_RU

ROOT = Path(__file__).resolve().parents[2]
PARQUET = ROOT / "data" / "processed" / "orders_clean.parquet"
FIG_DIR = ROOT / "data" / "processed" / "figures"

STAT_ROWS_RU = {
    "count": "число",
    "mean": "среднее",
    "std": "ст. откл.",
    "min": "мин",
    "25%": "25%",
    "50%": "медиана",
    "75%": "75%",
    "95%": "95%",
    "max": "макс",
    "skew": "асимметрия",
    "kurtosis": "эксцесс",
}


def load() -> pd.DataFrame:
    if not PARQUET.exists():
        from superstore.etl.load_and_clean import clean, resolve_raw

        df = pd.read_csv(resolve_raw(), low_memory=False)
        return clean(df)
    return pd.read_parquet(PARQUET)


def summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["sales", "profit", "quantity", "profit_margin", "delivery_days"]
    desc = df[cols].describe(percentiles=[0.25, 0.5, 0.75, 0.95]).T
    desc["skew"] = df[cols].skew()
    desc["kurtosis"] = df[cols].kurtosis()
    desc.index = [COLUMNS_RU.get(c, c) for c in desc.index]
    return desc.rename(columns=STAT_ROWS_RU)


def plot_revenue_by_region(df: pd.DataFrame) -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    agg = (
        df.groupby("region", as_index=False)["sales"]
        .sum()
        .sort_values("sales", ascending=True)
    )
    agg["region"] = translate_series(agg["region"], REGION_RU)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(agg["region"], agg["sales"], color=sns.color_palette("viridis", len(agg)))
    ax.set_xlabel("Выручка ($)")
    ax.set_title("Глобальный супермаркет — выручка по регионам")
    fig.tight_layout()
    out = FIG_DIR / "revenue_by_region.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out


def plot_profit_distribution(df: pd.DataFrame) -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    profits = df["profit"].dropna()
    q99 = profits.quantile(0.99)
    clipped = profits.clip(upper=q99)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(clipped, bins=60, density=True, alpha=0.7, color="#4C72B0", edgecolor="white")
    mu, sigma = clipped.mean(), clipped.std()
    x = np.linspace(clipped.min(), clipped.max(), 200)
    ax.plot(
        x,
        (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mu) / sigma) ** 2),
        "r-",
        lw=2,
        label=f"Норм. аппрокс. μ={mu:.1f}, σ={sigma:.1f}",
    )
    ax.set_xlabel("Прибыль ($, обрезка 99-й перцентиль)")
    ax.set_ylabel("Плотность")
    ax.set_title("Распределение прибыли и нормальная аппроксимация")
    ax.legend()
    fig.tight_layout()
    out = FIG_DIR / "profit_distribution.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out


def main() -> None:
    df = load()
    print("=== Размерность ===")
    print(df.shape)
    print("\n=== Описательная статистика ===")
    print(summary_stats(df).round(3))
    print("\n=== Топ категорий по прибыли ===")
    top = (
        df.groupby("category")["profit"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .round(2)
    )
    top.index = [CATEGORY_RU.get(i, i) for i in top.index]
    print(top)
    p1 = plot_revenue_by_region(df)
    p2 = plot_profit_distribution(df)
    print(f"\nГрафики: {p1}, {p2}")


if __name__ == "__main__":
    main()
