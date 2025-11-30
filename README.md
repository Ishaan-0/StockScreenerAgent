# StockScreenerAgent

Lightweight agent that combines a state graph (langgraph) with an LLM (Ollama / Google Generative) and a tool for stock screening.

## Features
- Stateful conversation flow implemented with langgraph.StateGraph.
- Tool integration for stock screening.
- Simple CLI loop for local testing.

## Requirements
- macOS
- Python 3.12
- Recommended virtualenv

Python libraries (examples):
- langgraph
- langchain-ollama
- langchain-google-genai (optional)
- colorama
- python-dotenv

Install:
```bash
cd /Volumes/T7/Personal__Work/AgenticAI/StockScreenerAgent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  
```

## Environment
Create a `.env` in the project root with any provider keys:
```
GOOGLE_API_KEY=your_api_key_here
```

## Run
- Run the agent loop:
```bash
python screenerAgent.py
```
- Run the tool as a script (tools are commonly wrapped with a decorator). If the tool is decorated and you want to run it directly for testing:
```python
# in tools.py __main__ block:
# call underlying function when wrapper is a StructuredTool
print(stock_screener.func("day_gainers", 0))
```
or remove the decorator during local testing.

## Common troubleshooting
- ValueError: "Checkpointer requires ... thread_id, checkpoint_ns, checkpoint_id"
  - Provide configurable keys when compiling or invoking:
  ```python
  app = graph.compile(checkpointer=memory, defaults={
      "thread_id": "main",
      "checkpoint_ns": "screener",
      "checkpoint_id": "latest",
  })
  # or per-invoke:
  app.invoke(state, config={"configurable":{"thread_id":"main","checkpoint_ns":"screener","checkpoint_id":"latest"}})
  ```

- TypeError: "'StructuredTool' object is not callable"
  - The @tool decorator returns a StructuredTool. Call the wrapped function with `.func` or remove the decorator for direct invocation.

- ValueError: "Found edge ending at unknown node `<function ...>`"
  - Ensure every edge target is a registered node id (string) or START/END. If using a router function, either:
    - register the router as a node id via `graph.add_node("router", router)` and point edges to `"router"`, or
    - use conditional edges that map to existing node ids (see langgraph docs).

## File layout (partial)
- screenerAgent.py — main agent / state graph
- tools.py — stock screener tool
- requirements.txt — (recommended)

## Notes
- The project targets quick testing and development. Adjust LLM model, tool wiring, and checkpointer behavior before production use.
- Keep API keys out of source control.

