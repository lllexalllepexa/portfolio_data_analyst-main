"""
Semantic search over product names with ChromaDB + sentence-transformers.
Run: python -m superstore.embeddings.chroma_products --query "office paper"
"""
from __future__ import annotations

import argparse
from pathlib import Path

import chromadb
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PARQUET = ROOT / "data" / "processed" / "orders_clean.parquet"
CHROMA_DIR = ROOT / "chroma_db"


def get_products(df: pd.DataFrame, limit: int = 3000) -> pd.DataFrame:
    prods = (
        df[["product_id", "product_name", "category", "sub_category"]]
        .drop_duplicates("product_id")
        .head(limit)
    )
    return prods


def build_collection(df: pd.DataFrame) -> chromadb.Collection:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(
        name="products",
        metadata={"hnsw:space": "cosine"},
    )
    if collection.count() > 0:
        return collection

    prods = get_products(df)
    docs = [
        f"{r.product_name} | {r.category} / {r.sub_category}"
        for r in prods.itertuples()
    ]
    collection.add(
        ids=prods["product_id"].astype(str).tolist(),
        documents=docs,
        metadatas=prods[["category", "sub_category"]].to_dict(orient="records"),
    )
    return collection


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="офисная бумага")
    parser.add_argument("--n", type=int, default=5)
    args = parser.parse_args()

    if not PARQUET.exists():
        raise SystemExit("Сначала ETL: python -m superstore.etl.load_and_clean")

    df = pd.read_parquet(PARQUET)
    col = build_collection(df)
    res = col.query(query_texts=[args.query], n_results=args.n)
    print(f"Запрос: {args.query}\n")
    for i, (doc, meta, dist) in enumerate(
        zip(res["documents"][0], res["metadatas"][0], res["distances"][0]), 1
    ):
        print(f"{i}. [расстояние {dist:.3f}] {doc}")
        print(f"   метаданные: {meta}\n")


if __name__ == "__main__":
    main()
