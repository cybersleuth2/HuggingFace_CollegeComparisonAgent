from smolagents import CodeAgent, HfApiModel, tool
import requests
import os
import plotly.graph_objects as go
from tools.final_answer import FinalAnswerTool
from Gradio_UI import GradioUI

# College Scorecard API URL
COLLEGE_SCORECARD_API_URL = "https://api.data.gov/ed/collegescorecard/v1/schools"

@tool
def fetch_college_data(college_name: str) -> dict:
    # ... (same as your original code)

@tool
def compare_colleges(college_data_list: list) -> str:
    # ... (same as your original code)

def generate_comparison_chart(college_data_list: list) -> go.Figure:
    # ... (same as your original code)

def compare_colleges_ui(college1_name: str, college2_name: str, college3_name: str = None):
    college_data_list = []
    for name in [college1_name, college2_name, college3_name]:
        if name:
            data = fetch_college_data(name)
            if "error" not in data:
                college_data_list.append(data)

    if not college_data_list:
        return "<p>No data found.</p>", go.Figure()

    table = compare_colleges(college_data_list)
    chart = generate_comparison_chart(college_data_list)
    return table, chart

# Set up the agent
final_answer = FinalAnswerTool()
model = HfApiModel(
    model_id='mistralai/Mistral-7B-Instruct-v0.1',
    max_tokens=1024,
    temperature=0.5,
)

agent = CodeAgent(
    model=model,
    tools=[final_answer, fetch_college_data, compare_colleges],
    max_steps=6,
    verbosity_level=1,
    name="college_comparison_agent",
    description="Compare colleges based on data.",
)

# Launch
GradioUI(agent).launch()
