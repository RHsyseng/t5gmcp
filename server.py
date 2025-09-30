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


@mcp.tool
def get_all_case_data() -> dict:
    """Return JIRA cards with attached case data by case_number"""
    cards_resp = urllib3.request("GET", f"{dashboard_api}/cards")
    cases_resp = urllib3.request("GET", f"{dashboard_api}/cases")
    escalations_resp = urllib3.request("GET", f"{dashboard_api}/escalations")
    issues_resp = urllib3.request("GET", f"{dashboard_api}/issues")
    bugs_resp = urllib3.request("GET", f"{dashboard_api}/bugs")
    details_resp = urllib3.request("GET", f"{dashboard_api}/details")

    cards_obj = json.loads(cards_resp.data)
    cases_obj = json.loads(cases_resp.data)
    escalations_obj = json.loads(escalations_resp.data)
    issues_obj = json.loads(issues_resp.data)
    bugs_obj = json.loads(bugs_resp.data)
    details_obj = json.loads(details_resp.data)

    # Build an index of cases by case_number for fast lookup
    case_index = {}

    if isinstance(cases_obj, dict):
        values = list(cases_obj.values())
        if values and isinstance(values[0], dict) and "case_number" in values[0]:
            for case in cases_obj.values():
                cn = case.get("case_number")
                if cn is not None:
                    case_index[cn] = case
        else:
            # Assume keys are the case numbers
            case_index = cases_obj
    elif isinstance(cases_obj, list):
        for case in cases_obj:
            if isinstance(case, dict):
                cn = case.get("case_number")
                if cn is not None:
                    case_index[cn] = case

    # Build a set of escalated case numbers for quick membership checks
    escalated_case_numbers = set()
    if isinstance(escalations_obj, list):
        for item in escalations_obj:
            if isinstance(item, dict):
                cn = item.get("case_number")
                if cn is not None:
                    escalated_case_numbers.add(str(cn))
            else:
                # assume primitive value is the case number
                escalated_case_numbers.add(str(item))

    # Normalized issues lookup by case number (string and numeric tolerant)
    issues_by_case = {}
    if isinstance(issues_obj, dict):
        issues_by_case = issues_obj

    # Normalized bugs lookup by case number (string and numeric tolerant)
    bugs_by_case = {}
    if isinstance(bugs_obj, dict):
        bugs_by_case = bugs_obj

    # Normalized details lookup by case number (string and numeric tolerant)
    details_by_case = {}
    if isinstance(details_obj, dict):
        details_by_case = details_obj

    # Enrich each card with its matching case data
    enriched = {}

    if isinstance(cards_obj, dict):
        for card_id, card in cards_obj.items():
            if not isinstance(card, dict):
                enriched[card_id] = card
                continue
            cn = card.get("case_number")
            merged = dict(card)
            merged["case"] = case_index.get(cn)
            merged["escalated"] = (
                (str(cn) in escalated_case_numbers) if cn is not None else False
            )
            # attach issues for this case
            issues_for_case = None
            if cn is not None:
                if str(cn) in issues_by_case:
                    issues_for_case = issues_by_case[str(cn)]
                elif cn in issues_by_case:
                    issues_for_case = issues_by_case[cn]
            merged["issues"] = issues_for_case
            # attach bugs for this case
            bugs_for_case = None
            if cn is not None:
                if str(cn) in bugs_by_case:
                    bugs_for_case = bugs_by_case[str(cn)]
                elif cn in bugs_by_case:
                    bugs_for_case = bugs_by_case[cn]
            merged["bugs"] = bugs_for_case
            # attach details for this case
            details_for_case = None
            if cn is not None:
                if str(cn) in details_by_case:
                    details_for_case = details_by_case[str(cn)]
                elif cn in details_by_case:
                    details_for_case = details_by_case[cn]
            merged["details"] = details_for_case
            enriched[card_id] = merged
    elif isinstance(cards_obj, list):
        result_list = []
        for card in cards_obj:
            if isinstance(card, dict):
                cn = card.get("case_number")
                merged = dict(card)
                merged["case"] = case_index.get(cn)
                merged["escalated"] = (
                    (str(cn) in escalated_case_numbers) if cn is not None else False
                )
                # attach issues for this case
                issues_for_case = None
                if cn is not None:
                    if str(cn) in issues_by_case:
                        issues_for_case = issues_by_case[str(cn)]
                    elif cn in issues_by_case:
                        issues_for_case = issues_by_case[cn]
                merged["issues"] = issues_for_case
                # attach bugs for this case
                bugs_for_case = None
                if cn is not None:
                    if str(cn) in bugs_by_case:
                        bugs_for_case = bugs_by_case[str(cn)]
                    elif cn in bugs_by_case:
                        bugs_for_case = bugs_by_case[cn]
                merged["bugs"] = bugs_for_case
                # attach details for this case
                details_for_case = None
                if cn is not None:
                    if str(cn) in details_by_case:
                        details_for_case = details_by_case[str(cn)]
                    elif cn in details_by_case:
                        details_for_case = details_by_case[cn]
                merged["details"] = details_for_case
                result_list.append(merged)
            else:
                result_list.append(card)
        enriched = {"items": result_list}
    else:
        enriched = cards_obj


if __name__ == "__main__":
    mcp.run()
