import mimetypes
import os
import re
import shutil
from typing import Optional

import gradio as gr
from smolagents.agent_types import AgentAudio, AgentImage, AgentText, handle_agent_output_types
from smolagents.agents import ActionStep, MultiStepAgent
from smolagents.memory import MemoryStep
from smolagents.utils import _is_package_available


def pull_messages_from_step(step_log: MemoryStep):
    """Extract ChatMessage objects from agent steps with proper nesting"""
    if isinstance(step_log, ActionStep):
        # Output the step number
        step_number = f"Step {step_log.step_number}" if step_log.step_number is not None else ""
        yield {"role": "assistant", "content": f"**{step_number}**"}

        # First yield the thought/reasoning from the LLM
        if hasattr(step_log, "model_output") and step_log.model_output is not None:
            model_output = step_log.model_output.strip()
            model_output = re.sub(r"```\s*<end_code>", "```", model_output)
            model_output = re.sub(r"<end_code>\s*```", "```", model_output)
            model_output = re.sub(r"```\s*\n\s*<end_code>", "```", model_output)
            model_output = model_output.strip()
            yield {"role": "assistant", "content": model_output}

        # Handle tool calls and errors
        if hasattr(step_log, "tool_calls") and step_log.tool_calls is not None:
            first_tool_call = step_log.tool_calls[0]
            used_code = first_tool_call.name == "python_interpreter"
            parent_id = f"call_{len(step_log.tool_calls)}"

            args = first_tool_call.arguments
            if isinstance(args, dict):
                content = str(args.get("answer", str(args)))
            else:
                content = str(args).strip()

            if used_code:
                content = re.sub(r"```.*?\n", "", content)
                content = re.sub(r"\s*<end_code>\s*", "", content)
                content = content.strip()
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

            if hasattr(step_log, "observations") and step_log.observations.strip():
                log_content = step_log.observations.strip()
                if log_content:
                    log_content = re.sub(r"^Execution logs:\s*", "", log_content)
                    yield {
                        "role": "assistant",
                        "content": f"{log_content}",
                        "metadata": {"title": "📝 Execution Logs", "parent_id": parent_id, "status": "done"},
                    }

            if hasattr(step_log, "error") and step_log.error is not None:
                yield {
                    "role": "assistant",
                    "content": str(step_log.error),
                    "metadata": {"title": "💥 Error", "parent_id": parent_id, "status": "done"},
                }

            parent_message_tool["metadata"]["status"] = "done"

        elif hasattr(step_log, "error") and step_log.error is not None:
            yield {"role": "assistant", "content": str(step_log.error), "metadata": {"title": "💥 Error"}}

        step_footnote = f"{step_number}"
        if hasattr(step_log, "input_token_count") and hasattr(step_log, "output_token_count"):
            token_str = f" | Input-tokens:{step_log.input_token_count:,} | Output-tokens:{step_log.output_token_count:,}"
            step_footnote += token_str
        if hasattr(step_log, "duration"):
            step_duration = f" | Duration: {round(float(step_log.duration), 2)}" if step_log.duration else None
            step_footnote += step_duration
        step_footnote = f"""<span style="color: #bbbbc2; font-size: 12px;">{step_footnote}</span> """
        yield {"role": "assistant", "content": f"{step_footnote}"}
        yield {"role": "assistant", "content": "-----"}


def stream_to_gradio(agent, task: str, reset_agent_memory: bool = False, additional_args: Optional[dict] = None):
    """Runs an agent with the given task and streams the messages from the agent as gradio ChatMessages."""
    if not _is_package_available("gradio"):
        raise ModuleNotFoundError("Please install 'gradio' extra to use the GradioUI: `pip install 'smolagents[gradio]'`")

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

    final_answer = step_log  # Last log is the run's final_answer
    final_answer = handle_agent_output_types(final_answer)

    if isinstance(final_answer, AgentText):
        yield {"role": "assistant", "content": f"**Final answer:**\n{final_answer.to_string()}\n"}
    elif isinstance(final_answer, AgentImage):
        yield {"role": "assistant", "content": {"path": final_answer.to_string(), "mime_type": "image/png"}}
    elif isinstance(final_answer, AgentAudio):
        yield {"role": "assistant", "content": {"path": final_answer.to_string(), "mime_type": "audio/wav"}}
    else:
        yield {"role": "assistant", "content": f"**Final answer:** {str(final_answer)}"}


class GradioUI:
    """A one-line interface to launch your agent in Gradio"""

    def __init__(self, agent: MultiStepAgent, task: str = "Search Task", reset_agent_memory: bool = False):
        self.agent = agent
        self.task = task
        self.reset_agent_memory = reset_agent_memory

    def launch(self):
        """Launch the Gradio UI."""
        iface = gr.Interface(
            fn=stream_to_gradio,
            inputs=[
                gr.Textbox(label="Task", lines=1, placeholder="Enter your task description", value=self.task),
            ],
            outputs=[gr.Chatbot()],
            live=True,
            allow_flagging="never",
            allow_screenshot=False,
            title="College Comparison Agent",
            theme="compact",
            examples=[["Compare college tuition costs"]],
        )
        iface.launch()
