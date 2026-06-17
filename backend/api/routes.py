from fastapi import APIRouter
from pydantic import BaseModel
from backend.agents.weather_agent import weather_agent
from fastapi.responses import StreamingResponse

router = APIRouter()


class WeatherRequest(BaseModel):
    query: str  # single natural-language field, e.g. "weather and alerts in Hyderabad"


def _initial_state(query: str) -> dict:
    return {
        "query":         query,
        "city":          "",    # filled by extract_city node
        "intent":        "[]",  # filled by extract_intents node
        "tool_response": {},
        "answer":        "",
    }


@router.post("/ask")
def ask(req: WeatherRequest):
    result = weather_agent.invoke(_initial_state(req.query))
    return {"answer": result["answer"], "city": result["city"]}


@router.post("/ask-stream")
def ask_stream(req: WeatherRequest):
    result = weather_agent.invoke(_initial_state(req.query))

    def generate():
        for char in result["answer"]:
            yield char

    return StreamingResponse(generate(), media_type="text/plain")