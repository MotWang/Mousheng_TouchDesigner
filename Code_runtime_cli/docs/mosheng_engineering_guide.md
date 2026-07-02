# 《墨·生》TouchDesigner 工程说明文档

## 0. 交付物索引

当前项目里和《墨·生》相关的交付物集中在以下位置：

- `mosheng_pipeline.toe`：TouchDesigner 工程文件，打开后应看到 `/mosheng_project` 主工程容器。
- `docs/mosheng_engineering_guide.md`：本文档，说明工程结构、调试顺序和现场保底方案。
- `docs/mosheng_prompt_library.md`：AI 图像和微动态视频 Prompt 库。
- `assets/mosheng/README.md`：正式图片、音频素材的放置和命名规范。
- `td/build_mosheng_pipeline.py`：从空 TD 工程重建 `/mosheng_project` 的脚本。
- `td/fix_mosheng_composite.py`、`td/fix_mosheng_resolution.py`：历史修补脚本，用于单独修复合成链路和 fallback 分辨率。
- `mosheng_projection_preview.png`：当前预览图的建议导出文件名。若仓库里没有该文件，打开 TD 工程后执行截图导出即可生成。

推荐的接手顺序：

1. 打开 `mosheng_pipeline.toe`。
2. 进入 `/mosheng_project/00_control_panel` 阅读 `README_start_here`。
3. 检查 `/mosheng_project/01_camera_motion_mask/OUT_motion_mask_raw` 是否静止为黑、挥手为白。
4. 检查 `/mosheng_project/03_ink_reveal_composite/OUT_final_projection`，并把它作为投影输出。
5. 素材到位后，按 `assets/mosheng/README.md` 命名放入，再同步切换 `switch_mono_season` 和 `switch_color_season` 的 Index。

## 1. 工程目标

《墨·生》是一套“黑白水墨被观众动作唤醒为彩色画面”的互动装置。工程核心是：

双层画面叠加 + 摄像头动作捕捉 + Optical Flow 运动检测 + 动态蒙版 + Feedback 水墨晕染 + 音效联动 + AI 生成占位接口。

最终投影输出 TOP：

`/mosheng_project/03_ink_reveal_composite/OUT_final_projection`

## 2. 已搭建的 TD 通道

### 00_control_panel

入口说明和关键参数表。

- `README_start_here`：打开工程后先读这里
- `control_values`：记录摄像头分辨率、光流阈值、晕染衰减、季节索引

### 01_camera_motion_mask

动作捕捉与蒙版生成通道：

`camera_640x480 -> level_camera_clean -> opticalflow_motion -> level_motion_gain -> threshold_motion -> blur_mask_soft_edge -> OUT_motion_mask_raw`

调参重点：

- `camera_640x480`：摄像头输入，建议 640x480
- `threshold_motion`：环境越乱，阈值越高
- `blur_mask_soft_edge`：让手势边缘柔和，避免硬边

静止状态下，`OUT_motion_mask_raw` 应尽量接近黑色；挥手区域应变白。

### 02_visual_assets

黑白和彩色素材层。

- `switch_mono_season`：黑白上层切换
- `switch_color_season`：彩色底层切换
- `OUT_mono_top_layer`：黑白画输出
- `OUT_color_bottom_layer`：彩色画输出

Switch Index：

- `0`：fallback 测试色块
- `1`：spring
- `2`：summer
- `3`：autumn
- `4`：winter

### 03_ink_reveal_composite

核心显色与晕染通道：

`OUT_motion_mask_raw -> composite_accumulate_mask -> OUT_ink_mask_final`

同时，`OUT_motion_mask_raw` 也会送入：

`feedback_ink_memory -> level_decay_092_096 -> blur_ink_bleed -> composite_accumulate_mask`

也就是说：实时运动蒙版负责“当前挥手显色”，Feedback 记忆负责“上一段动作残留”。Feedback 的目标保持在独立输入上，避免把目标指向依赖 Feedback 的合成节点而造成 cook loop。

然后：

`color layer + OUT_ink_mask_final -> matte_color_by_ink_mask -> over_color_on_mono -> OUT_final_projection`

调参重点：

- `level_decay_092_096`：建议 0.92 到 0.96，越高墨痕停留越久
- `blur_ink_bleed`：越大越像宣纸晕染，但太大会糊
- `feedback_ink_memory`：需要加 Reset 按钮时，给它做 pulse 复位

### 04_audio_reactivity

音效联动占位通道：

- `bgm_loop`：背景音乐
- `fx_water_light`：轻动作音效
- `fx_ink_heavy`：重动作音效
- `OUT_motion_strength`：从蒙版分析出的运动强度
- `motion_to_light_fx_volume`：轻动作音量曲线
- `motion_to_heavy_fx_volume`：重动作音量曲线

下一步接 `Audio Device Out CHOP` 或采样触发逻辑。

### 05_ai_generation_bridge

AI API 占位通道：

- `webclient_gemini_placeholder`
- `webclient_pixverse_placeholder`
- `prompt_template_mosheng`
- `interaction_params_to_ai`

当前不直接联网生成，先保证 fallback 图库稳定。后续接 API 时使用：

- 无人交互 30 秒：生成下一季画面
- 交互后 15 秒：把运动强度、路径、触碰元素转成权重，加入 prompt
- 新画完成后：用晕染/渐变替换底层素材

## 3. 图片素材如何添加

把图片放入：

`assets/mosheng/images/mono/`

`assets/mosheng/images/color/`

