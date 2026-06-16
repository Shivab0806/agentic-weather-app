from langgraph.graph import StateGraph, END
from backend.models.weather_state import WeatherState
from backend.tools.weather_tool import get_current_weather
from backend.tools.forecast_tool import get_forecast
from backend.tools.alert_tool import get_alerts
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.config import GEMINI_API_KEY

llm=ChatGoogleGenerativeAI(model="gemini-2.5-flash",google_api_key=GEMINI_API_KEY,streaming=True)

def route(state):
    q=state["query"].lower()
    if "forecast" in q: return "forecast"
    if "alert" in q: return "alert"
    return "weather"

def weather(state): return {**state,"tool_response":get_current_weather(state["city"])}
def forecast(state): return {**state,"tool_response":get_forecast(state["city"])}
def alert(state): return {**state,"tool_response":get_alerts(state["city"])}

def summarize(state):
    resp=llm.invoke(f"Question:{state['query']} Data:{state['tool_response']} Summarize.")
    return {**state,"answer":resp.content}

g=StateGraph(WeatherState)
g.add_node("weather",weather)
g.add_node("forecast",forecast)
g.add_node("alert",alert)
g.add_node("summarize",summarize)
g.add_conditional_edges("__start__",route,{"weather":"weather","forecast":"forecast","alert":"alert"})
g.add_edge("weather","summarize")
g.add_edge("forecast","summarize")
g.add_edge("alert","summarize")
g.add_edge("summarize",END)
weather_agent=g.compile()
