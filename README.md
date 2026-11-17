# Inai：自建 Agent Harness

参考《Harness Engineering Guide》4.7 和 OpenHarness，逐步实现自己的 Agent 运行时。

## 当前进度（2026-11-17）

已跑通 **假模型 → 真实工具 → 假模型最终回复** 的最小闭环。目前 `_infer()` 使用固定逻辑模拟模型决策，运行演示不需要 API Key，也不会请求真实模型。

```text
用户输入
  → 写入 SessionState 消息历史
  → 假模型提出 echo 工具调用请求
  → RuntimeEngine 从 ToolRegistry 查找并执行工具
  → 将工具结果写入消息历史
  → 再次调用假模型
  → 返回最终文本
```

### 已完成

- 消息模型：普通消息、工具调用消息、工具结果消息，以及序列化和反序列化。
- 会话状态：保存会话 ID、消息历史和当前推理轮数；每次 `run()` 创建独立会话。
- 工具接口与注册表：注册工具、查询工具、提供工具参数 Schema。
- 运行时循环：保存模型回复、执行工具、回写结果、继续推理；无工具调用时结束。
- 工具错误反馈：工具不存在、执行异常或返回失败时，转换成失败的工具结果消息。
- 调用关联：工具结果通过 `parent_id` 关联原工具调用消息。
- 轮数限制：`max_turns` 默认 10，耗尽后抛出异常，避免无限循环。
- `EchoTool`：校验 `text` 必须为字符串，原样返回文本并记录执行耗时。
- 命令行入口与测试：已验证普通文本、空文本、非法参数、工具缺失和轮数限制。

### 主要文件

| 文件 | 职责 |
| --- | --- |
| `core/message.py` | 消息类型、工具调用与结果消息 |
| `core/agent.py` | Agent 配置、执行状态枚举 |
| `core/tool.py` | 工具接口、工具结果和 Schema 定义 |
| `core/event.py` | 事件数据定义，尚未接入运行循环 |
| `runtime/state.py` | `SessionState`，保存一次运行的会话数据 |
| `runtime/engine.py` | 推理、工具执行和循环控制 |
| `runtime/__main__.py` | 注册 echo 工具并启动演示 |
| `tools/registry.py` | 工具注册与查找 |
| `tools/echo.py` | 用于验证闭环的回声工具 |
| `test/test_message.py` | 消息模型测试 |
| `test/test_runtime.py` | 工具与运行闭环测试 |

## 运行演示

在项目根目录 `H:\code2\inai` 执行：

```powershell
python -X utf8 -m runtime "你好，harness"
```

预期输出：

```text
收到工具结果：你好，harness
```

不传文本时默认使用“你好”。当前假模型第一次固定请求 `echo`，收到工具结果后返回文本；它还不会根据任务自主选择工具。

## 验证

需要安装 `pytest`。执行以下命令，只运行本地消息和运行时测试：

```powershell
python -m pytest test/test_message.py test/test_runtime.py -q
```

最近一次验证结果：**21 passed**。

## 下一步

1. 替换 `_infer()` 的模拟逻辑，接入真实模型，并适配工具调用请求和结果格式。
2. 验证真实模型能完成“请求工具 → 收到结果 → 最终回答”的闭环。
3. 将已有事件定义接入运行时，向外输出开始、工具执行、结束等进度。

当前尚未实现发布/订阅、会话持久化和恢复，也未在运行时接入权限检查或工具超时。消息历史只保留在本次 `run()` 的内存中；参数 Schema 只用于描述，`EchoTool` 自行校验输入，尚无通用 Schema 校验器。
