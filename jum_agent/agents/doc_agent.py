'''Documentation agent.

The `DocAgent` is responsible for generating human-readable documentation from
the changes produced by the Dev and validated by QA. This includes
updating READMEs, writing changelogs and crafting commit messages. It uses
the language model to turn structured diffs or code into descriptive text.
'''

from __future__ import annotations

from typing import Dict, List

from ..models.llm_client import LLMClient


class DocAgent:
    '''Agent that produces documentation and commit messages.'''

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm = llm_client

    def generate_docs(self, changelog: List[str], context: str = '') -> Dict[str, str]:
        '''Generate documentation and a commit message.

        :param changelog: A list of human-readable log entries describing code
            changes.
        :param context: Additional context or comments from QA.
        :returns: A dictionary with keys `readme_update`, `changelog_md` and
            `commit_message`.
        '''
        prompt = (
            'You are a technical writer AI. You are given a list of changes and some context. '
            'Write succinct documentation: a README update summarising the changes, a Markdown changelog entry, '
            'and a concise commit message. Separate the three sections with "---" lines.\\n'
            f'Changes:\\n{chr(10).join(changelog)}\\n'
            f'Context: {context}\\n'
            'Use clear language and avoid redundancy.'
        )
        try:
            response = self.llm.chat(prompt, temperature=0.2)
        except Exception:
            response = None
        if not response:
            default_message = 'Updated code based on the latest task.'
            return {
                'readme_update': default_message,
                'changelog_md': '* ' + default_message,
                'commit_message': default_message,
            }
        # Expect three sections separated by '---'
        sections = response.split('---')
        readme_update = sections[0].strip() if sections else response.strip()
        changelog_md = sections[1].strip() if len(sections) > 1 else ''
        commit_message = sections[2].strip() if len(sections) > 2 else ''
        return {
            'readme_update': readme_update,
            'changelog_md': changelog_md,
            'commit_message': commit_message,
        }
