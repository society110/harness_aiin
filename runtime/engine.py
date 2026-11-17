"""

"""
from runtime.state import SessionState
from core.message import Message, MessageType, ToolCallMessage, MessageRole,ToolResultMessage
from tools.registry import ToolRegistry


class RuntimeEngine:
    def __init__(self, tool_registry: ToolRegistry,max_turns:int = 10):
        if max_turns < 1:
            raise ValueError("max_turns 必须大于 0")

        self.tool_registry = tool_registry
        self.max_turns = max_turns


    async def _execute_tool(self, tool_call: ToolCallMessage) -> ToolResultMessage:
        tool = self.tool_registry.get(tool_call.tool_name)
        """如果没工具 显示工具为空"""
        if not tool:
            return ToolResultMessage(
                role=MessageRole.TOOL,
                type=MessageType.TOOL_RESULT,
                parent_id=tool_call.message_id,
                content=f"工具不存在:{tool_call.tool_name}",
                status="error",
            )
        """尝试调用工具 报错连着错误返回给模型 让模型返回给用户"""
        try:
            result = await tool.call(tool_call.tool_params)

            return ToolResultMessage(
                role=MessageRole.TOOL,
                type=MessageType.TOOL_RESULT,
                parent_id=tool_call.message_id,
                content=result.content,
                status="success" if result.success else "error",
            )
        except Exception as exc:
            return ToolResultMessage(
                role=MessageRole.TOOL,
                type=MessageType.TOOL_RESULT,
                parent_id=tool_call.message_id,
                content=f"{type(exc).__name__}: {exc}",
                status="error",
            )
    # 这里由你实现
    #现在里面的假逻辑是为了调试，但 _infer() 本身的职责是“调用模型，获得下一步回应”。
    async def _infer(self, state: SessionState) -> Message:
        if not state.messages:
            raise ValueError("推理前需要先添加消息")
        #取最后一条消息
        last_message = state.messages[-1]
        if last_message.type == MessageType.TOOL_RESULT:
            return Message(
                role=MessageRole.ASSISTANT,
                type=MessageType.TEXT,
                content=f"收到工具结果：{last_message.content}",
            )
        #只是提出工具调用请求，这里不会执行工具
        return ToolCallMessage(
            role=MessageRole.ASSISTANT,
            type=MessageType.TOOL_CALL,
            content="调用 echo 工具",
            tool_name="echo",
            tool_params={"text": last_message.content},
        )

    async def run(self, user_input: str) -> Message:
        state = SessionState()

        user_message = Message(
            role=MessageRole.USER,
            type=MessageType.TEXT,
            content=user_input,
        )

        state.add_message(user_message)
        """先获取回应 再看是否要工具调用 有则执行 结果放进去 没有则返回结果"""
        for _ in range(self.max_turns):
            state.current_turn += 1

            response = await self._infer(state)
            state.add_message(response)

            if isinstance(response, ToolCallMessage):
                tool_result = await self._execute_tool(response)
                state.add_message(tool_result)
            else:
                return response

        raise RuntimeError("超过最大推理轮数")
