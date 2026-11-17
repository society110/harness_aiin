"""验证假模型与工具闭环，不访问真实 API。"""

import asyncio

import pytest

from core.message import MessageRole, MessageType, ToolCallMessage
from runtime.engine import RuntimeEngine
from tools.echo import EchoTool
from tools.registry import ToolRegistry


@pytest.mark.parametrize("text", ["你好", ""])
def test_echo_roundtrip(text):
    registry = ToolRegistry()
    registry.register(EchoTool())

    response = asyncio.run(RuntimeEngine(registry).run(text))

    assert response.role == MessageRole.ASSISTANT
    assert response.type == MessageType.TEXT
    assert response.content == f"收到工具结果：{text}"


@pytest.mark.parametrize("params", [{}, {"text": None}, {"text": 123}])
def test_invalid_tool_input_becomes_error(params):
    registry = ToolRegistry()
    registry.register(EchoTool())
    request = ToolCallMessage(
        role=MessageRole.ASSISTANT,
        type=MessageType.TOOL_CALL,
        content="",
        tool_name="echo",
        tool_params=params,
    )

    result = asyncio.run(RuntimeEngine(registry)._execute_tool(request))

    assert result.status == "error"
    assert result.parent_id == request.message_id
    assert "ValueError" in result.content


def test_missing_tool_returns_feedback():
    response = asyncio.run(RuntimeEngine(ToolRegistry()).run("你好"))
    assert response.content == "收到工具结果：工具不存在:echo"


def test_turn_limit_stops_before_final_reply():
    registry = ToolRegistry()
    registry.register(EchoTool())
    with pytest.raises(RuntimeError, match="超过最大推理轮数"):
        asyncio.run(RuntimeEngine(registry, max_turns=1).run("你好"))
