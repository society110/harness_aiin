"""
state 就是状态：保存 Agent 当前运行到哪里、已经发生过什么。
"""

import uuid
from dataclasses import dataclass, field
from core.message import Message


#会话的工作记录本
@dataclass
class SessionState:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))#会话id
    messages: list[Message] = field(default_factory=list)#消息列表 用来存历史
    current_turn: int = 0

    #加消息到消息列表 给模型读
    def add_message(self, message: Message) -> None:
        self.messages.append(message)