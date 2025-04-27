import gradio as gr
import requests
import pandas as pd
from typing import List

# Function to fetch college data using the College Scorecard API
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
                
                # Extract relevant fields from the response
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

# Function to compare colleges and return the table
def compare_colleges(college_data_list: List[dict]) -> pd.DataFrame:
    # Convert the list of dictionaries into a DataFrame
    df = pd.DataFrame(college_data_list)
    return df

# Gradio interface setup
def compare_colleges_ui(college1_name, college2_name, college3_name, api_key):
    # Fetch data for each college
    college1_data = fetch_college_data(college1_name, api_key)
    college2_data = fetch_college_data(college2_name, api_key)
    college3_data = fetch_college_data(college3_name, api_key)

    # Combine data into a list of dictionaries
    college_data_list = [college1_data, college2_data, college3_data]

    # Call compare_colleges function to generate the table
    comparison_table = compare_colleges(college_data_list)
    
    return comparison_table

def launch_gradio_ui():
    # Replace with your actual API key
    api_key = "your_api_key_here"

    # Inputs for Gradio interface (text boxes for college names)
    college1 = gr.Textbox(label="Enter the first college name")
    college2 = gr.Textbox(label="Enter the second college name")
    college3 = gr.Textbox(label="Enter the third college name")
    
    # Output area for the comparison table
    output_table = gr.DataFrame()
    
    # Create a button to trigger the comparison
    submit_btn = gr.Button("Compare Colleges")
    submit_btn.click(compare_colleges_ui, inputs=[college1, college2, college3, api_key], outputs=[output_table])

    # Launch the Gradio interface
    gr.Interface(fn=None, inputs=[college1, college2, college3], outputs=[output_table], live=True).launch()

if __name__ == "__main__":
    launch_gradio_ui()
