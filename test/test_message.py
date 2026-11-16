"""消息类型单元测试"""

import pytest
from core.message import (
    Message,
    MessageRole,
    MessageType,
    ToolCallMessage,
    ToolResultMessage,
)


# ---------------------------------------------------------------------------
# ToolCallMessage
# ---------------------------------------------------------------------------
class TestToolCallMessage:
    def test_construct_default(self):
        msg = ToolCallMessage(
            role=MessageRole.ASSISTANT,
            type=MessageType.TOOL_CALL,
            content="",
        )
        assert msg.tool_name == ""
        assert msg.tool_params == {}

    def test_construct_with_values(self):
        msg = ToolCallMessage(
            role=MessageRole.ASSISTANT,
            type=MessageType.TOOL_CALL,
            content="call weather",
            tool_name="get_weather",
            tool_params={"city": "beijing"},
        )
        assert msg.tool_name == "get_weather"
        assert msg.tool_params == {"city": "beijing"}

    def test_to_dict_includes_extra_fields(self):
        msg = ToolCallMessage(
            role=MessageRole.ASSISTANT,
            type=MessageType.TOOL_CALL,
            content="",
            tool_name="get_weather",
            tool_params={"city": "beijing"},
        )
        d = msg.to_dict()
        assert d["type"] == "tool_call"
        assert d["tool_name"] == "get_weather"
        assert d["tool_params"] == {"city": "beijing"}

    def test_from_dict_roundtrip(self):
        msg = ToolCallMessage(
            role=MessageRole.ASSISTANT,
            type=MessageType.TOOL_CALL,
            content="call weather",
            tool_name="get_weather",
            tool_params={"city": "beijing"},
        )
        restored = Message.from_dict(msg.to_dict())
        assert isinstance(restored, ToolCallMessage)
        assert restored.tool_name == "get_weather"
        assert restored.tool_params == {"city": "beijing"}
        assert restored.content == "call weather"

    def test_from_dict_missing_tool_params_defaults_to_dict(self):
        data = {
            "message_id": "x",
            "role": "assistant",
            "type": "tool_call",
            "content": "",
        }
        msg = Message.from_dict(data)
        assert isinstance(msg, ToolCallMessage)
        assert msg.tool_params == {}

    def test_from_dict_tool_params_not_dict_falls_back(self):
        data = {
            "message_id": "x",
            "role": "assistant",
            "type": "tool_call",
            "content": "",
            "tool_params": "oops-not-a-dict",
        }
        msg = Message.from_dict(data)
        assert msg.tool_params == {}


# ---------------------------------------------------------------------------
# ToolResultMessage
# ---------------------------------------------------------------------------
class TestToolResultMessage:
    def test_construct_default(self):
        msg = ToolResultMessage(
            role=MessageRole.TOOL,
            type=MessageType.TOOL_RESULT,
            content="ok",
        )
        assert msg.status == "unknown"

    def test_construct_with_status(self):
        msg = ToolResultMessage(
            role=MessageRole.TOOL,
            type=MessageType.TOOL_RESULT,
            content="ok",
            status="success",
        )
        assert msg.status == "success"

    @pytest.mark.parametrize("status,expected", [
        ("success", True),
        ("error", False),
        ("unknown", False),
    ])
    def test_is_success_property(self, status, expected):
        msg = ToolResultMessage(
            role=MessageRole.TOOL,
            type=MessageType.TOOL_RESULT,
            content="",
            status=status,
        )
        assert msg.is_success is expected

    def test_to_dict_includes_status(self):
        msg = ToolResultMessage(
            role=MessageRole.TOOL,
            type=MessageType.TOOL_RESULT,
            content="done",
            status="success",
        )
        d = msg.to_dict()
        assert d["type"] == "tool_result"
        assert d["status"] == "success"

    def test_from_dict_roundtrip(self):
        msg = ToolResultMessage(
            role=MessageRole.TOOL,
            type=MessageType.TOOL_RESULT,
            content="done",
            status="success",
        )
        restored = Message.from_dict(msg.to_dict())
        assert isinstance(restored, ToolResultMessage)
        assert restored.status == "success"
        assert restored.content == "done"

    def test_from_dict_missing_status_defaults_to_unknown(self):
        data = {
            "message_id": "x",
            "role": "tool",
            "type": "tool_result",
            "content": "",
        }
        msg = Message.from_dict(data)
        assert isinstance(msg, ToolResultMessage)
        assert msg.status == "unknown"
