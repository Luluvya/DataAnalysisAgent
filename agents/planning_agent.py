"""
PlanningAgent - 数据探查与任务规划
基于 ReAct 架构，探查数据后输出分析任务列表
"""
from react_agent import run_react_agent
from tools.exploration_tools import create_exploration_registry
from agents.agent_prompts import PLANNING_PROMPT


async def run_planning_agent() -> list:
    """运行规划Agent，返回分析任务列表"""
    registry = create_exploration_registry()

    result = await run_react_agent(
        question="请探查数据结构，然后规划3-5个有价值的分析任务",
        system_prompt_template=PLANNING_PROMPT,
        tool_registry=registry,
        max_steps=6
    )

    if isinstance(result, list) and len(result) > 0:
        return result
    if isinstance(result, str):
        lines = [l.strip() for l in result.split('\n') if l.strip()]
        return lines[:5] if lines else ["分析商品销售趋势", "分析品类销售表现", "分析用户消费行为"]
    return [
        "分析商品销售趋势",
        "分析各品类销售表现与占比",
        "分析用户消费行为分布",
        "分析各地区销售情况",
        "分析销售额与其他指标的相关性"
    ]
