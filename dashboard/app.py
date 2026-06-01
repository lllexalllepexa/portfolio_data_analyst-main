"""Run: .\\scripts\\run_streamlit.ps1"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

from superstore.labels import (
    CATEGORY_RU,
    REGION_RU,
    SEGMENT_RU,
    for_display,
    translate_series,
)
PARQUET = ROOT / "data" / "processed" / "orders_clean.parquet"
DUCKDB = ROOT / "data" / "processed" / "superstore.duckdb"

ВСЕ_РЕГИОНЫ = "Все"


@st.cache_data
def load_data() -> pd.DataFrame:
    if PARQUET.exists():
        return pd.read_parquet(PARQUET)
    if DUCKDB.exists():
        con = duckdb.connect(str(DUCKDB), read_only=True)
        try:
            return con.execute("SELECT * FROM orders").df()
        finally:
            con.close()
    st.error("Сначала запустите ETL: `python -m superstore.etl.load_and_clean`")
    st.stop()


def main() -> None:
    st.set_page_config(page_title="Глобальный супермаркет", layout="wide")
    st.title("Глобальный супермаркет — аналитическая панель")
    st.caption("Global Superstore · 2011–2014")

    df = load_data()
    regions_ru = [ВСЕ_РЕГИОНЫ] + sorted(
        translate_series(df["region"].dropna(), REGION_RU).unique().tolist()
    )
    years = sorted(df["year"].dropna().unique().astype(int).tolist())
    categories_ru = sorted(
        translate_series(df["category"].dropna(), CATEGORY_RU).unique().tolist()
    )

    c1, c2, c3 = st.columns(3)
    region_sel = c1.selectbox("Регион", regions_ru)
    year_from, year_to = c2.select_slider(
        "Годы", options=years, value=(min(years), max(years))
    )
    category_sel = c3.multiselect("Категория", categories_ru, default=None)

    f = df[(df["year"] >= year_from) & (df["year"] <= year_to)]
    if region_sel != ВСЕ_РЕГИОНЫ:
        inv_region = {v: k for k, v in REGION_RU.items()}
        region_en = inv_region.get(region_sel, region_sel)
        f = f[f["region"] == region_en]
    if category_sel:
        inv_cat = {v: k for k, v in CATEGORY_RU.items()}
        cats_en = [inv_cat.get(c, c) for c in category_sel]
        f = f[f["category"].isin(cats_en)]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Выручка", f"${f['sales'].sum():,.0f}")
    m2.metric("Прибыль", f"${f['profit'].sum():,.0f}")
    m3.metric("Маржа", f"{100 * f['profit'].sum() / max(f['sales'].sum(), 1):.1f}%")
    m4.metric("Строк заказов", f"{len(f):,}")

    tab1, tab2, tab3 = st.tabs(["Динамика", "Категории", "Сегменты"])

    with tab1:
        ts = (
            f.dropna(subset=["order_date"])
            .assign(month=lambda x: x["order_date"].dt.to_period("M").astype(str))
            .groupby("month", as_index=False)
            .agg(revenue=("sales", "sum"), profit=("profit", "sum"))
        )
        ts_disp = ts.rename(columns={"month": "месяц", "revenue": "выручка", "profit": "прибыль"})
        fig = px.line(
            ts_disp,
            x="месяц",
            y=["выручка", "прибыль"],
            markers=True,
            title="Помесячная динамика",
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        cat = f.groupby("category", as_index=False).agg(
            revenue=("sales", "sum"), profit=("profit", "sum")
        )
        cat["category"] = translate_series(cat["category"], CATEGORY_RU)
        cat = cat.rename(columns={"category": "категория", "revenue": "выручка", "profit": "прибыль"})
        fig_bar = px.bar(
            cat,
            x="категория",
            y="выручка",
            color="прибыль",
            title="Выручка по категориям",
            labels={
                "категория": "Категория",
                "выручка": "Выручка",
                "прибыль": "Прибыль",
            },
        )
        fig_bar.update_layout(coloraxis_colorbar_title="Прибыль")
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab3:
        seg = f.groupby("segment", as_index=False)["profit"].sum()
        seg["segment"] = translate_series(seg["segment"], SEGMENT_RU)
        seg = seg.rename(columns={"segment": "сегмент", "profit": "прибыль"})
        st.plotly_chart(
            px.pie(seg, names="сегмент", values="прибыль", title="Доля прибыли по сегментам"),
            use_container_width=True,
        )

    st.divider()
    st.subheader("Сводка по региону и году")
    table = (
        f.groupby(["region", "year"], as_index=False)
        .agg(revenue=("sales", "sum"), profit=("profit", "sum"), lines=("order_id", "count"))
        .sort_values(["region", "year"])
    )
    st.dataframe(for_display(table), use_container_width=True)


if __name__ == "__main__":
    main()
