"""用于验证运行闭环的回声工具。"""

from time import perf_counter
from typing import Any

from core.tool import Tool, ToolResult


class EchoTool(Tool):
    def name(self) -> str:
        return "echo"

    def description(self) -> str:
        return "原样返回输入的文本"

    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "需要原样返回的文本"},
            },
            "required": ["text"],
        }

    async def call(self, params: dict[str, Any]) -> ToolResult:
        started = perf_counter()
        text = params.get("text")
        if not isinstance(text, str):
            raise ValueError("text 必须是字符串")
        return ToolResult(
            success=True,
            content=text,
            execution_time=perf_counter() - started,
        )
