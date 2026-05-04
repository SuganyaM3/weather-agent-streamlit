
import os
import streamlit as st

st.set_page_config(page_title="Sunny Weather")


def setup_api_key():
    # 🔥 FORCE SET KEY (bypass Streamlit issues)
    os.environ["GOOGLE_API_KEY"] = "AIzaSyDJHEezL5OhNwpSP4RXlWzCuX278M4aBEA"

    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "0"


def main():
    setup_api_key()

    st.title("🌤️ Sunny Weather")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Ask weather"):

        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        from agent import ask_agent

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = ask_agent(prompt)

            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()    