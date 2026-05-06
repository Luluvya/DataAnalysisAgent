"""
ReAct Agent 核心实现
基于 LangGraph StateGraph 构建 Thought → Action → Observation 循环
"""
import json
import re
from typing import TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage

from llm import llm_call
from tool_registry import ToolRegistry


# ── State 定义 ────────────────────────────────────────────
class ReActState(TypedDict):
    messages: Annotated[list, add_messages]
    question: str
    history: list          # [(thought, action, observation), ...]
    thought: str
    action: dict           # {"tool_name": ..., "tool_input": ...}
    observation: str
    finish: any            # 最终结果，非空时结束循环
    step: int
    max_steps: int


# ── 节点：Reasoning ───────────────────────────────────────
def make_reasoning_node(system_prompt_template: str, tool_registry: ToolRegistry):
    async def reasoning_node(state: ReActState) -> ReActState:
        """LLM推理节点：生成 Thought/Action/Finish"""
        history_str = ""
        for i, (t, a, o) in enumerate(state["history"]):
            history_str += f"Step {i+1}:\nThought: {t}\nAction: {a}\nObservation: {o}\n\n"

        tools_desc = tool_registry.get_tools_description()
        prompt = system_prompt_template.format(
            tools=tools_desc,
            question=state["question"],
            history=history_str or "无"
        )

        response = await llm_call(
            system="你是一个数据分析智能体，严格按JSON格式输出。",
            user=prompt,
            temperature=0.1
        )

        print(f"\n[Step {state['step']+1}] LLM输出:\n{response}")

        # 解析JSON输出
        thought, action, finish = parse_react_output(response)

        return {
            **state,
            "thought": thought,
            "action": action,
            "finish": finish,
            "step": state["step"] + 1
        }
    return reasoning_node


# ── 节点：Action ─────────────────────────────────────────
def make_action_node(tool_registry: ToolRegistry):
    async def action_node(state: ReActState) -> ReActState:
        """工具调用节点：执行 Action，获取 Observation"""
        action = state.get("action")
        if not action or not isinstance(action, dict):
            observation = "无工具调用"
        else:
            tool_name = action.get("tool_name", "")
            tool_input = action.get("tool_input", "")
            print(f"[Tool] 调用工具: {tool_name}，输入: {tool_input}")
            observation = tool_registry.execute(tool_name, str(tool_input))
            print(f"[Tool] 观察结果: {observation[:200]}...")

        # 记录到历史
        new_history = state["history"] + [(
            state["thought"],
            str(state["action"]),
            observation
        )]

        return {
            **state,
            "observation": observation,
            "history": new_history
        }
    return action_node


# ── 路由：决定继续还是结束 ────────────────────────────────
def should_continue(state: ReActState) -> str:
    """条件边：有finish或超过最大步数则结束"""
    finish = state.get("finish")
    step = state.get("step", 0)
    max_steps = state.get("max_steps", 5)

    if finish is not None and finish != [] and finish != {} and finish != "":
        return "end"
    if step >= max_steps:
        return "end"
    return "continue"


# ── 构建 ReAct Graph ─────────────────────────────────────
def build_react_graph(system_prompt_template: str, tool_registry: ToolRegistry):
    """构建 ReAct LangGraph"""
    g = StateGraph(ReActState)

    reasoning = make_reasoning_node(system_prompt_template, tool_registry)
    action = make_action_node(tool_registry)

    g.add_node("reasoning", reasoning)
    g.add_node("action", action)

    g.set_entry_point("reasoning")
    g.add_conditional_edges(
        "reasoning",
        should_continue,
        {"end": END, "continue": "action"}
    )
    g.add_edge("action", "reasoning")

    return g.compile()


# ── 工具函数：解析LLM输出 ────────────────────────────────
def parse_react_output(text: str):
    """从LLM输出中提取 Thought/Action/Finish"""
    # 提取JSON块
    start = text.find('{')
    end = text.rfind('}')

    if start == -1 or end == -1:
        return text, None, None

    json_str = text[start:end+1]

    try:
        data = json.loads(json_str)
        thought = data.get("Thought", "")
        action = data.get("Action", None)
        finish = data.get("Finish", None)

        # 空action处理
        if action == {} or action is None:
            action = None

        # 空finish处理
        if finish == [] or finish == {} or finish == "":
            finish = None

        return thought, action, finish
    except json.JSONDecodeError:
        # JSON解析失败，尝试正则提取
        thought_match = re.search(r'"Thought"\s*:\s*"([^"]*)"', text)
        thought = thought_match.group(1) if thought_match else ""
        return thought, None, None


# ── ReAct Agent 运行入口 ─────────────────────────────────
async def run_react_agent(
    question: str,
    system_prompt_template: str,
    tool_registry: ToolRegistry,
    max_steps: int = 5
) -> any:
    """运行ReAct Agent，返回finish内容"""
    graph = build_react_graph(system_prompt_template, tool_registry)

    initial_state: ReActState = {
        "messages": [HumanMessage(content=question)],
        "question": question,
        "history": [],
        "thought": "",
        "action": {},
        "observation": "",
        "finish": None,
        "step": 0,
        "max_steps": max_steps
    }

    result = await graph.ainvoke(initial_state)
    return result.get("finish")
