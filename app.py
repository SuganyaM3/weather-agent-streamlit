
import os
import streamlit as st

st.set_page_config(
    page_title="Sunny - Weather Assistant",
    page_icon="🌤️",
)

# ── API KEY ───────────────────────────────────────────────────────────────────
def setup_api_key():
    key = st.secrets.get("GOOGLE_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")

    if not key:
        st.error("Missing GOOGLE_API_KEY in Streamlit secrets.")
        st.stop()

    os.environ["GOOGLE_API_KEY"] = key
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "0"


# ── MAIN UI ───────────────────────────────────────────────────────────────────
def main():
    setup_api_key()

    st.title("🌤️ Sunny — Weather Assistant")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! Ask me weather 🌦️"}
        ]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask weather..."):

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        from agent import ask_agent

        with st.chat_message("assistant"):
            with st.spinner("Checking weather..."):
                reply = ask_agent(prompt)
            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
    