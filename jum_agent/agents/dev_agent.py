'''Development agent responsible for generating code.

The `DevAgent` uses a language model to translate a high-level task plan into
concrete code. In a production system you would craft detailed prompts
describing your coding guidelines and the target language. For now, this
agent uses a simple instruction and returns the response from the model.
'''

from __future__ import annotations

from typing import Any, Dict

from ..models.llm_client import LLMClient


class DevAgent:
    '''Agent that writes code based on a task and plan.'''

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm = llm_client

    def generate_code(self, task: str, plan: Dict[str, Any]) -> str:
        '''Generate code to satisfy the task.

        :param task: Original user task description.
        :param plan: High-level plan returned by the orchestrator’s planner.
        :returns: Code as a string.
        '''
        plan_summary = plan.get('summary', task)
        steps = plan.get('steps', [])
        instruction = (
            'You are an expert software engineer. Using Python, write code that '
            'accomplishes the following task: {task}. You can assume you have access '
            'to standard libraries. Provide only the code without backticks.'
        ).format(task=plan_summary)
        try:
            response = self.llm.chat(instruction, temperature=0.1)
        except Exception:
            response = None
        if not response:
            # Fallback stub
            return (
                '# TODO: implement code for task\\n'
                'def placeholder_function():\\n'
                '    raise NotImplementedError("This function should be implemented by the DevAgent")'
            )
        return response.strip()
