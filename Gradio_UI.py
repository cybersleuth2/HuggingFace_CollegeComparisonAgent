import gradio as gr
import pandas as pd
from smolagents.agents import MultiStepAgent
from smolagents.agent_types import AgentText, handle_agent_output_types
from tools import fetch_college_data, compare_colleges, generate_comparison_chart

class GradioUI:
    """Simplified Gradio interface for launching your agent."""

    def __init__(self, agent: MultiStepAgent, task: str = "Compare college tuition costs", reset_agent_memory: bool = False):
        self.agent = agent
        self.task = task
        self.reset_agent_memory = reset_agent_memory

    def launch(self):
        """Start the Gradio interface with a shareable link."""
        # Gradio Inputs: College names (3 input fields)
        inputs = [
            gr.Textbox(label="College 1", placeholder="e.g., Harvard", lines=1),
            gr.Textbox(label="College 2", placeholder="e.g., Stanford", lines=1),
            gr.Textbox(label="College 3 (Optional)", placeholder="e.g., MIT", lines=1),
        ]
        
        # Gradio Output: Downloadable CSV
        outputs = [
            gr.File(label="Download College Comparison CSV")
        ]

        # Create the Gradio interface
        iface = gr.Interface(
            fn=self.compare_colleges_to_csv,
            inputs=inputs,
            outputs=outputs,
            title="🎓 College Comparison Agent",
            live=False,  # Set to False because we don't need live updates
            allow_flagging="never",
        )
        # Launch with share=True to allow shareable link
        iface.launch(share=True)  # share=True will provide a shareable link

    def compare_colleges_to_csv(self, college1_name: str, college2_name: str, college3_name: str = None):
        """
        Fetches data for three colleges, compares them, and generates a CSV for download.
        """
        college_data_list = []
        colleges = [college1_name, college2_name, college3_name]

        # Fetch data for each college
        for name in colleges:
            if name:  # Only process if the name is not empty
                data = fetch_college_data(name)
                if isinstance(data, dict) and "error" not in data:
                    college_data_list.append(data)

        if not college_data_list:
            return None  # No valid college data to output

        # Prepare the CSV data from the fetched college data
        college_comparison_data = {
            "College Name": [college['name'] for college in college_data_list],
            "City": [college['city'] for college in college_data_list],
            "State": [college['state'] for college in college_data_list],
            "Student Size": [college['student_size'] for college in college_data_list],
            "SAT Score": [college['sat_score'] for college in college_data_list],
            "ACT Score": [college['act_score'] for college in college_data_list],
            "Acceptance Rate": [college['acceptance_rate'] for college in college_data_list],
            "Tuition (In-state)": [college['tuition_in_state'] for college in college_data_list],
            "Tuition (Out-of-state)": [college['tuition_out_of_state'] for college in college_data_list],
        }

        # Convert data to a pandas DataFrame
        df = pd.DataFrame(college_comparison_data)

        # Save to a CSV file
        csv_filename = "college_comparison.csv"
        df.to_csv(csv_filename, index=False)
        #
        # Return the CSV file for download
        return csv_filename
