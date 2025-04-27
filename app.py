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
    """
    # HTML generation for comparison remains the same as before
    ...

# Set up the agent
final_answer = FinalAnswerTool()
model = HfApiModel(
    model_id='mistralai/Mistral-Small-3.1-24B-Instruct-2503',
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

# Launch the Gradio UI with share=True
GradioUI(agent).launch(share=True)
