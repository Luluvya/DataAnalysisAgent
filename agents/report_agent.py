"""
ReportAgent - 报告生成
无工具调用，整合分析结果生成总分总结构Markdown报告
"""
import json
from llm import llm_call
from agents.agent_prompts import REPORT_PROMPT


async def run_report_agent(results: list) -> str:
    """运行报告Agent，返回Markdown报告字符串"""
    results_json = json.dumps(results, ensure_ascii=False, indent=2)

    report = await llm_call(
        system="你是专业的数据分析报告撰写专家，擅长将数据分析结果整合为清晰的商业报告。",
        user=REPORT_PROMPT.format(results=results_json),
        max_tokens=3000,
        temperature=0.3
    )

    if "# 执行摘要" in report:
        start_idx = report.find("# 执行摘要")
        report = report[start_idx:]

    return report
