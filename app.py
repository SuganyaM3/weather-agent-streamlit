
import os
import streamlit as st

st.set_page_config(
    page_title="Sunny - Weather Assistant",
    page_icon="🌤️",
    layout="centered",
)


# ── API Key Setup ─────────────────────────────────────────────────────────────
def setup_api_key():
    key = st.secrets.get("GOOGLE_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")

    if not key:
        st.error("""
🔑 API Key Missing!

Go to → Manage App → Secrets  
Add:

GOOGLE_API_KEY = "your-key"
""")
        st.stop()

    os.environ["GOOGLE_API_KEY"] = key
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "0"


# ── Main App ──────────────────────────────────────────────────────────────────
def main():
    setup_api_key()

    st.title("🌤️ Sunny — Weather Assistant")
    st.caption("Powered by Google ADK + Gemini 2.5 Flash")

    # Sidebar
    with st.sidebar:
        st.header("📍 Supported Cities")
        for city in [
            "Chennai", "Mumbai", "Delhi",
            "Bangalore", "Hyderabad",
            "London", "New York", "San Francisco",
            "Tokyo", "Paris", "Sydney", "Dubai",
        ]:
            st.write(f"• {city}")

        st.divider()

        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": "👋 Hi! I am Sunny ☀️ Ask me weather!"
        }]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input
    if user_input := st.chat_input("Ask weather..."):

        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        from agent import ask_agent

        with st.chat_message("assistant"):
            with st.spinner("Checking weather..."):
                reply = ask_agent(user_input)

            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()    