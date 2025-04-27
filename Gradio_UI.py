import gradio as gr

class GradioUI:
    def __init__(self, agent):
        self.agent = agent

    def compare_colleges_ui(self, college1_name: str, college2_name: str, college3_name: str = None):
        # Import necessary functions from app.py
        from app import fetch_college_data, compare_colleges, generate_comparison_chart
        
        college_data_list = []
        for name in [college1_name, college2_name, college3_name]:
            if name:
                data = fetch_college_data(name)
                if isinstance(data, dict) and "error" not in data:
                    college_data_list.append(data)

        if not college_data_list:
            return "<p>No data found.</p>", None  # Return None for the chart if no data found

        table = compare_colleges(college_data_list)
        chart = generate_comparison_chart(college_data_list)
        return table, chart

    def launch(self):
        with gr.Blocks() as demo:
            # Define inputs and outputs
            college1 = gr.Textbox(label="College 1")
            college2 = gr.Textbox(label="College 2")
            college3 = gr.Textbox(label="College 3 (Optional)")

            output_table = gr.HTML()
            output_chart = gr.Plot()

            # Define the button
            submit_btn = gr.Button("Compare Colleges")

            # Correctly use the click event and ensure proper binding
            submit_btn.click(self.compare_colleges_ui, inputs=[college1, college2, college3], outputs=[output_table, output_chart])

        demo.launch()
