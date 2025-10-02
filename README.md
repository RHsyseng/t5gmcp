## t5gmcp

FastMCP-based server that exposes tools to query a T5G dashboard for cards, cases, bugs, escalations, issues, and enriched case data.

### Prerequisites
- Python 3.9+
- pip

### Install
```bash
pip install -r requirements.txt
```

### Configure
Set the base URL for the dashboard API used by the server.
```bash
export DASHBOARD_API="https://your-dashboard.example.com/api"
```

### Run the server
- Using the helper script:
```bash
./run.sh
```

- Or directly with fastmcp:
```bash
fastmcp run server.py:mcp --transport http --port 8000
```

The server will listen at `http://localhost:8000/mcp` by default.

### Chatbot
A minimal chatbot is provided that can optionally use an LLM (OpenAI) with tool calling to invoke the MCP tools. Without an LLM, it falls back to keyword routing.

```bash
# optional if using LLM-backed chat
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-4o-mini

# ensure server is running first (see above)
python chatbot.py --mcp-url http://localhost:8000/mcp

# to run without an LLM and rely on keyword routing
python chatbot.py --no-llm
```

### CLI client
This repo includes a simple client to invoke server tools over HTTP.

```bash
python client.py -d cards
python client.py -d cases
python client.py -d bugs
python client.py -d details
python client.py -d escalations
python client.py -d issues
python client.py -d full_case_data
```

### Exposed tools
Server tools are defined in `server.py` and can be called via MCP or the provided CLI.

- `get_cards`: Returns all JIRA cards as a dict.
- `get_cases`: Returns all customer cases as a dict.
- `get_bugs`: Returns JIRA bugs keyed by case number.
- `get_details`: Returns extended case details keyed by case number.
- `get_escalations`: Returns a list of escalated cases.
- `get_issues`: Returns issues keyed by case number.
- `get_full_case_data`: All the info from get_cards, but keyed on cases rather than JIRA cards

