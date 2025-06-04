import streamlit as st
from openai import OpenAI
import time
import io

# python -m streamlit run chatbot.py

client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)

st.set_page_config(
    page_title="Chat with Phaenon",
    page_icon=":brain:",
    layout="centered"
)

# Styling
st.markdown(
    """
    <style>
    .stChatMessage.user {
        background-color: #0078ff;
        color: white;
        padding: 10px;
        border-radius: 10px;
    }
    .stChatMessage.assistant {
        background-color: #2b2b2b;
        color: white;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Session setup
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# Display previous messages
for msg in st.session_state.messages[1:]:
    if msg and isinstance(msg, dict) and "role" in msg and "content" in msg:
        avatar = msg.get("avatar", "🤖" if msg["role"] == "assistant" else "👁️")
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

# Chat input

def chat():
    st.sidebar.subheader("🤖 Phaenon - Chatbot")

    st.sidebar.image(r"C:\Users\samal\OneDrive\Desktop\project3\—Pngtree—cartoon rocket ship clipart illustration_17165822.png", width=250, caption="Phaenon Bot")
   
    user_input = st.sidebar.chat_input("Ask something...")

    if st.sidebar.button("🧹 Clear Chat History"):
        st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]
        st.rerun()

    txt = """The Phaenon Chatbot is an AI-powered conversational assistant designed to offer intelligent, human-like interactions. 
    Built using modern LLM (Large Language Model) APIs like DeepSeek or Google Generative AI and deployed through Streamlit, Phaenon combines sleek UI design with powerful backend AI processing to support a variety of user needs"""
    st.sidebar.info(txt)

    def export_chat(format="txt"):
        buffer = io.StringIO()
        for msg in st.session_state.messages[1:]:
            if not msg or not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                continue
            role = msg["role"].capitalize()
            content = msg["content"]
            avatar = msg.get("avatar", "")
            if format == "md":
                buffer.write(f"**{role}**: {avatar} \n{content}\n\n---\n\n")
            else:
                buffer.write(f"{role}: {avatar}\n{content}\n\n")
        return buffer.getvalue()

    download_format = st.sidebar.selectbox("📄 Export Format", ["txt", "md"])
    chat_data = export_chat(download_format)

    st.sidebar.download_button(
        label="💾 Download Chat",
        data=chat_data,
        file_name=f"phaenon_chat.{download_format}",
        mime="text/plain" if download_format == "txt" else "text/markdown"
    )

    if user_input:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "avatar": "👁️"
        })
        with st.chat_message("user", avatar="👁️"):
            st.markdown(user_input)

        try:
            # Try streaming first
            response = client.chat.completions.create(
                model="deepseek/deepseek-prover-v2:free",
                messages=st.session_state.messages,
                stream=True
            )

            with st.chat_message("assistant", avatar="🤖"):
                message_placeholder = st.empty()
                full_response = ""

                for chunk in response:
                    content = getattr(chunk.choices[0].delta, "content", "")
                    full_response += content
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.05)

                message_placeholder.markdown(full_response)

            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "avatar": "🤖"
            })

        except Exception as stream_error:
            print(f"[Streaming failed] {stream_error}")
            st.warning("⚠️ Chat crashed. History will be auto-cleared and retried.")

            # Preserve only the latest user input
            st.session_state.messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input, "avatar": "👁️"}
            ]

            try:
                # Retry without streaming
                response = client.chat.completions.create(
                    model="deepseek/deepseek-prover-v2:free",
                    messages=st.session_state.messages,
                    stream=False
                )
                full_response = response.choices[0].message.content

                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(full_response)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response,
                    "avatar": "🤖"
                })

            except Exception as fallback_error:
                st.error("❌ Still failed to respond. Please try again later.")
                print(f"[Fallback failed] {fallback_error}")
   
chat()