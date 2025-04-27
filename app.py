import gradio as gr
import requests
import pandas as pd
from typing import List, Dict

# Function to fetch college data using College Scorecard API
def fetch_college_data(college_name: str, api_key: str) -> dict:
    # College Scorecard API endpoint
    api_url = "https://api.data.gov/ed/collegescorecard/v1/schools"

    # Parameters to filter the API request (search by school name)
    params = {
        "school.name": college_name,
        "api_key": api_key,  # API Key is required
        "fields": "id,school.name,city,state,tuition,student.size,admissions.admission_rate.overall,sat_scores.average.overall,act_scores.average.overall",
        "per_page": 1  # Limit results to 1 school per search
    }

    try:
        # Send the GET request to the API
        response = requests.get(api_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Ensure there is at least one result
            if data["results"]:
                school_data = data["results"][0]
                
                # Extract relevant fields
                return {
                    "College Name": school_data.get("school.name", "U/A"),
                    "City": school_data.get("city", "U/A"),
                    "State": school_data.get("state", "U/A"),
                    "In-State Tuition": school_data.get("tuition", "U/A"),
                    "Student Size": school_data.get("student.size", "U/A"),
                    "Admission Rate": school_data.get("admissions.admission_rate.overall", "U/A"),
                    "Average SAT Score": school_data.get("sat_scores.average.overall", "U/A"),
                    "Average ACT Score": school_data.get("act_scores.average.overall", "U/A")
                }
            else:
                return {"College Name": "U/A", "City": "U/A", "State": "U/A", "In-State Tuition": "U/A",
                        "Student Size": "U/A", "Admission Rate": "U/A", "Average SAT Score": "U/A", "Average ACT Score": "U/A"}
        else:
            return {"College Name": "U/A", "City": "U/A", "State": "U/A", "In-State Tuition": "U/A",
                    "Student Size": "U/A", "Admission Rate": "U/A", "Average SAT Score": "U/A", "Average ACT Score": "U/A"}
    except Exception as e:
        print(f"Error fetching data for {college_name}: {e}")
        return {"College Name": "U/A", "City": "U/A", "State": "U/A", "In-State Tuition": "U/A",
                "Student Size": "U/A", "Admission Rate": "U/A", "Average SAT Score": "U/A", "Average ACT Score": "U/A"}

# Function to compare colleges
def compare_colleges(college_data_list: List[dict]) -> pd.DataFrame:
    # Convert the list of dictionaries into a DataFrame
    df = pd.DataFrame(college_data_list)
    return df

# Gradio interface setup
def launch_gradio_ui(api_key: str):
    with gr.Blocks() as demo:
        # Inputs for Gradio interface (text boxes for college names)
        college1 = gr.Textbox(label="Enter the first college name")
        college2 = gr.Textbox(label="Enter the second college name")
        college3 = gr.Textbox(label="Enter the third college name")
        
        # Output area for the comparison table
        output_table = gr.DataFrame()

        # Define the button and click event within the gr.Blocks context
        submit_btn = gr.Button("Compare Colleges")

        # Define the function to be called when the button is clicked
        def compare_colleges_ui(college1_name, college2_name, college3_name):
            # Fetch data for each college
            college1_data = fetch_college_data(college1_name, api_key)
            college2_data = fetch_college_data(college2_name, api_key)
            college3_data = fetch_college_data(college3_name, api_key)

            # Combine data into a list of dictionaries
            college_data_list = [college1_data, college2_data, college3_data]

            # Call compare_colleges function to generate the table
            comparison_table = compare_colleges(college_data_list)

            return comparison_table

        # Set the button click event to trigger the comparison
        submit_btn.click(compare_colleges_ui, inputs=[college1, college2, college3], outputs=[output_table])

    # Launch the Gradio interface
    demo.launch()

if __name__ == "__main__":
    # Replace with your actual API key
    api_key = "your_api_key_here"
    launch_gradio_ui(api_key)
