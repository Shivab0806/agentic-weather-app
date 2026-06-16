from fastapi import APIRouter
from pydantic import BaseModel
from backend.agents.weather_agent import weather_agent
from fastapi.responses import StreamingResponse

router=APIRouter()

class WeatherRequest(BaseModel):
    city:str
    query:str

@router.post("/ask")
def ask(req:WeatherRequest):
    result=weather_agent.invoke({"city":req.city,"query":req.query,"tool_response":{},"answer":""})
    return {"answer":result["answer"]}

@router.post("/ask-stream")
def ask_stream(req: WeatherRequest):

    result = weather_agent.invoke(
        {
            "city": req.city,
            "query": req.query,
            "tool_response": {},
            "answer": ""
        }
    )

    def generate():

        answer = result["answer"]

        for char in answer:
            yield char

    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )
