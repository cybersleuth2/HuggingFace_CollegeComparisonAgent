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
    """
    Fetches data from the College Scorecard API for a given college name.

    Args:
        college_name (str): The name of the college to search for.

    Returns:
        dict: A dictionary containing the college's data, including name, city, state, 
              student size, ownership, SAT score, ACT score, acceptance rate, and tuition.
    """
    try:
        # Fetch API key securely from environment variables
        api_key = os.getenv("COLLEGE_API_KEY")
        if not api_key:
            return {"error": "API key is missing. Please set the COLLEGE_API_KEY environment variable."}

        params = {
            "api_key": api_key,
            "school.name": college_name,
            "fields": "school.name,school.city,school.state,school.student.size,school.ownership,"
                      "school.sat_scores.average.overall,school.act_scores.average.overall,"
                      "school.admission_rate.overall,school.cost.tuition.in_state,school.cost.tuition.out_of_state"
        }
        response = requests.get(COLLEGE_SCORECARD_API_URL, params=params)
        
        # Check for a successful response (status code 200)
        if response.status_code != 200:
            return {"error": f"API request failed with status code {response.status_code}."}

        data = response.json()
        
        # Check if the data contains the necessary results
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
        college_data_list (list): A list of dictionaries, where each dictionary contains data for a college.
        
    Returns:
        str: An HTML table as a string showing the comparison of colleges' data.
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
        college_data_list (list): A list of dictionaries, where each dictionary contains data for a college.

    Returns:
        go.Figure: A Plotly bar chart figure comparing key metrics of the colleges.
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

# Required by Gradio UI
def compare_colleges_ui(college1_name: str, college2_name: str, college3_name: str = None):
    """
    Fetches data for three colleges and generates a table and chart comparing them.

    Args:
        college1_name (str): The name of the first college.
        college2_name (str): The name of the second college.
        college3_name (str, optional): The name of the third college, default is None.

    Returns:
        tuple: A tuple containing:
            - An HTML table string comparing the colleges.
            - A Plotly chart figure comparing the colleges.
    """
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
    model_id='mistralai/Mistral-Small-3.1-24B-Instruct-2503',  # Updated to the free Mistral model
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

# Launch Gradio UI (without share=False argument)
GradioUI(agent).launch()  # Removed share=False
