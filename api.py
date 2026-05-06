"""
DataAnalysisAgent Web API
FastAPI 后端，提供网页交互界面
"""
import asyncio
import os
import json
import base64
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd

from agents.planning_agent import run_planning_agent
from agents.analysis_agent import run_analysis_agent
from agents.report_agent import run_report_agent

app = FastAPI(title="DataAnalysisAgent API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# 存储分析状态
analysis_state = {
    "status": "idle",  # idle | running | done | error
    "progress": 0,
    "logs": [],
    "tasks": [],
    "results": [],
    "report": "",
    "figures": []
}


def log(msg: str):
    print(msg)
    analysis_state["logs"].append(msg)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """上传CSV数据文件"""
    content = await file.read()
    os.makedirs("data", exist_ok=True)
    with open("data/sales_data.csv", "wb") as f:
        f.write(content)
    # 预览
    df = pd.read_csv("data/sales_data.csv")
    return {
        "rows": len(df),
        "columns": list(df.columns),
        "preview": df.head(5).to_dict(orient="records")
    }


@app.post("/analyze")
async def analyze():
    """触发完整分析流程"""
    # 重置状态
    analysis_state.update({
        "status": "running",
        "progress": 0,
        "logs": [],
        "tasks": [],
        "results": [],
        "report": "",
        "figures": []
    })

    asyncio.create_task(_run_analysis())
    return {"message": "分析已启动"}


async def _run_analysis():
    """后台运行完整分析流程"""
    try:
        os.makedirs("out/figures", exist_ok=True)

        # Step 1: 规划
        log("🔍 [Step 1/3] PlanningAgent 正在探查数据...")
        analysis_state["progress"] = 10
        tasks = await run_planning_agent()
        analysis_state["tasks"] = tasks
        analysis_state["progress"] = 30
        log(f"✅ 规划完成，共 {len(tasks)} 个分析任务")
        for i, t in enumerate(tasks, 1):
            log(f"   {i}. {t}")

        # Step 2: 分析
        log("\n📊 [Step 2/3] AnalysisAgent 正在执行分析...")
        results = await run_analysis_agent(tasks)
        analysis_state["results"] = results
        analysis_state["progress"] = 70

        # 收集图表
        figures = []
        for r in results:
            fp = r.get("figure_path", "")
            if fp and os.path.exists(fp):
                with open(fp, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                figures.append({
                    "task": r["task"],
                    "path": fp,
                    "b64": f"data:image/png;base64,{b64}"
                })
        analysis_state["figures"] = figures
        log(f"✅ 分析完成，生成 {len(figures)} 张图表")

        # Step 3: 报告
        log("\n📝 [Step 3/3] ReportAgent 正在生成报告...")
        report = await run_report_agent(results)
        analysis_state["report"] = report
        analysis_state["progress"] = 100

        # 保存报告
        with open("out/analysis_report.md", "w", encoding="utf-8") as f:
            f.write(report)

        analysis_state["status"] = "done"
        log("\n✅ 分析完成！报告已生成。")

    except Exception as e:
        analysis_state["status"] = "error"
        log(f"❌ 分析出错: {e}")


@app.get("/status")
async def get_status():
    """获取分析进度和结果"""
    return analysis_state


@app.get("/report")
async def get_report():
    """获取Markdown报告"""
    return {"report": analysis_state.get("report", "")}


@app.post("/generate-sample")
async def generate_sample():
    """生成示例数据"""
    import numpy as np
    np.random.seed(42)
    n = 3900
    categories = ['服装', '配饰', '鞋类', '外套']
    regions = ['华东', '华南', '华北', '华西', '华中']
    genders = ['男', '女']
    dates = pd.date_range('2024-01-01', '2024-12-31', periods=n)
    ages = np.random.choice(['<20', '20-29', '30-39', '40-49', '50-59', '60+'], n,
                             p=[0.08, 0.25, 0.28, 0.20, 0.12, 0.07])
    category = np.random.choice(categories, n, p=[0.45, 0.30, 0.15, 0.10])
    region = np.random.choice(regions, n)
    gender = np.random.choice(genders, n)
    base_price = {'服装': 65, '配饰': 55, '鞋类': 75, '外套': 90}
    amounts = [round(base_price[c] * np.random.uniform(0.6, 1.8), 2) for c in category]
    quantities = np.random.randint(1, 5, n)
    totals = [round(a * q, 2) for a, q in zip(amounts, quantities)]
    df = pd.DataFrame({
        'date': dates.strftime('%Y-%m-%d'),
        'category': category,
        'region': region,
        'gender': gender,
        'age_group': ages,
        'unit_price': amounts,
        'quantity': quantities,
        'total_amount': totals
    })
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/sales_data.csv", index=False, encoding="utf-8-sig")
    return {
        "rows": len(df),
        "columns": list(df.columns),
        "preview": df.head(5).to_dict(orient="records")
    }
