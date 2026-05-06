"""
工具注册表
使用 LangChain Tool 装饰器注册工具
"""
import json
import pandas as pd
from typing import Callable, Dict, Any
from dataclasses import dataclass


@dataclass
class Tool:
    name: str
    description: str
    func: Callable


class ToolRegistry:
    """工具注册表 - 管理所有可调用工具"""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, name: str, description: str):
        """装饰器：注册工具"""
        def decorator(func: Callable):
            self._tools[name] = Tool(name=name, description=description, func=func)
            return func
        return decorator

    def get_tools_description(self) -> str:
        """返回所有工具的描述，用于注入Prompt"""
        if not self._tools:
            return "无可用工具"
        lines = []
        for name, tool in self._tools.items():
            lines.append(f"- {name}: {tool.description}")
        return "\n".join(lines)

    def execute(self, tool_name: str, tool_input: str) -> str:
        """执行工具"""
        if tool_name not in self._tools:
            return f"错误：工具 '{tool_name}' 不存在，可用工具：{list(self._tools.keys())}"
        try:
            result = self._tools[tool_name].func(tool_input)
            return str(result)
        except Exception as e:
            return f"工具执行错误: {e}"

    @property
    def tool_names(self):
        return list(self._tools.keys())
