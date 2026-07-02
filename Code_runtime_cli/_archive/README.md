# 归档说明 · _archive

## 概述

本目录保存项目开发过程中的历史版本、调试脚本和中间产物，仅供历史参考。

**注意：** 归档中的文件不保证可用，仅用于追溯开发历史。

---

## 目录结构

```
_archive/
├── toe_versions/          # 历史版本TD工程
│   ├── mosheng_pipeline.toe
│   ├── mosheng_pipeline_*.toe
│   └── crash_backup_*/   # 崩溃备份
│
├── debug_scripts/        # 调试脚本
│   ├── debug_*.py
│   ├── inspect_*.py
│   ├── probe_*.py
│   ├── test_*.py
│   ├── verify_*.py
│   ├── fix_*.py
│   └── ...
│
└── output_snapshots/     # 输出快照（待填充）
```

---

## 主要历史版本

| 版本 | 日期 | 说明 |
|------|------|------|
| aesthetic_test_20260615.12 | 2026-06-16 | 最终版（已移至根目录 mosheng_final.toe） |
| unified_16x9_final | 2026-06-15 | 统一16:9比例版本 |
| scroll_reveal_final | 2026-06-15 | 卷轴展开版本 |
| motion_performance_final | 2026-06-15 | 动效性能优化版 |
| elegant_chinese_final | 2026-06-14 | 国风美学版 |
| cinematic_hand_final | 2026-06-14 | 电影级手部交互版 |
| gesture_visual_v2 | 2026-06-14 | 手势可视化v2 |
| audio_integrated | 2026-06-11 | 音频集成版 |
| complete_stable | 2026-06-09 | 完整稳定版 |
| before_seasons | 2026-06-09 | 四季功能前版本 |

---

## 恢复历史版本

如需恢复某个历史版本：
1. 从 `toe_versions/` 复制对应的 .toe 文件到 Code/ 根目录
2. 用 TouchDesigner 打开
3. **注意：** 历史版本可能不兼容当前素材路径

---

*© 2026 《墨·生》项目组*
