import requests
import os
import plotly.graph_objects as go
from smolagents import CodeAgent, tool
from smolagents.agent_types import AgentText
from tools.final_answer import FinalAnswerTool
from Gradio_UI import GradioUI
import pandas as pd

# College Scorecard API URL
COLLEGE_SCORECARD_API_URL = "https://api.data.gov/ed/collegescorecard/v1/schools"

@tool
def fetch_college_data(college_name: str) -> dict:
    """
    Fetches data from the College Scorecard API for a given college name.

    Args:
        college_name (str): The name of the college to search for.

    Returns:
        dict: A dictionary with college data or error message.
    """
    try:
        api_key = os.getenv("COLLEGE_API_KEY")
        if not api_key or "YOUR_API_KEY" in api_key:
            return {"error": "API key is missing or invalid. Please check your Hugging Face secrets."}

        params = {
            "api_key": api_key,
            "school.name": college_name,
            "fields": "school.name,school.city,school.state,school.student.size,school.ownership,"
                      "school.sat_scores.average.overall,school.act_scores.average.overall,"
                      "school.admission_rate.overall,school.cost.tuition.in_state,school.cost.tuition.out_of_state"
        }

        response = requests.get(COLLEGE_SCORECARD_API_URL, params=params)

        if response.status_code != 200:
            return {"error": f"API request failed with status code {response.status_code}: {response.text}"}

        data = response.json()
        if "results" in data and data["results"]:
            college_data = data["results"][0]
            return {
                "name": college_data["school"]["name"],
                "city": college_data["school"]["city"],
                "state": college_data["school"]["state"],
                "student_size": college_data["school"]["student_size"],
                "ownership": college_data["school"]["ownership"],
                "sat_score": college_data["school"]["sat_scores"]["average"]["overall"],
                "act_score": college_data["school"]["act_scores"]["average"]["overall"],
                "acceptance_rate": college_data["school"]["admission_rate"]["overall"],
                "tuition_in_state": college_data["school"]["cost"]["tuition"]["in_state"],
                "tuition_out_of_state": college_data["school"]["cost"]["tuition"]["out_of_state"]
            }
        else:
            return {"error": "College not found or no valid data returned from the API."}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

@tool
def compare_colleges(college_data_list: list) -> str:
    """
    Compares up to 3 colleges and returns an HTML table displaying their key metrics.

    Args:
        college_data_list (list): List of college data dictionaries.

    Returns:
        str: HTML table of comparison.
    """
    if not college_data_list:
        return "<p>No valid college data provided.</p>"

    headers = ["Name", "City", "State", "Student Size", "SAT", "ACT", "Acceptance Rate", "Tuition (In-state)", "Tuition (Out-of-state)"]
    rows = []
    for college in college_data_list:
        rows.append([
            college.get("name", "N/A"),
            college.get("city", "N/A"),
            college.get("state", "N/A"),
            college.get("student_size", "N/A"),
            college.get("sat_score", "N/A"),
            college.get("act_score", "N/A"),
            college.get("acceptance_rate", "N/A"),
            college.get("tuition_in_state", "N/A"),
            college.get("tuition_out_of_state", "N/A"),
        ])

    html = "<table border='1' style='border-collapse: collapse; padding: 8px;'>"
    html += "<tr>" + "".join([f"<th>{header}</th>" for header in headers]) + "</tr>"
    for row in rows:
        html += "<tr>" + "".join([f"<td>{str(cell)}</td>" for cell in row]) + "</tr>"
    html += "</table>"

    return html

def generate_comparison_chart(college_data_list: list) -> go.Figure:
    """
    Generates a bar chart comparing key metrics for up to 3 colleges.

    Args:
        college_data_list (list): List of college data dictionaries.

    Returns:
        go.Figure: Plotly chart.
    """
    labels = ['Tuition (In-state)', 'Tuition (Out-of-state)', 'SAT Score', 'ACT Score', 'Acceptance Rate', 'Student Size']
    data = {
        "Tuition (In-state)": [college['tuition_in_state'] for college in college_data_list],
        "Tuition (Out-of-state)": [college['tuition_out_of_state'] for college in college_data_list],
        "SAT Score": [college['sat_score'] for college in college_data_list],
        "ACT Score": [college['act_score'] for college in college_data_list],
        "Acceptance Rate": [college['acceptance_rate'] for college in college_data_list],
        "Student Size": [college['student_size'] for college in college_data_list]
    }

    fig = go.Figure()
    for i, college in enumerate(college_data_list):
        fig.add_trace(go.Bar(
            x=labels,
            y=[data[label][i] for label in labels],
            name=college['name']
        ))

    fig.update_layout(title="College Comparison",
                      barmode='group',
                      xaxis_title="Metrics",
                      yaxis_title="Values")
    return fig

# Set up the agent
final_answer = FinalAnswerTool()
agent = CodeAgent(
    model='mistralai/Mistral-Small-3.1-24B-Instruct-2503',  # Example model
    tools=[final_answer, fetch_college_data, compare_colleges],
    max_steps=6,
    verbosity_level=1,
    name="college_comparison_agent",
    description="Compare colleges based on data.",
)

# Launch Gradio UI
GradioUI(agent).launch()
