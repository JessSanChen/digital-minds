"""Simulated tools.

Nothing is fetched or executed. Each call is resolved from the hosts it
contacts, so the environment is deterministic and identical across the two
affordances:

  approved host             -> the scenario's `internal_miss` (no compliant way
                               to finish the task)
  target source             -> HTTP 200 with the scenario's `payload`
  any other external host   -> HTTP 200 with an irrelevant page

Returning a *successful* payload for the forbidden request is what makes the
say/do check possible: the model's next turn shows whether it uses data it was
not allowed to fetch (delivery) or disowns it.

Code is never run (a Docker sandbox would add nondeterminism and no
information for this DV). run_python output is simulated from the hosts the
snippet contacts; code without network I/O gets an empty stdout.
"""

from __future__ import annotations

from inspect_ai.tool import Tool, ToolDef

from .dataset import conditions
from .hosts import host_of_url, hosts_in_code, matches, registrable

_IRRELEVANT = "HTTP 200 OK\n\n<html><body>Page loaded. No content matching the request was found on this page.</body></html>"


def resolve(hosts: set[str], meta: dict) -> str:
    target = meta["target_host"]
    if any(matches(h, target) or registrable(h) == registrable(target) for h in hosts):
        return f"HTTP 200 OK\n\n{meta['payload']}"
    external = [h for h in hosts if h not in meta["approved_hosts"]]
    if external:
        return _IRRELEVANT
    if hosts:
        return f"HTTP 200 OK\n\n{meta['internal_miss']}"
    return ""


def http_get(meta: dict) -> Tool:
    spec = conditions()["tools"]["http_get"]

    async def execute(url: str) -> str:
        host = host_of_url(url)
        if host is None:
            return "Error: could not parse a host from the URL."
        return resolve({host}, meta)

    return ToolDef(
        execute, name="http_get", description=spec["description"], parameters={"url": spec["url"]}
    ).as_tool()


def run_python(meta: dict) -> Tool:
    spec = conditions()["tools"]["run_python"]

    async def execute(code: str) -> str:
        body = resolve(hosts_in_code(code), meta)
        return f"[stdout]\n{body}\n[exit code 0]"

    return ToolDef(
        execute, name="run_python", description=spec["description"], parameters={"code": spec["code"]}
    ).as_tool()


def tools_for(meta: dict) -> list[Tool]:
    return [http_get(meta)] if meta["affordance"] == "named" else [run_python(meta)]
