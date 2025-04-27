import gradio as gr

# Function that will be triggered when the user enters a task in the Gradio interface.
def compare_colleges(college_name_1: str, college_name_2: str):
    # Fetch the college data for both colleges
    college_data_1 = get_college_data(college_name_1)
    college_data_2 = get_college_data(college_name_2)

    if 'error' in college_data_1:
        return f"Error fetching data for {college_name_1}: {college_data_1['error']}"
    if 'error' in college_data_2:
        return f"Error fetching data for {college_name_2}: {college_data_2['error']}"
    
    # Compare the data (simplified example of comparison)
    comparison = f"Comparison of {college_name_1} and {college_name_2}:\n\n"
    
    comparison += f"**Tuition (In-State):**\n{college_name_1}: ${college_data_1['tuition_in_state']}  |  {college_name_2}: ${college_data_2['tuition_in_state']}\n\n"
    comparison += f"**Tuition (Out-of-State):**\n{college_name_1}: ${college_data_1['tuition_out_of_state']}  |  {college_name_2}: ${college_data_2['tuition_out_of_state']}\n\n"
    comparison += f"**SAT Score:**\n{college_name_1}: {college_data_1['sat_score']}  |  {college_name_2}: {college_data_2['sat_score']}\n\n"
    comparison += f"**ACT Score:**\n{college_name_1}: {college_data_1['act_score']}  |  {college_name_2}: {college_data_2['act_score']}\n\n"
    comparison += f"**Acceptance Rate:**\n{college_name_1}: {college_data_1['acceptance_rate']}  |  {college_name_2}: {college_data_2['acceptance_rate']}\n\n"
    comparison += f"**Student Size:**\n{college_name_1}: {college_data_1['student_size']}  |  {college_name_2}: {college_data_2['student_size']}"

    return comparison

# Gradio Interface
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
    iface.launch()

# Run the Gradio app
launch_gradio()
