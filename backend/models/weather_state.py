from typing import TypedDict


class WeatherState(TypedDict):
    query:         str   # raw free-text user input
    city:          str   # extracted by the extract_city node
    intent:        str   # JSON-encoded list, e.g. '["weather","forecast"]'
    tool_response: dict  # merged results from all tool calls
    answer:        str   # final natural-language response