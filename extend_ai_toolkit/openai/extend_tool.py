import json
from typing import Any

from agents import FunctionTool
from agents.run_context import RunContextWrapper

from extend_ai_toolkit.shared import ExtendAPI, Tool


def ExtendTool(api: ExtendAPI, tool: Tool) -> FunctionTool:
    async def on_invoke_tool(ctx: RunContextWrapper[Any], input_str: str) -> str:
        return await api.run(tool.method.value, **json.loads(input_str))

    parameters = tool.args_schema.model_json_schema()
    parameters["additionalProperties"] = False
    parameters["type"] = "object"

    if "description" in parameters:
        del parameters["description"]

    if "title" in parameters:
        del parameters["title"]

    if "properties" in parameters:
        for prop in parameters["properties"].values():
            if "title" in prop:
                del prop["title"]
            if "default" in prop:
                del prop["default"]

    return FunctionTool(
        name=tool.method.value,
        description=tool.description,
        params_json_schema=parameters,
        on_invoke_tool=on_invoke_tool,
        strict_json_schema=False
    )
