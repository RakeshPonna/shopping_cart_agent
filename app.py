"""
Streamlit UI for the AI Shopping Agent.
"""

import os

import streamlit as st
from dotenv import load_dotenv

from src.agent import ensure_database, run_agent

load_dotenv()

SAMPLE_QUESTIONS = [
    "Find me almonds under ₹500 with 4.5+ rating",
    "Show me cashews or pistachios under ₹550",
    "What raisins or dates do you have under ₹300?",
    "Show me all makhana and pumpkin seeds with ratings",
    "Show me dry fruit gift boxes",
    "Place an order for Vedaka Walnut Kernels",
]


def init_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None


def reset_chat() -> None:
    st.session_state.messages = []
    st.session_state.pending_prompt = None


def main() -> None:
    st.set_page_config(
        page_title="AI Shopping Agent",
        page_icon="🛒",
        layout="centered",
    )
    ensure_database()
    init_session_state()

    with st.sidebar:
        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            reset_chat()
            st.rerun()

        st.divider()
        st.subheader("Sample Questions")
        for idx, question in enumerate(SAMPLE_QUESTIONS):
            if st.button(question, key=f"sample_{idx}", use_container_width=True):
                st.session_state.pending_prompt = question
                st.rerun()

    st.title("🛒 AI Shopping Agent")
    st.caption("Ask about products, filter by price, organic status, or rating, and place orders.")

    if not os.getenv("GROQ_API_KEY"):
        st.warning(
            "GROQ_API_KEY is not set. Add `GROQ_API_KEY=...` to a `.env` file in the project root "
            "or export it in your environment before chatting."
        )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Ask for products or place an order...")
    prompt = user_input or st.session_state.pending_prompt
    if st.session_state.pending_prompt is not None:
        st.session_state.pending_prompt = None

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching catalog..."):
                try:
                    reply = run_agent(st.session_state.messages)
                except Exception as exc:
                    reply = f"Sorry, I encountered an error: {exc}"
            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
