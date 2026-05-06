"""
AnalysisAgent - 数据分析执行
基于 ReAct 架构，逐任务调用分析工具，输出结论+图表
"""
from react_agent import run_react_agent
from tools.analysis_tools import create_analysis_registry
from agents.agent_prompts import ANALYSIS_PROMPT


async def run_analysis_agent(tasks: list) -> list:
    """逐任务运行分析Agent，返回结果列表"""
    registry = create_analysis_registry()
    results = []

    for i, task in enumerate(tasks):
        print(f"\n  执行任务 {i+1}/{len(tasks)}: {task}")
        try:
            result = await run_react_agent(
                question=task,
                system_prompt_template=ANALYSIS_PROMPT,
                tool_registry=registry,
                max_steps=4
            )
            if isinstance(result, dict):
                results.append({
                    "task": task,
                    "text": result.get("text", "分析完成"),
                    "figure_path": result.get("figure_path", "")
                })
            else:
                results.append({
                    "task": task,
                    "text": str(result) if result else "分析完成",
                    "figure_path": ""
                })
        except Exception as e:
            print(f"  任务执行出错: {e}")
            results.append({
                "task": task,
                "text": f"分析过程中出现错误: {e}",
                "figure_path": ""
            })
    return results
