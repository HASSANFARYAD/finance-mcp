import argparse
import json
import os
import sys
from typing import Any

import anyio
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

DEFAULT_SERVER_URL = "http://127.0.0.1:8080/sse"
DEFAULT_TOOL_NAMES = [
    "reports_summary",
    "reports_monthly",
    "company_profile_get",
    "tax_configs_list",
    "invoices_list",
    "expenses_list",
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Test MCP tools via SSE using JWT or API key authentication."
    )
    parser.add_argument(
        "--server-url",
        default=os.environ.get("MCP_SERVER_URL", DEFAULT_SERVER_URL),
        help="MCP SSE server URL (default: env MCP_SERVER_URL or %(default)s)",
    )
    parser.add_argument(
        "--auth",
        choices=["api_key", "jwt", "both", "auto"],
        default="auto",
        help="Authentication mode (default: auto)",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("MCP_API_KEY"),
        help="API key (or set MCP_API_KEY env var)",
    )
    parser.add_argument(
        "--jwt",
        default=os.environ.get("MCP_JWT"),
        help="JWT access token (or set MCP_JWT env var)",
    )
    parser.add_argument(
        "--tool",
        action="append",
        help="Tool name to call (repeatable). If omitted, a safe default set is used.",
    )
    parser.add_argument(
        "--args",
        action="append",
        default=[],
        help="JSON arguments for the corresponding --tool (repeatable).",
    )
    return parser.parse_args()


def _build_headers(mode: str, api_key: str | None, jwt: str | None) -> dict[str, str]:
    headers: dict[str, str] = {}
    if mode == "api_key" and api_key:
        headers["x-api-key"] = api_key
    elif mode == "jwt" and jwt:
        headers["Authorization"] = f"Bearer {jwt}"
    return headers


def _resolve_modes(auth: str, api_key: str | None, jwt: str | None) -> list[str]:
    if auth == "both":
        return ["api_key", "jwt"]
    if auth == "api_key":
        return ["api_key"]
    if auth == "jwt":
        return ["jwt"]
    # auto
    if api_key and jwt:
        return ["api_key", "jwt"]
    if api_key:
        return ["api_key"]
    if jwt:
        return ["jwt"]
    return []


def _build_tool_calls(
    tool_names: list[str] | None,
    tool_args: list[str],
) -> list[tuple[str, dict[str, Any] | None]]:
    if not tool_names:
        return [(name, None) for name in DEFAULT_TOOL_NAMES]

    calls: list[tuple[str, dict[str, Any] | None]] = []
    for idx, name in enumerate(tool_names):
        raw = tool_args[idx] if idx < len(tool_args) else None
        if raw:
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON for --args at index {idx}: {exc}") from exc
            if not isinstance(parsed, dict):
                raise ValueError(f"--args at index {idx} must be a JSON object")
            calls.append((name, parsed))
        else:
            calls.append((name, None))
    return calls


async def _run_for_mode(
    server_url: str,
    mode: str,
    headers: dict[str, str],
    tool_calls: list[tuple[str, dict[str, Any] | None]],
) -> int:
    print(f"== Testing MCP tools ({mode}) ==")
    async with sse_client(server_url, headers=headers) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            available = {tool.name for tool in tools.tools}
            print(f"Connected. Server reports {len(available)} tools.")

            exit_code = 0
            for name, args in tool_calls:
                if name not in available:
                    print(f"[skip] Tool not available: {name}")
                    exit_code = 1
                    continue
                try:
                    result = await session.call_tool(name, args)
                except Exception as exc:
                    print(f"[error] {name}: {exc}")
                    exit_code = 1
                    continue

                if result.isError:
                    print(f"[fail] {name}: {result.content}")
                    exit_code = 1
                else:
                    print(f"[ok] {name}")
            return exit_code


def main() -> int:
    args = _parse_args()
    modes = _resolve_modes(args.auth, args.api_key, args.jwt)
    if not modes:
        print("Missing credentials. Provide --api-key or --jwt (or set MCP_API_KEY/MCP_JWT).")
        return 2

    try:
        tool_calls = _build_tool_calls(args.tool, args.args)
    except ValueError as exc:
        print(str(exc))
        return 2

    exit_code = 0
    for mode in modes:
        headers = _build_headers(mode, args.api_key, args.jwt)
        try:
            code = anyio.run(
                _run_for_mode,
                args.server_url,
                mode,
                headers,
                tool_calls,
            )
        except Exception as exc:
            print(f"[error] {mode}: {exc}")
            code = 1
        exit_code = max(exit_code, code)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
