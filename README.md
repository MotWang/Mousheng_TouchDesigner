# 《墨·生》—— 交互水墨投影装置

> 人未动，画为静；人一动，墨生色，画成境。
> —— 以吴冠中「动与静」为内核

---

## 项目简介

《墨·生》是一件基于 TouchDesigner 的交互式水墨投影装置作品。

观众站在画卷前，通过肢体动作与画面互动——静止时，是一幅素墨留白的山水；动作时，墨色晕染之处，重彩工笔缓缓透出。当整幅画被完全唤醒，四季便依次绽放。

这不是预设的动画，是每一位观众，在画里留下了自己的痕迹。

---

## 技术栈

- **实时渲染引擎**：TouchDesigner
- **动作捕捉**：Optical Flow 光流算法
- **视觉效果**：双层叠加 + Feedback 晕染 + Bloom 后期
- **输出规格**：1280×720 · 16:9 · 无黑边

---

## 目录结构

```
墨生/
├── Code/                    # TD工程与代码
│   ├── mosheng_final.toe    # ⭐ 最终版TD工程
│   ├── td/                  # Python脚本（核心构建工具）
│   ├── docs/                # 技术文档
│   ├── assets/              # 工程资源
│   ├── outputs/             # 输出快照
│   ├── tests/               # 测试脚本
│   └── _archive/            # 历史版本归档
│
├── 四季背景图/               # 四季主视觉素材（8张）
│   ├── spring_mono.png      # 春 · 黑白
│   ├── spring_color.png     # 春 · 彩色
│   ├── summer_mono.png      # 夏 · 黑白
│   ├── summer_color.png     # 夏 · 彩色
│   ├── autumn_mono.png      # 秋 · 黑白
│   ├── autumn_color.png     # 秋 · 彩色
│   ├── winter_mono.png      # 冬 · 黑白
│   └── winter_color.png     # 冬 · 彩色
│
├── 音效（背景音+转场）/       # 音效素材
│   ├── 02_转场音效/
│   ├── 03_环境音/
│   └── 04_交互音效/
│
├── 图片/                    # 现场布展照片
│   ├── 现场照片_01~44.jpg
│   ├── 04_现场视频/
│   └── _原始备份/
│
├── 宣传视频素材/             # 宣传视频制作素材
│   ├── 01_图片素材/
│   ├── 02_视频素材/
│   ├── 背景播放器+提词器.html
│   └── ...
│
├── 墨生_现场操作提示_A4.pdf   # 现场操作卡
├── 墨生_现场操作提示_A4.html
└── README.md                # 本文档
```

---

## 快速开始

### 打开工程

直接双击 `Code/mosheng_final.toe` 即可打开最终版工程。

### 工程通道结构

1. **00_control_panel** — 入口说明与关键参数
2. **01_camera_motion_mask** — 动作捕捉与蒙版生成
3. **02_visual_assets** — 黑白/彩色素材层（四季切换）
4. **03_ink_reveal_composite** — 核心显色与晕染
5. **04_audio_reactivity** — 音效联动
6. **05_ai_generation_bridge** — AI API 桥接
7. **06_water_highlight** — 湿墨边缘高光
8. **07_grade_and_frame** — 宣纸肌理、后期调色

### 最终输出

`/mosheng_project/07_grade_and_frame/OUT_final_projection_graded`

---

## 交互规则

- **初始状态**：完全黑白（由彩色图实时去色生成，像素严格对齐）
- **触发显色**：每次 Motion 立即显色，通过 Maximum 累积
- **显色保留**：停止动作后不会退回黑白
- **换季触发**：覆盖达到阈值后，画卷展开并渐变进入下一季
- **清空记忆**：换季完成时才清空显色记忆
- **冷启动保护**：4秒冷启动保护，确保打开工程先呈现纯黑白画卷

---

## 四季绽放效果

| 季节 | 绽放效果 |
|------|----------|
| **春** | 柳叶轻盈飘落，疏朗灵动 |
| **夏** | 荷瓣上浮，金色绽放辉光 |
| **秋** | 枫叶纷飞铺洒，金尘点点 |
| **冬** | 雪花飘落，素白渐覆画面 |

---

## Contributors

- **MotWang** — `《墨·生》` project author, TD interactive artwork design/production, and project-specific CLI optimization/integration

---

## 已上传运行代码与优化版 CLI

为保证仓库可直接下载运行，同时不破坏本地 `Code` 原始仓库历史，本项目已提供：

- `Code_runtime_cli/`：可直接查看与使用的运行代码快照（不含嵌套 `.git` 元数据）
- 该目录包含你优化后的 CLI、TouchDesigner 脚本、工程文档与相关资产

对应在线仓库：[`MotWang/Mousheng_TouchDesigner`](https://github.com/MotWang/Mousheng_TouchDesigner.git)

---

## Contribution（MotWang）

- 将 CLI 深度应用于《墨·生》交互装置生产流程，并完成工程化落地
- 增加/强化面向 Agent 的工作闭环（observe/apply/verify/history/rollback）
- 修复并增强稳定性（disconnect、ops delete、docs/timeline、verify 输出等）
- 优化 FeedbackTOP 用法与回路安全性，降低 cook-loop 风险
- 增强 ripple/ink 视觉链路（扩散、噪声扰动、显色复合、RGB 爆色抑制）
- 补全运行文档、项目资产组织与 macOS 实操说明

### Repository Attribution Note

- 本仓库中的 `Code_runtime_cli/` 为《墨·生》项目运行快照与优化集成版本
- 该目录保留并尊重原 CLI 作者署名，同时明确 Mosheng 项目侧二次开发贡献

## Acknowledgement

- Thanks **0dot77 (Taeyang Yoo)** for the original `td-cli` foundation.

---

## macOS 运行 TouchDesigner 与 CLI

### 1) 运行 TouchDesigner 工程（Mac）

- 安装并打开 TouchDesigner（macOS 版）
- 打开工程：`Code_runtime_cli/mosheng_final.toe`（若该文件存在）或你的目标 `.toe`
- 确认工程内 `TDCliServer` 已加载，默认端口为 `9500`

### 2) 运行优化后的 CLI（Mac）

- 进入目录：`Code_runtime_cli/`
- 本地构建：`go build -o td-cli ./cmd/td-cli/`
- 连接测试：`./td-cli status`

### 3) 常用验证命令

- `./td-cli instances`
- `./td-cli ops list /project1 --depth 2`
- `./td-cli screenshot /project1/<top_path> -o frame.png`

---

*© 2026 《墨·生》项目组*
