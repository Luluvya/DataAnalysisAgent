# DataAnalysisAgent · 智能商品销售数据分析助手

> 基于 LangGraph Plan-and-Solve + ReAct 混合架构，面向商品销售数据分析场景，自动完成数据探查、多维度分析、可视化图表生成与专业报告输出。

## 📝 项目简介

商品销售数据分析存在分析维度多、人工耗时长、报告质量参差不齐等问题。本项目设计了三Agent流水线（规划→分析→报告），一键自动化分析商品销售数据并生成图文并茂的深度分析报告。

## ✨ 核心功能

- [x] **PlanningAgent**：自动探查数据结构，规划 3-5 个关键分析任务
- [x] **AnalysisAgent**：调用数据分析工具，执行销售趋势/品类/地区/用户行为等多维度分析，生成可视化图表
- [x] **ReportAgent**：综合所有任务结论，输出总分总结构的图文并茂 Markdown 报告

## 🛠️ 技术栈

- **Agent 框架**：LangGraph（StateGraph + 条件边）
- **大语言模型**：DeepSeek-V3（via 硅基流动 API）
- **ReAct 实现**：基于 LangGraph 节点构建 Thought→Action→Observation 循环
- **数据分析**：Pandas + Matplotlib
- **架构模式**：Plan-and-Solve 统领全局，ReAct 负责底层推理与工具调用

## 📁 项目结构

```
DataAnalysisAgent/
├── main.py                    # 主入口，串联三个Agent
├── react_agent.py             # ReAct Agent 核心实现（LangGraph）
├── llm.py                     # LLM 调用封装
├── tool_registry.py           # 工具注册表
├── agents/
│   ├── planning_agent.py      # 规划Agent
│   ├── analysis_agent.py      # 分析Agent
│   └── report_agent.py        # 报告Agent
├── tools/
│   ├── exploration_tools.py   # 数据探查工具
│   └── analysis_tools.py      # 数据分析工具（含图表生成）
├── data/
│   ├── sales_data.csv         # 商品销售数据
│   └── generate_sample_data.py # 示例数据生成脚本
├── out/                       # 输出目录（自动创建）
│   ├── analysis_report.md     # 分析报告
│   └── figures/               # 图表文件
├── requirements.txt
└── .env.example
```

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置 API 密钥

```bash
cp .env.example .env
# 编辑 .env，填入硅基流动 API Key
# SILICONFLOW_KEY=your_key_here
```

### 生成示例数据

```bash
cd data
python generate_sample_data.py
```

### 运行分析

```bash
python main.py
```

输出路径：
- 报告：`out/analysis_report.md`
- 图表：`out/figures/`

## 🎯 项目亮点

- **企业级框架**：基于 LangGraph 构建 ReAct 循环，使用 StateGraph + 条件边管理推理状态，相比手写循环更稳定可维护
- **工具注册机制**：自定义 ToolRegistry，通过装饰器注册工具，Agent 动态选择并调用，解耦分析逻辑与推理逻辑
- **自适应分析**：工具自动识别数据列类型（日期/品类/地区等），适配不同数据集结构，无需硬编码列名

## 👤 作者

- GitHub: [@Luluvya](https://github.com/Luluvya)
- Email: danlanz11@163.com
