import mimetypes
import os
import re
import shutil
from typing import Optional
import requests
import gradio as gr
from smolagents.agent_types import AgentAudio, AgentImage, AgentText, handle_agent_output_types
from smolagents.agents import ActionStep, MultiStepAgent
from smolagents.memory import MemoryStep
from smolagents.utils import _is_package_available

# Function to fetch college data
def get_college_data(college_name: str):
    api_url = "https://api.data.gov/ed/collegescorecard/v1/schools"
    params = {
        'school.name': college_name,
        'fields': 'id,school.name,school.city,school.state,school.student_size,school.ownership,school.sat_scores,school.act_scores,school.admission_rate,school.cost.tuition',
        'api_key': 'YOUR_API_KEY',  # Replace with your actual API key
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()

        if 'results' in data and len(data['results']) > 0:
            college_info = data['results'][0]
            return {
                'name': college_info['school']['name'],
                'city': college_info['school']['city'],
                'state': college_info['school']['state'],
                'student_size': college_info['school']['student_size'],
                'ownership': college_info['school']['ownership'],
                'sat_score': college_info['school'].get('sat_scores', {}).get('average', {}).get('overall', 'N/A'),
                'act_score': college_info['school'].get('act_scores', {}).get('average', {}).get('overall', 'N/A'),
                'acceptance_rate': college_info['school'].get('admission_rate', {}).get('overall', 'N/A'),
                'tuition_in_state': college_info['school'].get('cost', {}).get('tuition', {}).get('in_state', 'N/A'),
                'tuition_out_of_state': college_info['school'].get('cost', {}).get('tuition', {}).get('out_of_state', 'N/A'),
            }
        else:
            return {'error': 'No data found for this college.'}

    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

# Function to compare colleges
def compare_colleges(college_name_1: str, college_name_2: str):
    college_data_1 = get_college_data(college_name_1)
    college_data_2 = get_college_data(college_name_2)

    if 'error' in college_data_1:
        return f"Error fetching data for {college_name_1}: {college_data_1['error']}"
    if 'error' in college_data_2:
        return f"Error fetching data for {college_name_2}: {college_data_2['error']}"
    
    # Generate a comparison of the two colleges
    comparison = f"Comparison of {college_name_1} and {college_name_2}:\n\n"
    comparison += f"**Tuition (In-State):**\n{college_name_1}: ${college_data_1['tuition_in_state']}  |  {college_name_2}: ${college_data_2['tuition_in_state']}\n\n"
    comparison += f"**Tuition (Out-of-State):**\n{college_name_1}: ${college_data_1['tuition_out_of_state']}  |  {college_name_2}: ${college_data_2['tuition_out_of_state']}\n\n"
    comparison += f"**SAT Score:**\n{college_name_1}: {college_data_1['sat_score']}  |  {college_name_2}: {college_data_2['sat_score']}\n\n"
    comparison += f"**ACT Score:**\n{college_name_1}: {college_data_1['act_score']}  |  {college_name_2}: {college_data_2['act_score']}\n\n"
    comparison += f"**Acceptance Rate:**\n{college_name_1}: {college_data_1['acceptance_rate']}  |  {college_name_2}: {college_data_2['acceptance_rate']}\n\n"
    comparison += f"**Student Size:**\n{college_name_1}: {college_data_1['student_size']}  |  {college_name_2}: {college_data_2['student_size']}"

    return comparison

# Gradio UI for college comparison
def launch_gradio():
    iface = gr.Interface(
        fn=compare_colleges,
        inputs=[
            gr.Textbox(label="College Name 1", placeholder="Enter the first college name"),
            gr.Textbox(label="College Name 2", placeholder="Enter the second college name"),
        ],
        outputs="text",
        live=True,
        title="College Comparison App",
        description="Compare colleges based on tuition, SAT scores, ACT scores, acceptance rates, and more!",
    )
    iface.launch(share=False)  # Disables the share link

if __name__ == "__main__":
    launch_gradio()
