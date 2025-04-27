import gradio as gr
import requests
import pandas as pd
from typing import List, Dict

# Function to fetch college data using an API
def fetch_college_data(college_name: str) -> dict:
    # Example API endpoint, replace with the actual API you're using
    api_url = f"https://api.collegeapi.com/college/{college_name.replace(' ', '%20')}"
    
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            return {
                "College Name": data.get("name", "U/A"),
                "City": data.get("city", "U/A"),
                "State": data.get("state", "U/A"),
                "In-State Tuition": data.get("in_state_tuition", "U/A"),
                "Out-of-State Tuition": data.get("out_of_state_tuition", "U/A"),
                "Student Size": data.get("student_size", "U/A"),
                "Admission Rate": data.get("admission_rate", "U/A"),
                "Average SAT Score": data.get("sat_score", "U/A"),
                "Average ACT Score": data.get("act_score", "U/A"),
                "Known For": data.get("known_for", "U/A"),
                "Application Deadlines": data.get("application_deadlines", "U/A")
            }
        else:
            return {"College Name": "U/A", "City": "U/A", "State": "U/A", "In-State Tuition": "U/A",
                    "Out-of-State Tuition": "U/A", "Student Size": "U/A", "Admission Rate": "U/A",
                    "Average SAT Score": "U/A", "Average ACT Score": "U/A", "Known For": "U/A", "Application Deadlines": "U/A"}
    except Exception as e:
        print(f"Error fetching data for {college_name}: {e}")
        return {"College Name": "U/A", "City": "U/A", "State": "U/A", "In-State Tuition": "U/A",
                "Out-of-State Tuition": "U/A", "Student Size": "U/A", "Admission Rate": "U/A",
                "Average SAT Score": "U/A", "Average ACT Score": "U/A", "Known For": "U/A", "Application Deadlines": "U/A"}

# Function to compare colleges
def compare_colleges(college_data_list: List[dict]) -> pd.DataFrame:
    # Convert the list of dictionaries into a DataFrame
    df = pd.DataFrame(college_data_list)
    return df

# Gradio interface setup
def launch_gradio_ui():
    # Inputs for Gradio interface (text boxes for college names)
    college1 = gr.Textbox(label="Enter the first college name")
    college2 = gr.Textbox(label="Enter the second college name")
    college3 = gr.Textbox(label="Enter the third college name")
    
    # Output area for the comparison table
    output_table = gr.DataFrame()
    
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

    # Create a button to trigger the comparison
    submit_btn = gr.Button("Compare Colleges")
    submit_btn.click(compare_colleges_ui, inputs=[college1, college2, college3], outputs=[output_table])

    # Launch the Gradio interface
    gr.Interface(fn=None, inputs=[college1, college2, college3], outputs=[output_table], live=True).launch()

if __name__ == "__main__":
    launch_gradio_ui()
