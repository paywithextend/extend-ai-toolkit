"""Generate capability documentation from the executable catalog."""

from pathlib import Path

from extend_ai_toolkit import ExecutionPolicy, list_tool_specs
from extend_ai_toolkit.shared import Configuration


def render():
    lines = [
        "# Tool capabilities",
        "",
        "Generated from the shared catalog. Discovery and invocation use the same host allowlist.",
        "",
        "| Tool | Required capabilities | Effect |",
        "| --- | --- | --- |",
    ]
    policy = ExecutionPolicy.from_configuration(Configuration.all_tools())
    for tool in list_tool_specs(policy=policy):
        scopes = ", ".join(
            scope["product"] + "." + action
            for scope in tool.required_scopes
            for action in scope["actions"]
        )
        lines.append(f"| `{tool.name}` | {scopes} | {tool.side_effect_class} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    Path(__file__).resolve().parents[1].joinpath("CAPABILITIES.md").write_text(render())
