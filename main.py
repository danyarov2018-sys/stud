import os
from dotenv import dotenv_values
import streamlit as st
from groq import Groq

# --- STREAMLIT PAGE CONFIG ---
st.set_page_config(
    page_title="The Tech Buddy 🧑‍💻",
    page_icon="🤖",
    layout="centered"
)

# --- LOAD SECRETS ---
try:
    # локальная разработка через .env
    secrets = dotenv_values(".env")
    GROQ_API_KEY = secrets["GROQ_API_KEY"]
except:
    # облако Streamlit
    secrets = st.secrets
    GROQ_API_KEY = secrets.get("GROQ_API_KEY")

# проверка ключа
if not GROQ_API_KEY:
    st.error("GROQ_API_KEY не найден! Проверьте Secrets.")
    st.stop()

# переменная окружения для Groq
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

INITIAL_RESPONSE = secrets.get("INITIAL_RESPONSE", "Hello!")
INITIAL_MSG = secrets.get("INITIAL_MSG", "I'm ready to chat!")
CHAT_CONTEXT = secrets.get("CHAT_CONTEXT", "You are a helpful assistant.")

# --- INIT GROQ CLIENT ---
try:
    client = Groq()
except Exception as e:
    st.error(f"Ошибка инициализации Groq: {e}")
    st.stop()

# --- INIT CHAT HISTORY ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": INITIAL_RESPONSE}
    ]

# --- STREAM PARSER ---
def parse_groq_stream(stream):
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# --- STREAMLIT UI ---
st.title("Hey Buddy! 🤓")
st.caption("Helping you level up your coding game")

# вывод истории
for message in st.session_state.chat_history:
    with st.chat_message(message["role"], avatar='🤖' if message["role"]=="assistant" else "🗨️"):
        st.markdown(message["content"])

# ввод пользователя
user_prompt = st.chat_input("Ask me anything!")

if user_prompt:
    # добавляем сообщение пользователя
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})
    with st.chat_message("user", avatar="🗨️"):
        st.markdown(user_prompt)

    # формируем сообщения для модели
    messages = [
        {"role": "system", "content": CHAT_CONTEXT},
        {"role": "assistant", "content": INITIAL_MSG},
        *st.session_state.chat_history
    ]

    # получаем поток от модели
    with st.chat_message("assistant", avatar='🤖'):
        stream = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            stream=True
        )
        response = st.write_stream(parse_groq_stream(stream))

    st.session_state.chat_history.append({"role": "assistant", "content": response})



