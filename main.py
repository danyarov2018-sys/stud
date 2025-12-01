import os
import streamlit as st
from dotenv import dotenv_values
from groq import Groq

# --- 1. Вспомогательная функция для потоковой передачи ---

def parse_groq_stream(stream):
    """Парсит чанки из потокового ответа Groq."""
    for chunk in stream:
        if chunk.choices:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content

# --- 2. Конфигурация страницы и загрузка секретов ---

st.set_page_config(
    page_title="The Tech Buddy",
    page_icon="🤖",
    layout="centered",
)

# Загрузка секретов (.env локально, st.secrets в Streamlit Cloud)
try:
    # Пытаемся загрузить локально из .env
    secrets = dotenv_values(".env")
    # Проверка, что ключ есть, чтобы избежать KeyError
    if not secrets.get("GROQ_API_KEY"):
        raise KeyError("GROQ_API_KEY is missing in .env")
    
except Exception:
    # Если локальная загрузка не удалась, используем st.secrets (Streamlit Cloud)
    secrets = st.secrets

# Извлечение API ключа и других переменных
# Ключ будет доступен как в локальной, так и в облачной среде
try:
    GROQ_API_KEY = secrets["GROQ_API_KEY"]
    INITIAL_RESPONSE = secrets["INITIAL_RESPONSE"]
    INITIAL_MSG = secrets["INITIAL_MSG"]
    CHAT_CONTEXT = secrets["CHAT_CONTEXT"]
except KeyError as e:
    st.error(f"Ошибка: Не найден необходимый секрет {e}. Проверьте `secrets.toml` или `.env`.")
    st.stop()


# Инициализация клиента Groq
# ИСПОЛЬЗУЙТЕ ЯВНУЮ ПЕРЕДАЧУ КЛЮЧА для надежности
client = Groq(api_key=GROQ_API_KEY)

# --- 3. Логика приложения Streamlit ---

# Инициализация истории чата
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": INITIAL_RESPONSE}
    ]

st.title("Hey Buddy! 🤖")
st.caption("Your personal AI assistant")

# Отображение истории чата
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Пользовательский ввод
user_prompt = st.chat_input(INITIAL_MSG)

if user_prompt:
    # 1. Отображение сообщения пользователя
    with st.chat_message("user"):
        st.markdown(user_prompt)

    st.session_state.chat_history.append(
        {"role": "user", "content": user_prompt}
    )

    # 2. Подготовка контекста для API
    messages = [
        {"role": "system", "content": CHAT_CONTEXT},
        # INITIAL_MSG уже содержится в INITIAL_RESPONSE, 
        # но если вы хотите, чтобы это был отдельный токен, оставьте
        # {"role": "assistant", "content": INITIAL_MSG},
        *st.session_state.chat_history
    ]

    # 3. Ответ LLM (потоковая передача)
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            stream=True
        )
        response = st.write_stream(parse_groq_stream(stream))

    # 4. Сохранение ответа в историю
    st.session_state.chat_history.append(
        {"role": "assistant", "content": response}
    )





