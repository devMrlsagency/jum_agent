'''Manager agent responsible for planning and coordinating tasks.

The `ManagerAgent` receives a high-level objective and breaks it down into
detailed tasks for the Dev, QA and Doc agents. It can also maintain the
overall project context and constraints. In practice, this agent would
construct a comprehensive roadmap using an LLM, but here it returns a simple
structure for demonstration purposes.
'''

from __future__ import annotations

from typing import Any, Dict, List

from ..models.llm_client import LLMClient


class ManagerAgent:
    '''Agent that plans a project and assigns tasks to other agents.'''

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm = llm_client

    def plan(self, objective: str, context: str = '', constraints: str = '') -> List[Dict[str, Any]]:
        '''Generate a list of tasks to accomplish the objective.

        :param objective: The overall goal to achieve.
        :param context: Additional context about the project.
        :param constraints: Technical or business constraints.
        :returns: A list of task dictionaries. Each task has at least a
            description and a type (e.g. 'dev', 'qa', 'doc').
        '''
        prompt = (
            'You are a project manager AI. You are given a software development objective, '
            'some context and constraints. Break the objective into a sequence of tasks '
            'with short descriptions. Label each task with the type of agent that '
            'should handle it: DEV for code generation, QA for testing, DOC for documentation.\\n'
            f'Objective: {objective}\\n'
            f'Context: {context}\\n'
            f'Constraints: {constraints}\\n'
            'Return the tasks as a numbered list.'
        )
        try:
            response = self.llm.chat(prompt, temperature=0.3)
        except Exception:
            response = None
        tasks: List[Dict[str, Any]] = []
        if not response:
            # Fallback: default single dev task
            tasks.append({'description': objective, 'type': 'dev'})
            return tasks
        # Parse the response into tasks. Expect lines like '1. DEV: Description'
        for line in response.splitlines():
            line = line.strip()
            if not line or not line[0].isdigit():
                continue
            # Remove numbering prefix
            parts = line.split('.', 1)
            body = parts[1].strip() if len(parts) > 1 else line
            # Determine type: look for 'DEV', 'QA', 'DOC'
            task_type = 'dev'
            if body.lower().startswith('qa'):
                task_type = 'qa'
                body = body[2:].lstrip(' :')
            elif body.lower().startswith('doc'):
                task_type = 'doc'
                body = body[3:].lstrip(' :')
            elif body.lower().startswith('dev'):
                task_type = 'dev'
                body = body[3:].lstrip(' :')
            tasks.append({'description': body.strip(), 'type': task_type})
        if not tasks:
            tasks.append({'description': objective, 'type': 'dev'})
        return tasks
