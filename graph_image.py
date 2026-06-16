from backend.agents.weather_agent import weather_agent

png = weather_agent.get_graph().draw_mermaid_png()

with open("state_graph.png", "wb") as f:
    f.write(png)

print("Graph Generated")