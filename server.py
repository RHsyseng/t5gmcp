from fastmcp import FastMCP
import json
import urllib3
import os
import logging

dashboard_api = os.environ.get("DASHBOARD_API")

mcp = FastMCP(
    name="t5gmcp",
    instructions="""
        This server retrieves data from
        the t5g dashboard to facilitate
        ad-hoc queries of that data
    """,
)


@mcp.tool
def get_cards() -> dict:
    """Retrieve all JIRA cards from the dashboard"""
    cards = urllib3.request("GET", f"{dashboard_api}/cards")
    return json.loads(cards.data)


@mcp.tool
def get_cases() -> dict:
    """Retrieve all customer cases from the dashboard"""
    cases = urllib3.request("GET", f"{dashboard_api}/cases")
    return json.loads(cases.data)


@mcp.tool
def get_bugs() -> dict:
    """Retrieve all JIRA bugs from the dashboard"""
    bugs = urllib3.request("GET", f"{dashboard_api}/bugs")
    return json.loads(bugs.data)


@mcp.tool
def get_details() -> dict:
    """Retrieve all extended case details from the dashboard"""
    details = urllib3.request("GET", f"{dashboard_api}/details")
    return json.loads(details.data)


@mcp.tool
def get_escalations() -> list:
    """Retrieve a list of all escalated cases from the dashboard"""
    escalations = urllib3.request("GET", f"{dashboard_api}/escalations")
    return json.loads(escalations.data)


@mcp.tool
def get_issues() -> dict:
    """Retrieve all issues associated with a case from the dashboard"""
    issues = urllib3.request("GET", f"{dashboard_api}/issues")
    return json.loads(issues.data)


if __name__ == "__main__":
    mcp.run()