文件名必须对应：

- `spring_mono.png` / `spring_color.png`
- `summer_mono.png` / `summer_color.png`
- `autumn_mono.png` / `autumn_color.png`
- `winter_mono.png` / `winter_color.png`

要求：

- 黑白和彩色是一对，同构图，同尺寸
- 建议 `1920x1080` 或 `1280x720`
- 不要一张横图一张竖图
- 不要让主体位置发生偏移
- 彩色层可以更饱和，但轮廓必须和黑白层对齐

放入后在 TD 中进入：

`/mosheng_project/02_visual_assets`

把 `switch_mono_season` 和 `switch_color_season` 的 Index 调成同一个季节编号。

如果目录不存在，按下面结构新建：

`assets/mosheng/images/mono/`

`assets/mosheng/images/color/`

`assets/mosheng/audio/bgm/`

`assets/mosheng/audio/fx/`

## 4. 图片素材如何制作

推荐流程：

1. 先用 Gemini / MJ / Imagen 生成彩色主图。
2. 固定 seed 或用 reference image 生成黑白版本。
3. 在 Photoshop / Photopea 中把两张图叠在一起检查边缘。
4. 强制裁切到相同画布尺寸。
5. 输出 PNG。

黑白 Prompt：

`主 Prompt + ink wash painting, monochrome, no color, xuan paper, minimal`

彩色 Prompt：

`主 Prompt + vibrant Chinese gongbi color, rich pigment, gold accents`

微动态视频：

用彩色静态图作为首帧，再用同图轻微位移版作为尾帧。Seedance / 可灵 / Runway 指令必须强调：

`极轻微动态，缓慢循环，无镜头移动`

## 5. 音频素材如何添加

放入：

`assets/mosheng/audio/bgm/bgm_spring.mp3`

`assets/mosheng/audio/fx/fx_water_01.wav`

`assets/mosheng/audio/fx/fx_ink_heavy.wav`

命名规范：

- `bgm_spring.mp3`
- `bgm_summer.mp3`
- `bgm_autumn.mp3`
- `bgm_winter.mp3`
- `fx_water_01.wav`
- `fx_paper_01.wav`
- `fx_ink_heavy.wav`

Suno Prompt 示例：

`Traditional Chinese guzheng, bamboo flute, peaceful, minimal, contemplative, no drums, looping ambient`

## 6. 现场调试顺序

1. 摄像头不要正对投影画面，避免拍到画面变化造成误触。
2. 打开 `01_camera_motion_mask`，确认静止时蒙版黑、挥手时蒙版白。
3. 调 `threshold_motion`，直到环境光不会误触。
4. 调 `level_decay_092_096`，让墨痕停留 1 到 3 秒。
5. 调 `blur_ink_bleed`，让边缘像宣纸晕开。
6. 接入正式黑白/彩色图片。
7. 接入音频。
8. 最后再接 AI API。

## 7. 当前工程逻辑速读

工程的主线是“检测动作 -> 生成蒙版 -> 用蒙版显色 -> 用残留模拟水墨晕染”。

观众站在摄像头前时，`01_camera_motion_mask` 用 Optical Flow 计算画面运动量。`threshold_motion` 把连续运动量压成黑白蒙版：黑色代表没有动作，白色代表观众正在挥动的位置。`blur_mask_soft_edge` 会软化边缘，让蒙版不像硬切图形。

`02_visual_assets` 负责提供两张对齐的画：黑白画在上层，彩色画在底层。现在没有正式国风素材，所以 `switch_mono_season` 和 `switch_color_season` 的 Index 为 `0` 时显示 fallback 色块。正式素材放好后，把两个 switch 调到同一个季节编号即可。

`03_ink_reveal_composite` 是视觉核心。当前白色蒙版直接让彩色层显现；Feedback 会保留上一段运动痕迹，再经过 `level_decay_092_096` 衰减和 `blur_ink_bleed` 模糊，形成“墨在纸上慢慢散开并消退”的感觉。最后 `matte_color_by_ink_mask` 把蒙版变成彩色层透明度，`over_color_on_mono` 把彩色显现结果叠到黑白画上。

`04_audio_reactivity` 暂时是占位逻辑：它读取最终墨迹蒙版的平均强度，输出 `OUT_motion_strength`，后续可以把这个信号接到音量、采样触发或粒子强度。`05_ai_generation_bridge` 也是占位：Prompt、交互参数表和 Gemini / Pixverse Web Client 已经留好，正式 API Key 和调用策略可以晚于现场交互稳定之后再接。

## 8. 答辩核心话术

本装置基于 TouchDesigner 搭建，利用摄像头和 Optical Flow 实时捕捉观众肢体动作。画面结构分为黑白上层和彩色底层，系统把运动轨迹转化为动态蒙版，使观众挥手区域逐渐显露底层重彩画面。通过 Feedback 与 Blur 模拟水墨在宣纸上晕开的残留质感，并将运动强度映射到水滴、纸张和泼墨音效。作品以吴冠中“动与静”的艺术观为内核：人未动，画为静；人一动，墨生色，画成境。

## 9. 保底方案

如果 Week 1 光流和 Feedback 不稳定：

1. 保留双层画面和运动蒙版。
2. 暂时关闭 Feedback，只用 Blur 后的实时蒙版。
3. AI API 改为 fallback 图库轮播。
4. 四季切换缩减为 1 到 2 套主视觉。

保底必留：

双层叠加 + 光流交互 + 显色蒙版 + 基础音效。
