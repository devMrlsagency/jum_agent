'''Simple persistent memory using JSON files.

This module provides helper functions to record the actions of agents in
JSON files. Each agent can append its actions to a log file, which is
rotated daily. In a production system you might use Redis and a vector
database for retrieval, but this simple implementation suffices for a
self-contained demo.
'''

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def get_log_dir() -> Path:
    '''Return the base directory for logs, creating it if necessary.'''
    log_dir = os.environ.get('LOG_DIR', 'logs/agents')
    path = Path(log_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _get_log_file(agent_id: str) -> Path:
    '''Return the path to the log file for the current day and agent.'''
    date_str = datetime.utcnow().strftime('%Y-%m-%d')
    return get_log_dir() / f'{agent_id}_{date_str}.jsonl'


def append_log(agent_id: str, record: Dict[str, Any]) -> None:
    '''Append a JSON record to the agent’s log file.'''
    log_file = _get_log_file(agent_id)
    with log_file.open('a', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False)
        f.write('\n')


def read_logs(agent_id: str) -> List[Dict[str, Any]]:
    '''Read all log entries for the agent for the current day.'''
    log_file = _get_log_file(agent_id)
    if not log_file.exists():
        return []
    records: List[Dict[str, Any]] = []
    with log_file.open('r', encoding='utf-8') as f:
        for line in f:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records
