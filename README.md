## t5gmcp

FastMCP-based server that exposes tools to query a T5G dashboard for cards, cases, bugs, escalations, issues, and enriched case data.

### Prerequisites
- Python 3.9+
- pip

### Install
```bash
pip install fastmcp urllib3
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

### CLI client
This repo includes a simple client to invoke server tools over HTTP.

```bash
python client.py -d cards
python client.py -d cases
python client.py -d bugs
python client.py -d details
python client.py -d escalations
python client.py -d issues
python client.py -d all_case_data
```

### Exposed tools
Server tools are defined in `server.py` and can be called via MCP or the provided CLI.

- `get_cards`: Returns all JIRA cards as a dict.
- `get_cases`: Returns all customer cases as a dict.
- `get_bugs`: Returns JIRA bugs keyed by case number.
- `get_details`: Returns extended case details keyed by case number.
- `get_escalations`: Returns a list of escalated cases.
- `get_issues`: Returns issues keyed by case number.
- `get_all_case_data`: Builds enriched card data by `case_number`:
  - Adds `case`: the matching case object
  - Adds `escalated`: boolean if case is in escalations
  - Adds `issues`: issues for the case
  - Adds `bugs`: bugs for the case
  - Adds `details`: extended details for the case

