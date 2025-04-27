import gradio as gr
from smolagents.agents import ActionStep, MultiStepAgent
from smolagents.agent_types import AgentAudio, AgentImage, AgentText, handle_agent_output_types
from smolagents.memory import MemoryStep
import re

def pull_messages_from_step(step_log: MemoryStep):
    """Extract and format messages from each agent step."""
    if isinstance(step_log, ActionStep):
        step_number = f"Step {step_log.step_number}" if step_log.step_number is not None else ""
        yield {"role": "assistant", "content": f"**{step_number}**"}

        if hasattr(step_log, "model_output") and step_log.model_output:
            model_output = step_log.model_output.strip()
            model_output = re.sub(r"```\s*<end_code>", "```", model_output)
            model_output = re.sub(r"<end_code>\s*```", "```", model_output)
            model_output = model_output.strip()
            yield {"role": "assistant", "content": model_output}

        if hasattr(step_log, "tool_calls") and step_log.tool_calls:
            first_tool_call = step_log.tool_calls[0]
            used_code = first_tool_call.name == "python_interpreter"
            parent_id = f"call_{len(step_log.tool_calls)}"

            args = first_tool_call.arguments
            content = str(args.get("answer", str(args))) if isinstance(args, dict) else str(args)

            if used_code:
                content = re.sub(r"```.*?\n", "", content)
                content = re.sub(r"\s*<end_code>\s*", "", content).strip()
                if not content.startswith("```python"):
                    content = f"```python\n{content}\n```"

            parent_message_tool = {
                "role": "assistant",
                "content": content,
                "metadata": {
                    "title": f"🛠️ Used tool {first_tool_call.name}",
                    "id": parent_id,
                    "status": "pending",
                },
            }
            yield parent_message_tool

            if hasattr(step_log, "observations") and step_log.observations:
                obs = step_log.observations.strip()
                if obs:
                    obs = re.sub(r"^Execution logs:\s*", "", obs)
                    yield {
                        "role": "assistant",
                        "content": obs,
                        "metadata": {"title": "📝 Execution Logs", "parent_id": parent_id, "status": "done"},
                    }

            if hasattr(step_log, "error") and step_log.error:
                yield {
                    "role": "assistant",
                    "content": str(step_log.error),
                    "metadata": {"title": "💥 Error", "parent_id": parent_id, "status": "done"},
                }

            parent_message_tool["metadata"]["status"] = "done"

        elif hasattr(step_log, "error") and step_log.error:
            yield {"role": "assistant", "content": str(step_log.error), "metadata": {"title": "💥 Error"}}

        footnote = step_number
        if hasattr(step_log, "input_token_count") and hasattr(step_log, "output_token_count"):
            footnote += f" | Input: {step_log.input_token_count:,}, Output: {step_log.output_token_count:,}"
        if hasattr(step_log, "duration") and step_log.duration:
            footnote += f" | Duration: {round(float(step_log.duration), 2)}s"

        footnote = f"""<span style="color: #bbbbc2; font-size: 12px;">{footnote}</span>"""
        yield {"role": "assistant", "content": footnote}
        yield {"role": "assistant", "content": "-----"}

def stream_to_gradio(agent, task: str, reset_agent_memory: bool = False, additional_args=None):
    """Runs the agent on a task and streams the output for Gradio."""
    total_input_tokens = 0
    total_output_tokens = 0

    for step_log in agent.run(task, stream=True, reset=reset_agent_memory, additional_args=additional_args):
        if hasattr(agent.model, "last_input_token_count") and agent.model.last_input_token_count is not None:
            total_input_tokens += agent.model.last_input_token_count
            total_output_tokens += agent.model.last_output_token_count
            if isinstance(step_log, ActionStep):
                step_log.input_token_count = agent.model.last_input_token_count
                step_log.output_token_count = agent.model.last_output_token_count

        for message in pull_messages_from_step(step_log):
            yield message

    final_answer = handle_agent_output_types(step_log)

    if isinstance(final_answer, AgentText):
        yield {"role": "assistant", "content": f"**Final answer:**\n{final_answer.to_string()}\n"}
    elif isinstance(final_answer, AgentImage):
        yield {"role": "assistant", "content": {"path": final_answer.to_string(), "mime_type": "image/png"}}
    elif isinstance(final_answer, AgentAudio):
        yield {"role": "assistant", "content": {"path": final_answer.to_string(), "mime_type": "audio/wav"}}
    else:
        yield {"role": "assistant", "content": f"**Final answer:** {str(final_answer)}"}

class GradioUI:
    """Simplified Gradio interface for launching your agent."""

    def __init__(self, agent: MultiStepAgent, task: str = "Compare college tuition costs", reset_agent_memory: bool = False):
        self.agent = agent
        self.task = task
        self.reset_agent_memory = reset_agent_memory

    def launch(self, share=True):
        """Start the Gradio interface with shareable link."""
        iface = gr.Interface(
            fn=lambda task: stream_to_gradio(self.agent, task, self.reset_agent_memory),
            inputs=[gr.Textbox(label="College Comparison Task", placeholder="e.g., Compare Harvard vs Stanford", lines=1)],
            outputs=[gr.Chatbot(type="messages")],
            title="🎓 College Comparison Agent",
            live=True,
            allow_flagging="never",
        )
        iface.launch(share=share)  # set share=True to enable external share link
