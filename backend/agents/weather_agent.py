import json
from langgraph.graph import StateGraph, END
from backend.models.weather_state import WeatherState
from backend.tools.weather_tool import get_current_weather
from backend.tools.forecast_tool import get_forecast
from backend.tools.alert_tool import get_alerts
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.config import GEMINI_API_KEY

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    streaming=True,
)

# ── 1. City extraction ────────────────────────────────────────────────────────

CITY_SYSTEM = """
You are a location extractor for a weather assistant.
Given a user query, return ONLY a JSON object with a single key "city".
The value must be the city name exactly as it appears (or can be inferred) from the query.
If no city is mentioned return {"city": "unknown"}.
Examples:
  "How is the weather in Hyderabad?" → {"city": "Hyderabad"}
  "Tell me the forecast and alerts in New York" → {"city": "New York"}
  "Is it raining?" → {"city": "unknown"}
Return ONLY the JSON object, no explanation.
"""


def extract_city(state: WeatherState) -> WeatherState:
    """Pull the city name out of the free-text query via LLM."""
    resp = llm.invoke([
        {"role": "system", "content": CITY_SYSTEM},
        {"role": "user",   "content": state["query"]},
    ])
    try:
        data = json.loads(resp.content.strip())
        city = data.get("city", "unknown")
    except Exception:
        city = "unknown"
    return {**state, "city": city}


# ── 2. Intent extraction ──────────────────────────────────────────────────────

INTENT_SYSTEM = """
You are an intent classifier for a weather assistant.
Given a user query, return ONLY a JSON array of intents.
Valid values: "weather", "forecast", "alerts".
Include ALL intents the user is asking about.
If unclear, default to ["weather"].
Examples:
  "What is the weather?" → ["weather"]
  "Any storms or forecasts?" → ["alerts", "forecast"]
  "Current conditions, forecast, and any warnings" → ["weather", "forecast", "alerts"]
Return ONLY the JSON array, no explanation.
"""


def extract_intents(state: WeatherState) -> WeatherState:
    """Detect all intents present in the user query via LLM."""
    resp = llm.invoke([
        {"role": "system", "content": INTENT_SYSTEM},
        {"role": "user",   "content": state["query"]},
    ])
    try:
        intents = json.loads(resp.content.strip())
        if not isinstance(intents, list):
            intents = ["weather"]
    except Exception:
        intents = ["weather"]

    valid = {"weather", "forecast", "alerts"}
    intents = [i for i in intents if i in valid] or ["weather"]
    return {**state, "intent": json.dumps(intents)}


# ── 3. Tool execution ─────────────────────────────────────────────────────────

TOOL_MAP = {
    "weather":  get_current_weather,
    "forecast": get_forecast,
    "alerts":   get_alerts,
}


def fetch_tools(state: WeatherState) -> WeatherState:
    """Run every detected tool and merge results into tool_response."""
    intents = json.loads(state.get("intent", '["weather"]'))
    city    = state["city"]
    combined = {}
    for intent in intents:
        fn = TOOL_MAP.get(intent)
        if fn:
            combined[intent] = fn(city)
    return {**state, "tool_response": combined}


# ── 4. Summarization ──────────────────────────────────────────────────────────

def summarize(state: WeatherState) -> WeatherState:
    prompt = (
        f"The user asked: {state['query']}\n"
        f"City: {state['city']}\n"
        f"Here is the data retrieved:\n{json.dumps(state['tool_response'], indent=2)}\n\n"
        "Write a clear, natural-language answer covering everything the user asked about. "
        "If no alerts exist, say so briefly. Be concise."
    )
    resp = llm.invoke(prompt)
    return {**state, "answer": resp.content}


# ── Graph ─────────────────────────────────────────────────────────────────────

g = StateGraph(WeatherState)
g.add_node("extract_city",    extract_city)
g.add_node("extract_intents", extract_intents)
g.add_node("fetch_tools",     fetch_tools)
g.add_node("summarize",       summarize)

g.add_edge("__start__",       "extract_city")
g.add_edge("extract_city",    "extract_intents")
g.add_edge("extract_intents", "fetch_tools")
g.add_edge("fetch_tools",     "summarize")
g.add_edge("summarize",       END)

weather_agent = g.compile()