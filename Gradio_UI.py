import gradio as gr
from smolagents.agents import MultiStepAgent
from smolagents.agent_types import AgentText
from smolagents.memory import MemoryStep
from smolagents.tools import fetch_college_data, compare_colleges, generate_comparison_chart
import pandas as pd

class GradioUI:
    def __init__(self, agent: MultiStepAgent, task: str = "Compare college tuition costs", reset_agent_memory: bool = False):
        self.agent = agent
        self.task = task
        self.reset_agent_memory = reset_agent_memory

    def launch(self):
        """Start the Gradio interface."""
        iface = gr.Interface(
            fn=self.process_input,
            inputs=[
                gr.Textbox(label="College 1", placeholder="Enter first college name"),
                gr.Textbox(label="College 2", placeholder="Enter second college name"),
                gr.Textbox(label="College 3 (Optional)", placeholder="Enter third college name", optional=True),
                gr.Button("Submit")
            ],
            outputs=[
                gr.Dataframe(headers=["Name", "City", "State", "Student Size", "SAT", "ACT", "Acceptance Rate", "Tuition (In-state)", "Tuition (Out-of-state)"]),
                gr.Plotly(figure=generate_comparison_chart)
            ],
            live=True,
            title="🎓 College Comparison Agent"
        )
        iface.launch(share=True)  # share=True to enable sharing via a public link

    def process_input(self, college1_name: str, college2_name: str, college3_name: str = None):
        """Process the college names, fetch data, and return the comparison table and chart."""
        college_data_list = []
        for name in [college1_name, college2_name, college3_name]:
            if name:
                data = fetch_college_data(name)
                if isinstance(data, dict) and "error" not in data:
                    college_data_list.append(data)

        if not college_data_list:
            return pd.DataFrame(), go.Figure()  # Return empty dataframe and figure

        table = compare_colleges(college_data_list)
        chart = generate_comparison_chart(college_data_list)
        return table, chart
