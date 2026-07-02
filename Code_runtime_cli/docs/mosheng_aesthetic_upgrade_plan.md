# 《墨·生》美学升级安全实施说明

## 最终交互规则

- 初始画面为完全黑白，黑白由同一张彩色图实时去色生成，因此像素严格对齐。
- 每次 Motion 立即显色；显色区域通过 `Maximum` 累积，停止动作后不会退回黑白。
- 覆盖达到阈值后，画卷展开并渐变进入下一季；换季完成时才清空显色记忆。
- 核心输出与美学输出均为 `1280×720`，Fill Outside，不增加黑边或硬卷轴框。

## 安全边界

升级脚本不会删除或替换当前稳定核心：

- `glsl_scroll_reveal_mix`：明确执行 `黑白 × (1-mask) + 彩色 × mask`。
- `screen_reveal_with_immediate_brush`：保证动作立即显色。
- `composite_accumulate_mask`：保持 `Maximum` 永久累积。
- `level_decay_092_096`：保持 `opacity=1.0`，仅在换季时由状态机重置。
- `/mosheng_project/03_ink_reveal_composite/OUT_final_projection`：继续保留为核心输出。

禁止重新引入双输入 Matte TOP、会消退的灰雾反馈、内容缩放、黑边或默认呼吸位移。

## 四阶段职责

1. `upgrade_01_true_mono_base.py`
   - 保留现有“彩色图实时生成黑白图”的对齐逻辑。
   - 轻调水墨黑阶，并给彩色层做克制增艳。

2. `upgrade_02_ink_reveal_rebuild.py`
   - 名称保留，但实际只做安全调优，不重建、不删除节点。
   - 强制 `Maximum + decay 1.0`，保持即时笔触和永久显色。
   - 添加 4 秒冷启动保护，过滤摄像头首帧差，确保打开工程先呈现纯黑白画卷。

3. `optimize_smooth_season_cycle.py`
   - 当前季先用 `smootherstep` 缓动完成显色。
   - 换季使用三拍结构：`当前季彩色 → 当前季黑白 → 下一季黑白`。
   - 彩色退场与黑白换季共持续 10 秒，避免两幅重彩画面直接叠加产生双影。
   - 转场期间暂时屏蔽 Motion；换季完成后恢复 Motion，让下一季从黑白重新被唤醒。
   - BGM 与环境声使用同一缓动曲线渐变。

4. `upgrade_03_water_highlight.py`
   - 新增可选湿墨边缘高光，内部 `480×270`，最终回到 `1280×720`。
   - `Waterenable` 默认关闭，普通笔记本默认无额外水光负载。

5. `upgrade_04_paper_frame_grade.py`
   - 添加低强度程序化宣纸肌理、轻暗角和低强度 Bloom。
   - 不裁切、不缩放、不加黑边、不添加呼吸位移。
   - 创建 `/mosheng_project/07_grade_and_frame/OUT_final_projection_graded`，并自动将 `projection_panel` 指向它。

## 独立测试执行

只在以下副本执行：

`Code/mosheng_pipeline_aesthetic_test_20260615.toe`

逐阶段命令：

```bash
td-cli --port 9500 exec -f Code/td/upgrade_01_true_mono_base.py
td-cli --port 9500 exec -f Code/td/upgrade_02_ink_reveal_rebuild.py
td-cli --port 9500 exec -f Code/td/optimize_smooth_season_cycle.py
td-cli --port 9500 exec -f Code/td/upgrade_03_water_highlight.py
td-cli --port 9500 exec -f Code/td/upgrade_04_paper_frame_grade.py
```

全部阶段已经逐项验收后，才可运行：

```bash
td-cli --port 9500 exec -f Code/td/upgrade_00_run_all.py
```

`upgrade_00` 会在每阶段检查依赖、错误数量和输出尺寸；任一阶段失败立即停止。脚本不会调用 `project.save()`，也不会覆盖正式工程。

## 验收标准

- 每阶段 `BAD_COUNT 0`。
- Mask `0` 等于黑白画面；Mask `1` 等于彩色画面。
- 每次动作立即出现彩色墨迹，停止后颜色保留。
- 仅换季完成时清空为下一季黑白。
- 黑白、彩色、Motion、核心输出、美学输出均为 `1280×720`。
- `Waterenable=0` 时保持当前性能水平；开启后持续运行不低于 30 FPS。
- HDMI 全屏展示 `/mosheng_project/07_grade_and_frame/OUT_final_projection_graded`。
