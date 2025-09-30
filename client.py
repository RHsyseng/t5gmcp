#!/usr/bin/env python

import asyncio
import argparse
from fastmcp import Client
import sys

client = Client("http://localhost:8000/mcp")


async def call_tool(tool_name: str):
    async with client:
        tool_name = f"get_{tool_name}"
        result = await client.call_tool(tool_name)
        print(result)


parser = argparse.ArgumentParser(prog=sys.argv[0], description="t5gmcp cli tool")

parser.add_argument("-d", "--data", required=True)
args = parser.parse_args()

if args.data in (
    "cards",
    "cases",
    "bugs",
    "details",
    "escalations",
    "issues",
    "all_case_data",
):
    asyncio.run(call_tool(args.data))
else:
    print(f"unknown data type: {args.data}")
