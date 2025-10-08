# Jum Agent

Jum Agent is a prototype backend for a multi agent development platform.  It
exposes a single entry point that accepts a task description (for example
originating from a chat interface) and automatically orchestrates the work
necessary to complete that task.  The platform is designed to be self‑hosted
and to run entirely on your own hardware using open‑source large language
models (LLMs) instead of paid cloud APIs.  A front‑end will be added later;
for now the focus is on the backend architecture and automation.

## Why a local language model?

Many developers want to avoid sending proprietary data to third‑party AI
providers.  Articles such as Instaclustr’s review of top open‑source LLMs
explain that models like **LLaMA 3**, **Gemma 2** and **Mixtral‑8x22B** offer
instruction‑tuned checkpoints and long context windows with licenses that
permit local use【494255927950003†L264-L290】.  Running models locally keeps your
data private, avoids per‑token fees and allows unlimited experimentation
【40816953960309†L164-L166】.  The platform therefore relies on tools that
expose local models through an OpenAI‑compatible API.  For example, the
Ollama runtime lets you pull a `.gguf` model (e.g. `llama3.1`) and run it
locally via `ollama run modelname`【40816953960309†L452-L490】.  Such a server
behaves like OpenAI’s API but does not send data over the internet, making it
a good default choice.

## Project overview

The repository is organised as a Python package with clearly separated
components:

```
jum_agent/
│  README.md          — project overview and instructions
│  requirements.txt     — Python dependencies
│  .env.example         — example environment variables
│
├─ jum_agent/              — package containing the source code
│  │  ┌─ __init__.py
│  │  ├─ main.py         — command‑line entry point
│  │  ├─ orchestrator.py  — orchestrator class coordinating agents
│  │  ├─ models/          — wrappers for local LLMs
│  │  │  └─ llm_client.py  — thin client for calling a local LLM
│  │  ├─ agents/
│  │  │  ┌─ __init__.py
│  │  │  ├─ manager_agent.py — splits an objective into detailed tasks
│  │  │  ├─ dev_agent.py   — generates code given a task description
│  │  │  ├─ qa_agent.py    — validates generated code
│  │  │  └─ doc_agent.py  — produces documentation and commit messages
│  │  ├─ utils/
│  │  │  ┌─ env.py      — helper to load environment variables
│  │  │  └─ memory.py   — simple JSON log storage
└─ tasks/
    └─ example.md      — placeholder tasks or documentation
```

### Orchestrator

The `Orchestrator` class takes a user request and coordinates the work.  A
simple workflow is:

1. **Plan** – Use the LLM to summarise the task and plan the work.
2. **Develop** – Forward the plan to the `DevAgent`, which uses the LLM to
   generate code.  The agent can write files into the repository or return
   code snippets.
3. **Quality Assurance** – The `QaAgent` runs the generated code in a
   sandbox and checks whether it meets the requirements.  If not, it sends
   feedback back to the `DevAgent`.
4. **Doc** – After the development and QA phases, the Doc agent uses the
   changelog to update README files, generate a Markdown changelog and craft
   a concise commit message.
5. **Loop** until the QA agent reports success for each sub‑task.  The
   manager’s rule of “do not move to the next phase without validation” is
   enforced by the orchestrator.
6. **Commit** – Once the work passes QA and documentation is complete,
   the orchestrator can commit the new files to the Git repository.  This
   external side effect requires confirmation from the user before pushing.

### Local language model

The `LLMClient` wrapper in `jum_agent/models/llm_client.py` connects to a
local model server.  By default, it points to an **Ollama** server running
on `http://localhost:11434/v1`.  You can run an Ollama model by installing
Ollama and pulling a model (`ollama pull modelname`).  The GetStream
article notes that Ollama allows you to convert `.gguf` models and run
them with `ollama run modelname`【40816953960309†L448-L490】, and it
provides an extensive library of models and a simple command‑line interface.
The client uses the OpenAI Python library to send requests to this local
server using the `base_url` parameter【40816953960309†L246-L257】.

If you prefer another tool, such as LM Studio or Llamafile, modify
`LLMClient` to point at the corresponding local inference server.  For
example, LM Studio exposes a server at `http://localhost:1234/v1` and can
serve models in the `gguf` format【40816953960309†L164-L206】.

### Environment variables

Configuration values—such as the base URL for the LLM, model name and
GitHub credentials—are loaded from a `.env` file.  A sample `.env.example`
is included.  The `python‑dotenv` package reads these variables at
runtime via the `jum_agent.utils.env.load_env()` helper.  Do not commit
your real keys to version control.

### Example usage

To test the orchestrator without the front‑end, you can install the
dependencies and run a simple CLI from inside the `jum_agent` package:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # customise as needed
python -m jum_agent.main "Create a mini software that reads a Google Doc and inserts links based on page numbers"
```

This example triggers the orchestrator, which uses the dev and QA agents to
generate and test a simple script.  The agents currently include
placeholder implementations; you should extend them to meet your exact
requirements.

## Next steps

The current repository contains only a skeleton with stubbed agents.  To
build a complete multi‑agent system you should:

1. Implement prompt templates and call patterns in `DevAgent` and
  `QaAgent` to generate and test real code.  Consider fine‑tuning a local
  model on your development guidelines and code base.  The Mixtral model
  is particularly strong at coding tasks and supports long contexts and
  function calling【494255927950003†L368-L394】.
2. Add support for external tools such as Google Docs.  You can write
  helper functions using Google’s API to fetch documents and parse
  numbered pages.
3. Build a front‑end chat interface that sends tasks to the orchestrator
  and displays progress updates.  The backend is designed to be
  framework‑agnostic, so you can integrate it into a Flask, FastAPI or
  Node.js server.

The goal is to provide a self‑hosted, fully automated coding assistant
powered by modern open‑source LLMs.  Feel free to adapt and extend this
framework to fit your team’s workflows.
