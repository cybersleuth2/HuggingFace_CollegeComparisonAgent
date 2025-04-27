import gradio as gr
import requests
import pandas as pd
import os
from typing import List

# Fetch college data using College Scorecard API
def fetch_college_data(college_name: str) -> dict:
    api_url = f"https://api.data.gov/ed/collegescorecard/v1/schools"
    
    # Retrieve API key from Hugging Face secrets
    api_key = os.getenv("COLLEGE_API_KEY")  # Retrieve the key from Hugging Face secrets

    if not api_key:
        raise ValueError("API Key not found in Hugging Face Secrets!")

    # Setup request parameters
    params = {
        'api_key': api_key,
        'school.name': college_name,
        'fields': 'id,school.name,latest.student.size,latest.cost.tuition.in_state,latest.admissions.admission_rate.overall',  # Fields you want to retrieve
        'page': 0,  # Default to first page
        'per_page': 1  # Request only one result per page
    }
    
    try:
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            if results:
                college_data = results[0]  # Get the first result
                return {
                    "College Name": college_data.get("school.name", "U/A"),
                    "Student Size": college_data.get("latest.student.size", "U/A"),
                    "In-State Tuition": college_data.get("latest.cost.tuition.in_state", "U/A"),
                    "Admission Rate": college_data.get("latest.admissions.admission_rate.overall", "U/A")
                }
            else:
                return {"College Name": "U/A", "Student Size": "U/A", "In-State Tuition": "U/A", "Admission Rate": "U/A"}
        else:
            return {"College Name": "U/A", "Student Size": "U/A", "In-State Tuition": "U/A", "Admission Rate": "U/A"}
    except Exception as e:
        print(f"Error fetching data for {college_name}: {e}")
        return {"College Name": "U/A", "Student Size": "U/A", "In-State Tuition": "U/A", "Admission Rate": "U/A"}

# Function to compare colleges and return the table
def compare_colleges(college_data_list: List[dict]) -> pd.DataFrame:
    df = pd.DataFrame(college_data_list)
    return df

# Gradio interface setup inside Blocks context
def launch_gradio_ui():
    with gr.Blocks() as demo:
        # Inputs for Gradio interface (text boxes for college names)
        college1 = gr.Textbox(label="Enter the first college name")
        college2 = gr.Textbox(label="Enter the second college name")
        college3 = gr.Textbox(label="Enter the third college name")
        
        # Output area for the comparison table
        output_table = gr.DataFrame()
        
        # Create a button to trigger the comparison
        submit_btn = gr.Button("Compare Colleges")

        # Define the function to be called when the button is clicked
        def compare_colleges_ui(college1_name, college2_name, college3_name):
            # Fetch data for each college
            college1_data = fetch_college_data(college1_name)
            college2_data = fetch_college_data(college2_name)
            college3_data = fetch_college_data(college3_name)

            # Combine data into a list of dictionaries
            college_data_list = [college1_data, college2_data, college3_data]

            # Call compare_colleges function to generate the table
            comparison_table = compare_colleges(college_data_list)
            
            return comparison_table

        # Set the button click event to trigger the comparison inside the Blocks context
        submit_btn.click(compare_colleges_ui, inputs=[college1, college2, college3], outputs=[output_table])

    # Launch the Gradio interface
    demo.launch()

if __name__ == "__main__":
    launch_gradio_ui()
