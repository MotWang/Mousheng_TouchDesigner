# 代码说明 · td/ 目录

## 概述

`td/` 目录包含所有 TouchDesigner Python 脚本，用于工程构建、效果优化和工具开发。

---

## 核心脚本

### 构建类（Build）

| 脚本 | 用途 |
|------|------|
| `build_mosheng_pipeline.py` | 主管道构建脚本，生成完整的工程结构 |
| `build_season_payoff.py` | 四季绽放效果构建 |
| `build_motion_petals.py` | 运动花瓣效果构建 |
| `build_ripple.py` | 涟漪效果构建 |

### 升级类（Upgrade）

美学升级系列脚本，按顺序执行：

| 脚本 | 用途 |
|------|------|
| `upgrade_00_run_all.py` | 一键执行所有升级 |
| `upgrade_01_true_mono_base.py` | 真正的黑白基底升级 |
| `upgrade_02_ink_reveal_rebuild.py` | 水墨显色重建 |
| `upgrade_03_water_highlight.py` | 湿墨边缘高光 |
| `upgrade_04_paper_frame_grade.py` | 宣纸画框与调色 |

### 优化类（Refine / Optimize）

| 脚本 | 用途 |
|------|------|
| `refine_ink.py` | 水墨效果优化 |
| `refine_payoff_classical.py` | 经典绽放效果优化 |
| `optimize_smooth_season_cycle.py` | 四季循环平滑优化 |
| `enhance_vivid_interactive.py` | 生动交互效果增强 |
| `update_petals_ink.py` | 花瓣水墨效果更新 |

### 工具类（Utils）

| 脚本 | 用途 |
|------|------|
| `td_cli_handler.py` | TD CLI 命令行处理器 |
| `heartbeat.py` | 心跳检测 |
| `webserver_callbacks.py` | Web 服务器回调 |
| `ui_audio_reactive.py` | 音频反应 UI |
| `validate_aesthetic_upgrade.py` | 美学升级验证 |

---

## 使用方式

### 在 TouchDesigner 中运行

1. 打开 TD 工程
2. 在 Text DAT 中粘贴脚本
3. 右键 → Run Script

### 通过 td-cli 运行

```bash
# 运行构建脚本
td-cli run build_mosheng_pipeline.py

# 运行升级
td-cli run upgrade_00_run_all.py
```

---

## 归档脚本

`_archive/debug_scripts/` 目录中保存了开发过程中的调试、测试、探测脚本，仅供历史参考。

---

*© 2026 《墨·生》项目组*
