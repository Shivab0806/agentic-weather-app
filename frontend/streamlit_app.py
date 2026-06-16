import streamlit as st
import requests

st.title("🌦 Agentic Weather Assistant")

city = st.text_input("City")
query = st.text_input("Question")

if st.button("Ask"):

    status = st.status(
        "Processing Request...",
        expanded=True
    )

    status.write("Fetching weather information...")

    response = requests.post(
        "http://localhost:8000/weather/ask-stream",
        json={
            "city": city,
            "query": query
        },
        stream=True
    )

    status.write("Generating AI response...")

    answer = ""

    placeholder = st.empty()

    for chunk in response.iter_content(
        chunk_size=1,
        decode_unicode=True
    ):

        if chunk:
            answer += chunk
            placeholder.markdown(answer)

    status.update(
        label="Completed",
        state="complete"
    )