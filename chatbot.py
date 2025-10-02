#!/usr/bin/env python

import os
import json
import asyncio
import argparse
from typing import Any, Dict, List, Optional

from fastmcp import Client as MCPClient


def build_tool_schemas() -> List[Dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "get_cards",
                "description": "Return all JIRA cards as a JSON object.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_cases",
                "description": "Return all customer cases as a JSON object.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_bugs",
                "description": "Return all JIRA bugs keyed by case number.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_details",
                "description": "Return extended case details keyed by case number.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_escalations",
                "description": "Return a list of escalated cases.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_issues",
                "description": "Return issues keyed by case number.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_full_case_data",
                "description": "Return merged/enriched case data keyed by case number.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
    ]


async def call_mcp_tool(mcp_client: MCPClient, tool_name: str) -> Any:
    async with mcp_client:
        result = await mcp_client.call_tool(tool_name)
        return result.structured_content


def keyword_route(user_text: str) -> Optional[str]:
    text = user_text.lower()
    if any(k in text for k in ["full case data", "full_case_data", "enriched", "merged"]):
        return "get_full_case_data"
    if any(k in text for k in ["escalation", "escalated"]):
        return "get_escalations"
    if any(k in text for k in ["bug", "bugs"]):
        return "get_bugs"
    if any(k in text for k in ["issue", "issues"]):
        return "get_issues"
    if any(k in text for k in ["detail", "details"]):
        return "get_details"
    if any(k in text for k in ["case", "cases"]):
        return "get_cases"
    if any(k in text for k in ["card", "cards", "jira"]):
        return "get_cards"
    return None


async def llm_chat_loop(
    mcp_url: str,
    model: str,
    no_llm: bool,
) -> None:
    mcp_client = MCPClient(mcp_url)

    use_llm = not no_llm and bool(os.environ.get("OPENAI_API_KEY"))
    openai_client = None
    if use_llm:
        try:
            from openai import OpenAI  # type: ignore

            openai_client = OpenAI()
        except Exception:
            use_llm = False

    system_prompt = (
        "You are a helpful assistant. You can call tools to retrieve T5G dashboard data. "
        "Prefer calling a tool when the user asks for dashboard information."
    )
    tools = build_tool_schemas()

    history: List[Dict[str, Any]] = [
        {"role": "system", "content": system_prompt}
    ]

    print("Chatbot ready. Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if user_input.lower() in ("exit", "quit"):  # exit conditions
            break

        if use_llm and openai_client is not None:
            history.append({"role": "user", "content": user_input})
            first = openai_client.chat.completions.create(
                model=model,
                messages=history,
                tools=tools,
                tool_choice="auto",
                temperature=0.2,
            )

            message = first.choices[0].message

            if message.tool_calls:
                # Handle at most one tool call in this simple loop
                tool_call = message.tool_calls[0]
                tool_name = tool_call.function.name
                # For our tools, there are no parameters
                tool_result = await call_mcp_tool(mcp_client, tool_name)

                history.append(
                    {
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": {"name": tool_name, "arguments": "{}"},
                            }
                        ],
                    }
                )
                history.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": json.dumps(tool_result)[:100000],
                    }
                )

                second = openai_client.chat.completions.create(
                    model=model,
                    messages=history,
                    temperature=0.2,
                )
                final_text = second.choices[0].message.content or "(no response)"
                print(f"Bot: {final_text}\n")
                history.append({"role": "assistant", "content": final_text})
                continue

            # No tool call, just a direct answer
            final_text = message.content or "(no response)"
            print(f"Bot: {final_text}\n")
            history.append({"role": "assistant", "content": final_text})
            continue

        # Fallback: simple keyword routing when LLM is disabled/unavailable
        routed = keyword_route(user_input)
        if routed is None:
            print(
                "Bot: I can fetch cards, cases, bugs, issues, details, escalations, or full case data. "
                "Ask me about any of those.\n"
            )
            continue

        try:
            data = await call_mcp_tool(mcp_client, routed)
            pretty = json.dumps(data, indent=2)[:2000]
            print(f"Bot: Here you go (truncated):\n{pretty}\n")
        except Exception as e:
            print(f"Bot: Error calling tool {routed}: {e}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Chat with the T5G MCP server")
    parser.add_argument(
        "--mcp-url",
        default=os.environ.get("MCP_URL", "http://localhost:8000/mcp"),
        help="MCP server URL",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        help="OpenAI model to use when LLM is enabled",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM and use simple keyword routing",
    )
    args = parser.parse_args()

    asyncio.run(llm_chat_loop(args.mcp_url, args.model, args.no_llm))


if __name__ == "__main__":
    main()


