from typing import TypedDict
class WeatherState(TypedDict):
    query:str
    city:str
    tool_response:dict
    answer:str
