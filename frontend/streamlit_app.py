import streamlit as st
import requests

st.title("🌦 Agentic Weather Assistant")

query = st.text_input(
    "Ask anything about the weather",
    placeholder="e.g. What's the weather, forecast and any alerts in Hyderabad?",
)

if st.button("Ask", disabled=not query.strip()):

    status = st.status("Processing request...", expanded=True)

    response = requests.post(
        "http://localhost:8000/weather/ask-stream",
        json={"query": query},
        stream=True,
    )

    status.write("Fetching weather data and generating response...")

    answer = ""
    placeholder = st.empty()

    for chunk in response.iter_content(chunk_size=1, decode_unicode=True):
        if chunk:
            answer += chunk
            placeholder.markdown(answer)

    status.update(label="Completed", state="complete")