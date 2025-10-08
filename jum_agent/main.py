'''Command-line interface for Jum Agent.

Run this module with a single argument describing the task to see how the orchestrator coordinates agents to complete the work. For example:

    python -m jum_agent.main Create a Python script that reads a Google Doc and inserts links based on page numbers

Make sure to configure your .env file before running. See jum_agent/utils/env.py and .env.example for details.
'''

import argparse
import sys

from .orchestrator import Orchestrator
from .models.llm_client import LLMClient
from .utils.env import load_env

def main() -> None:
    '''Entry point for the jum_agent CLI.'''
    parser = argparse.ArgumentParser(
        description='Run a task through the Jum Agent orchestrator.'
    )
    parser.add_argument(
        'task',
        nargs=argparse.REMAINDER,
        help='Task description to send to the orchestrator',
    )
    args = parser.parse_args()
    task_description = ' '.join(args.task).strip()
    if not task_description:
        parser.error('A task description is required.')

    # Load environment variables from .env
    load_env()

    # Initialise the LLM client and orchestrator
    client = LLMClient()
    orchestrator = Orchestrator(client)

    # Run the orchestrator
    print(f'Incoming task: {task_description}')
    result = orchestrator.handle_task(task_description)
    print('=== Result ===')
    print(result)

if __name__ == '__main__':
    main()
