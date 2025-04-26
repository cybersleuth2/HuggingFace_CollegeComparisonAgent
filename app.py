from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel, load_tool, tool
import requests
import datetime
import pytz
import yaml
from tools.final_answer import FinalAnswerTool
import plotly.graph_objects as go
from Gradio_UI import GradioUI

# College Scorecard API URL
COLLEGE_SCORECARD_API_URL = "https://api.data.gov/ed/collegescorecard/v1/schools"

# Define a tool to fetch college data from the College Scorecard API
@tool
def fetch_college_data(college_name: str) -> dict:
    """
    Fetches data from the College Scorecard API for a given college name.
    Args:
        college_name: The name of the college to search for.
    Returns:
        A dictionary containing the college's data.
    """
    try:
        # Define the parameters for the API call
        params = {
            "api_key": "YOUR_API_KEY",  # Get this from data.gov
            "school.name": college_name,
            "fields": "school.name,school.city,school.state,school.student.size,school.ownership,school.sat_scores.average.overall,school.act_scores.average.overall,school.admission_rate.overall,school.cost.tuition.in_state,school.cost.tuition.out_of_state"
        }
        
        # Make the API request
        response = requests.get(COLLEGE_SCORECARD_API_URL, params=params)
        data = response.json()
        
        if "results" in data and data["results"]:
            college_data = data["results"][0]  # Use the first match
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
            return {"error": "College not found or API error."}
    except Exception as e:
        return {"error": str(e)}

# Define the college comparison tool
@tool
def compare_colleges(college_data_list: list) -> str:
    """
    Compares up to 3 colleges based on tuition, SAT/ACT scores, acceptance rate, and more.
    Args:
        college_data_list: List of dictionaries containing data for up to 3 colleges.
    Returns:
        A string comparison report.
    """
    comparison = ""
    
    # Create header for the comparison
    comparison += f"Comparison between {', '.join([college['name'] for college in college_data_list])}:\n\n"

    for key in ['tuition_in_state', 'tuition_out_of_state', 'sat_score', 'act_score', 'acceptance_rate', 'student_size']:
        comparison += f"{key.replace('_', ' ').title()}:\n"
        for college in college_data_list:
            comparison += f"  {college['name']}: {college[key]}\n"
        comparison += "\n"

    return comparison

# Define a function to generate visualizations (bar chart)
def generate_comparison_chart(college_data_list: list) -> go.Figure:
    """
    Generate a Plotly bar chart comparing colleges on key metrics like tuition, SAT, ACT, and acceptance rate.
    Args:
        college_data_list: List of dictionaries containing data for up to 3 colleges.
    Returns:
        A Plotly figure object.
    """
    labels = ['Tuition (In-state)', 'Tuition (Out-of-state)', 'SAT Score', 'ACT Score', 'Acceptance Rate', 'Student Size']
    college_names = [college['name'] for college in college_data_list]

    # Prepare data for plotting
    data = {
        "Tuition (In-state)": [college['tuition_in_state'] for college in college_data_list],
        "Tuition (Out-of-state)": [college['tuition_out_of_state'] for college in college_data_list],
        "SAT Score": [college['sat_score'] for college in college_data_list],
        "ACT Score": [college['act_score'] for college in college_data_list],
        "Acceptance Rate": [college['acceptance_rate'] for college in college_data_list],
        "Student Size": [college['student_size'] for college in college_data_list]
    }

    fig = go.Figure()

    # Add traces for each college
    for i, college in enumerate(college_data_list):
        fig.add_trace(go.Bar(
            x=labels,
            y=[data[label][i] for label in labels],
            name=college['name']
        ))

    fig.update_layout(title="College Comparison",
                      barmode='group',
                      xaxis_title="Metrics",
                      yaxis_title="Values",
                      showlegend=True)

    return fig

# Set up the agent
final_answer = FinalAnswerTool()
model = HfApiModel(
    max_tokens=2096,
    temperature=0.5,
    model_id='Qwen/Qwen2.5-Coder-32B-Instruct',  # it is possible that this model may be overloaded
    custom_role_conversions=None,
)

agent = CodeAgent(
    model=model,
    tools=[final_answer, fetch_college_data, compare_colleges],
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name="college_comparison_agent",  # Fixed agent name
    description="Compares up to 3 colleges based on tuition, SAT/ACT scores, acceptance rate, and more.",
)

# Create the Gradio UI to interact with the agent
gr_interface = GradioUI(agent)

# Function to run the comparison
def compare_colleges_ui(college1_name: str, college2_name: str, college3_name: str = None):
    # Fetch data for each college
    college_data_list = []
    for college_name in [college1_name, college2_name, college3_name]:
        if college_name:
            college_data = fetch_college_data(college_name)
            if "error" not in college_data:
                college_data_list.append(college_data)
    
    # Perform comparison and generate report
    comparison_report = compare_colleges(college_data_list)

    # Generate and display the chart
    comparison_chart = generate_comparison_chart(college_data_list)

    return comparison_report, comparison_chart

# Launch the Gradio UI
gr_interface.launch()
