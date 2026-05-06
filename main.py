"""
DataAnalysisAgent - 商品销售数据分析智能体
基于 LangGraph Plan-and-Solve + ReAct 架构
运行方式: python main.py
输出: out/analysis_report.md + out/figures/
"""
import asyncio
import os
from agents.planning_agent import run_planning_agent
from agents.analysis_agent import run_analysis_agent
from agents.report_agent import run_report_agent

async def main():
    print("=" * 60)
    print("DataAnalysisAgent · 商品销售数据分析智能体")
    print("=" * 60)

    # Step 1: 规划Agent - 探查数据，生成分析任务列表
    print("\n[Step 1/3] PlanningAgent 正在探查数据...")
    tasks = await run_planning_agent()
    print(f"\n规划完成，共 {len(tasks)} 个分析任务：")
    for i, t in enumerate(tasks, 1):
        print(f"  {i}. {t}")

    # Step 2: 分析Agent - 逐任务执行分析
    print("\n[Step 2/3] AnalysisAgent 正在执行分析...")
    results = await run_analysis_agent(tasks)
    print(f"\n分析完成，共完成 {len(results)} 个任务")

    # Step 3: 报告Agent - 整合结果，生成报告
    print("\n[Step 3/3] ReportAgent 正在生成报告...")
    report = await run_report_agent(results)

    # 保存报告
    os.makedirs("out", exist_ok=True)
    with open("out/analysis_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print("\n" + "=" * 60)
    print("✅ 分析完成！")
    print("📄 报告路径: out/analysis_report.md")
    print("📊 图表路径: out/figures/")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
