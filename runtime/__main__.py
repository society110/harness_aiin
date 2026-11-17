"""运行假模型与 echo 工具的最小闭环：python -m runtime。"""

import argparse
import asyncio

from runtime.engine import RuntimeEngine
from tools.echo import EchoTool
from tools.registry import ToolRegistry


async def main() -> None:
    parser = argparse.ArgumentParser(description="假模型与 echo 工具的闭环演示")
    parser.add_argument("text", nargs="?", default="你好")
    args = parser.parse_args()

    registry = ToolRegistry()
    registry.register(EchoTool())
    response = await RuntimeEngine(registry).run(args.text)
    print(response.content)


if __name__ == "__main__":
    asyncio.run(main())
