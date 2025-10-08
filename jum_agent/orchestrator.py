'''Core orchestration logic.

The orchestrator coordinates multiple agents to fulfil a user request. It
includes planning, code generation and quality assurance phases. The
orchestrator interacts with a local language model via an LLMClient to
interpret tasks and generate code. It uses DevAgent and QaAgent to
produce and verify the code respectively.
'''

from __future__ import annotations

import logging
from typing import Any, Dict, List

from .models.llm_client import LLMClient
from .agents.dev_agent import DevAgent
from .agents.qa_agent import QaAgent
from .agents.manager_agent import ManagerAgent
from .agents.doc_agent import DocAgent
from .utils.memory import append_log

logger = logging.getLogger(__name__)

class Orchestrator:
    '''Orchestrates development tasks using local LLMs and multiple agents.'''

    def __init__(self, llm_client: LLMClient, max_iterations: int = 3) -> None:
        self.llm = llm_client
        self.manager = ManagerAgent(llm_client)
        self.dev_agent = DevAgent(llm_client)
        self.qa_agent = QaAgent(llm_client)
        self.doc_agent = DocAgent(llm_client)
        self.max_iterations = max_iterations

    def _plan(self, objective: str) -> Dict[str, Any]:
        '''Create a high-level plan for a task using the Manager agent.'''
        tasks = self.manager.plan(objective)
        return {'summary': objective, 'tasks': tasks}

    def handle_task(self, objective: str) -> str:
        '''Handle a user objective end-to-end and return a result message.'''
        # Generate a plan of tasks using the Manager
        plan = self._plan(objective)
        tasks = plan.get('tasks', [])
        logger.info('Manager plan: %s', tasks)
        changelog: List[str] = []
        context: str = ''
        for idx, task in enumerate(tasks, 1):
            description = task.get('description', '')
            task_type = task.get('type', 'dev').lower()
            logger.info('Executing task %d/%d: type=%s, description=%s', idx, len(tasks), task_type, description)
            if task_type == 'dev':
                # Developer writes code
                code_result = self.dev_agent.generate_code(description, {'summary': description, 'steps': [description]})
                append_log('dev', {'task': description, 'code': code_result})
                # QA automatically runs after dev
                passed, feedback = self.qa_agent.check_code(code_result, description)
                append_log('qa', {'task': description, 'passed': passed, 'feedback': feedback})
                if not passed:
                    # If QA fails, return immediately with feedback
                    return (
                        'Task ' + repr(description) + ' failed during QA.\n'
                        + 'Feedback: ' + feedback + '\n'
                        + 'Generated code:\n' + code_result
                    )
                # QA passed; record change for documentation
                changelog.append(f'Implemented: {description}')
            elif task_type == 'qa':
                # Standalone QA task (rare)
                passed, feedback = self.qa_agent.check_code('', description)
                append_log('qa', {'task': description, 'passed': passed, 'feedback': feedback})
                if not passed:
                    return 'QA task ' + repr(description) + ' failed: ' + feedback
            elif task_type == 'doc':
                # Documentation is generated after all dev and qa tasks, so skip here
                changelog.append(f'Documentation requested: {description}')
            else:
                logger.warning('Unknown task type %s', task_type)

        # After all tasks, generate documentation
        docs = self.doc_agent.generate_docs(changelog, context)
        append_log('doc', {'changelog': changelog, 'docs': docs})
        # Return combined result
        result_message = 'All tasks completed successfully.\n\n'
        result_message += 'Changelog:\n' + '\n'.join(changelog) + '\n\n'
        result_message += 'Documentation Update:\n' + docs.get('readme_update', '')
        result_message += '\n\nCommit Message:\n' + docs.get('commit_message', '')
        return result_message
