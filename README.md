# AI Shopping Agent

An AI-powered shopping assistant prototype built with **LangChain**, **GroqCloud (`openai/gpt-oss-120b`)**, **Streamlit**, and **SQLite**, managed with **uv**.

Users can search and filter products (by keyword, category, INR price range, organic status, and customer rating), inspect product reviews, and place orders directly into the `orders` table.

## Tech Stack

- **Framework:** LangChain (`langchain`, `langchain-groq`, `langgraph`)
- **LLM:** `openai/gpt-oss-120b` via GroqCloud
- **UI:** Streamlit
- **Database:** SQLite (`resources/store.db`)
- **Package Manager:** `uv`

## Project Structure

```text
shopping_cart/
├── app.py                 # Streamlit chat UI (New Chat + Sample Questions sidebar)
├── pyproject.toml         # uv project dependencies
├── .env.example           # Environment variable template
├── resources/
│   └── store.db           # SQLite database (auto-created on startup)
└── src/
    ├── __init__.py
    ├── setup_db.py        # Creates tables and seeds 50 products & reviews (prices in INR)
    ├── reviews_api.py     # Aggregates average ratings and review counts
    └── agent.py           # LangChain agent + tools (search_products, get_product_details, place_order)
```

## Setup & Run

1. **Install dependencies** with `uv`:
   ```bash
   uv sync
   ```

2. **Configure your GroqCloud API key**:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and set your key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

3. **Initialize the database** (optional — `app.py` also initializes it automatically if missing):
   ```bash
   uv run python src/setup_db.py
   ```

4. **Start the Streamlit app**:
   ```bash
   uv run streamlit run app.py
   ```

## Example Prompts

- `Find me almonds under ₹500 with 4.5+ rating`
- `Show me cashews or pistachios under ₹550`
- `What raisins or dates do you have under ₹300?`
- `Show me all makhana and pumpkin seeds with ratings`
- `Show me dry fruit gift boxes`
- `Place an order for Vedaka Walnut Kernels`
