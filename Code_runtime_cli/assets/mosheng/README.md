# 《墨·生》素材目录

把正式素材按以下路径放入，文件名保持不变，TouchDesigner 工程会自动读取。

## 目录结构

```text
assets/mosheng/
  images/
    mono/
      spring_mono.png
      summer_mono.png
      autumn_mono.png
      winter_mono.png
    color/
      spring_color.png
      summer_color.png
      autumn_color.png
      winter_color.png
  audio/
    bgm/
      bgm_spring.mp3
      bgm_summer.mp3
      bgm_autumn.mp3
      bgm_winter.mp3
    fx/
      fx_water_01.wav
      fx_paper_01.wav
      fx_ink_heavy.wav
```

## 黑白上层

- `images/mono/spring_mono.png`
- `images/mono/summer_mono.png`
- `images/mono/autumn_mono.png`
- `images/mono/winter_mono.png`

## 彩色底层

- `images/color/spring_color.png`
- `images/color/summer_color.png`
- `images/color/autumn_color.png`
- `images/color/winter_color.png`

## 音频

- `audio/bgm/bgm_spring.mp3`
- `audio/fx/fx_water_01.wav`
- `audio/fx/fx_ink_heavy.wav`

要求：黑白和彩色必须同分辨率、同构图、同画布比例。建议统一 `1920x1080` 或 `1280x720`。

## 当前状态

正式国风图片和音频素材尚未放入时，TD 工程会使用 fallback 色块占位。预览偏纯色是正常状态。素材到位后，在 TD 中进入 `/mosheng_project/02_visual_assets`，把 `switch_mono_season` 和 `switch_color_season` 的 Index 调为同一个季节编号即可切换：

- `0`：fallback 占位
- `1`：spring
- `2`：summer
- `3`：autumn
- `4`：winter
