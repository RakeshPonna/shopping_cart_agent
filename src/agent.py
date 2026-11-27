"""
AI Shopping Agent powered by LangChain and GroqCloud (openai/gpt-oss-120b).
"""

from __future__ import annotations

import json
import os
import sqlite3
from typing import Optional

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_groq import ChatGroq

from src.reviews_api import get_product_rating, get_ratings_for_products
from src.setup_db import DB_PATH, create_database

load_dotenv()

MODEL_NAME = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """You are a helpful AI Shopping Assistant for an online dry fruits, nuts, seeds, and snacks store.
All product prices are in Indian Rupees (INR / ₹). Available categories include: `nuts`, `dry-fruits`, `seeds`, and `snacks`.

You have access to tools to:
1. `search_products`: Search and filter products by keyword, category, price range (in INR), organic status, and minimum rating.
2. `get_product_details`: Get full details and customer reviews for a specific product by its ID.
3. `place_order`: Place an order for a specific product by its `product_id`.

Guidelines:
- Always use `search_products` when the user asks to find, browse, or filter products.
- Present matching products clearly with their Product ID, Name, Price (in ₹), Average Rating (with review count), and short description.
- When the user wants to order or buy an item:
  - If you already know the exact `product_id` from the conversation, call `place_order(product_id=...)`.
  - If the user refers to a product by name and you don't have its `product_id` yet, call `search_products` first to find the exact `product_id`.
  - If multiple products match ambiguously, ask the user which one they want to order before placing the order.
  - After `place_order` succeeds, confirm the order clearly with the Order ID, Product Name, Price (in ₹), and timestamp.
- Never invent products, prices, ratings, or order confirmations. Only report data returned by your tools.
"""


def ensure_database() -> None:
    """Create and seed store.db if it does not exist yet."""
    if not os.path.exists(DB_PATH):
        create_database()


def _get_connection() -> sqlite3.Connection:
    ensure_database()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@tool
def search_products(
    query: str = "",
    category: str = "",
    max_price: Optional[float] = None,
    min_price: Optional[float] = None,
    organic_only: bool = False,
    min_rating: Optional[float] = None,
) -> str:
    """Search for products in the store catalog with optional filters.

    Args:
        query: Keyword to match against product name, description, or category (e.g. "almonds", "cashews", "makhana", "dates").
        category: Exact category filter (e.g. "nuts", "dry-fruits", "seeds", "snacks").
        max_price: Maximum price in INR (inclusive).
        min_price: Minimum price in INR (inclusive).
        organic_only: Set to True to return only organic-verified products.
        min_rating: Minimum average customer rating from 0.0 to 5.0 (inclusive).
    """
    sql = "SELECT id, name, category, price, description, is_organic FROM products WHERE 1=1"
    params: list[object] = []

    if query.strip():
        like = f"%{query.strip().lower()}%"
        sql += " AND (LOWER(name) LIKE ? OR LOWER(description) LIKE ? OR LOWER(category) LIKE ?)"
        params.extend([like, like, like])

    if category.strip():
        sql += " AND LOWER(category) = LOWER(?)"
        params.append(category.strip())

    if max_price is not None:
        sql += " AND price <= ?"
        params.append(float(max_price))

    if min_price is not None:
        sql += " AND price >= ?"
        params.append(float(min_price))

    if organic_only:
        sql += " AND is_organic = 1"

    conn = _get_connection()
    try:
        rows = conn.execute(sql, params).fetchall()
    finally:
        conn.close()

    if not rows:
        return json.dumps({"products": [], "message": "No products matched your criteria."})

    product_ids = [row["id"] for row in rows]
    ratings_list = get_ratings_for_products(product_ids)
    ratings_map = {r["product_id"]: r for r in ratings_list}

    results = []
    for row in rows:
        rating_info = ratings_map.get(row["id"], {"average_rating": 0.0, "review_count": 0})
        avg_rating = rating_info["average_rating"]

        if min_rating is not None and avg_rating < float(min_rating):
            continue

        results.append(
            {
                "product_id": row["id"],
                "name": row["name"],
                "category": row["category"],
                "price": row["price"],
                "is_organic": bool(row["is_organic"]),
                "average_rating": avg_rating,
                "review_count": rating_info["review_count"],
                "description": row["description"],
            }
        )

    results.sort(key=lambda p: (-p["average_rating"], p["price"]))
    return json.dumps({"products": results, "count": len(results)})


@tool
def get_product_details(product_id: int) -> str:
    """Get detailed product information, average rating, and customer reviews for a product ID.

    Args:
        product_id: The numeric ID of the product.
    """
    conn = _get_connection()
    try:
        product = conn.execute(
            "SELECT id, name, category, price, description, is_organic FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()
        if not product:
            return json.dumps({"error": f"Product with id {product_id} was not found."})

        review_rows = conn.execute(
            "SELECT rating, reviewer_name, review_text FROM reviews WHERE product_id = ?",
            (product_id,),
        ).fetchall()
    finally:
        conn.close()

    rating_info = get_product_rating(product_id)
    return json.dumps(
        {
            "product_id": product["id"],
            "name": product["name"],
            "category": product["category"],
            "price": product["price"],
            "is_organic": bool(product["is_organic"]),
            "description": product["description"],
            "average_rating": rating_info["average_rating"],
            "review_count": rating_info["review_count"],
            "reviews": [
                {
                    "reviewer": r["reviewer_name"],
                    "rating": r["rating"],
                    "comment": r["review_text"],
                }
                for r in review_rows
            ],
        }
    )


@tool
def place_order(product_id: int) -> str:
    """Place an order for a specific product by inserting a record into the orders table.

    Args:
        product_id: The numeric ID of the product to order.
    """
    conn = _get_connection()
    try:
        product = conn.execute(
            "SELECT id, name, price FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()
        if not product:
            return json.dumps({"error": f"Cannot place order: product_id {product_id} does not exist."})

        cursor = conn.execute(
            "INSERT INTO orders (product_id, product_name, price) VALUES (?, ?, ?)",
            (product["id"], product["name"], product["price"]),
        )
        conn.commit()
        order_id = cursor.lastrowid
        order_row = conn.execute(
            "SELECT id, product_id, product_name, price, ordered_at FROM orders WHERE id = ?",
            (order_id,),
        ).fetchone()
    finally:
        conn.close()

    return json.dumps(
        {
            "status": "confirmed",
            "order_id": order_row["id"],
            "product_id": order_row["product_id"],
            "product_name": order_row["product_name"],
            "price": order_row["price"],
            "ordered_at": order_row["ordered_at"],
        }
    )


TOOLS = [search_products, get_product_details, place_order]


def create_shopping_agent(api_key: Optional[str] = None):
    """Build and return the compiled LangChain shopping agent."""
    resolved_key = api_key or os.getenv("GROQ_API_KEY")
    if not resolved_key:
        raise ValueError(
            "GROQ_API_KEY is not set. Add it to your .env file or environment variables."
        )

    llm = ChatGroq(
        model=MODEL_NAME,
        temperature=0,
        api_key=resolved_key,
    )
    return create_agent(
        model=llm,
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
    )


def run_agent(chat_history: list[dict[str, str]], api_key: Optional[str] = None) -> str:
    """Run the shopping agent on the given chat history and return the assistant's reply."""
    ensure_database()
    agent = create_shopping_agent(api_key=api_key)
    messages = [(msg["role"], msg["content"]) for msg in chat_history]
    result = agent.invoke({"messages": messages})
    final_message = result["messages"][-1]
    content = getattr(final_message, "content", "")
    if isinstance(content, list):
        return "\n".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        ).strip()
    return str(content).strip()
