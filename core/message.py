"""消息类型和接口定义"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Type


class MessageRole(str, Enum):
    """消息角色"""

    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    SYSTEM = "system"


class MessageType(str, Enum):
    """消息类型"""

    TEXT = "text"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    EVENT = "event"


@dataclass
class Message:
    """通用消息类"""

    role: MessageRole
    type: MessageType
    content: str
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "message_id": self.message_id,
            "role": self.role.value,
            "type": self.type.value,
            "content": self.content,
            "parent_id": self.parent_id,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }

    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """从字典创建，按 type 自动分发到对应子类"""
        target = _REGISTRY.get(MessageType(data["type"]), cls)
        return target._build(data)

    @classmethod
    def _build(cls, data: Dict[str, Any]) -> "Message":
        """按基础字段构造，子类可重写以还原扩展字段"""
        return cls(
            role=MessageRole(data["role"]),
            type=MessageType(data["type"]),
            content=data["content"],
            message_id=data.get("message_id", str(uuid.uuid4())),
            parent_id=data.get("parent_id"),
            metadata=data.get("metadata", {}),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
        )


@dataclass
class ToolCallMessage(Message):
    """工具调用消息"""

    tool_name: str = ""
    tool_params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["tool_name"] = self.tool_name
        data["tool_params"] = self.tool_params
        return data

    @classmethod
    def _build(cls, data: Dict[str, Any]) -> "ToolCallMessage":
        message = super()._build(data)
        message.tool_name = str(data.get("tool_name", ""))
        params = data.get("tool_params", {})
        message.tool_params = params if isinstance(params, dict) else {}
        return message


@dataclass
class ToolResultMessage(Message):
    """工具结果消息"""

    status: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["status"] = self.status
        return data

    @classmethod
    def _build(cls, data: Dict[str, Any]) -> "ToolResultMessage":
        message = super()._build(data)
        message.status = str(data.get("status", "unknown"))
        return message

    @property
    def is_success(self) -> bool:
        return self.status == "success"


# 消息类型注册表：新增消息类型 = 加枚举值 + 定义子类 + 在此登记，from_dict 即可自动还原
_REGISTRY: Dict[MessageType, Type[Message]] = {
    MessageType.TOOL_CALL: ToolCallMessage,
    MessageType.TOOL_RESULT: ToolResultMessage,
}
