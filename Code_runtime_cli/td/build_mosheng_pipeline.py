PROJECT_DIR = "/Users/moriaty/Documents/Codex/2026-05-20/0dot77-td-cli-https-github-com"
ASSET_DIR = PROJECT_DIR + "/assets/mosheng"


def destroy_if_exists(parent_op, name):
    node = parent_op.op(name)
    if node is not None:
        node.destroy()


def create(parent_op, type_name, name, x=0, y=0):
    destroy_if_exists(parent_op, name)
    node = parent_op.create(type_name, name)
    node.nodeX = x
    node.nodeY = y
    return node


def setpar(node, names, value):
    for name in names:
        par = getattr(node.par, name, None)
        if par is None:
            continue
        try:
            par.val = value
            return True
        except Exception:
            try:
                par.expr = str(value)
                return True
            except Exception:
                pass
    return False


def connect(dst, index, src):
    try:
        dst.inputConnectors[index].connect(src)
        return True
    except Exception:
        return False


def add_note(parent_op, name, text, x, y):
    dat = create(parent_op, "textDAT", name, x, y)
    dat.text = text
    return dat


def safe_color(top, rgba):
    r, g, b, a = rgba
    setpar(top, ("colorr", "r"), r)
    setpar(top, ("colorg", "g"), g)
    setpar(top, ("colorb", "b"), b)
    setpar(top, ("alpha", "a"), a)
    setpar(top, ("outputresolution",), "custom")
    setpar(top, ("resolutionw", "resx", "w"), 1280)
    setpar(top, ("resolutionh", "resy", "h"), 720)


root = op("/")

# Remove old work container only; keep TDCliServer/local/perform intact.
old = root.op("mosheng_project")
if old is not None:
    old.destroy()

mosheng = root.create("baseCOMP", "mosheng_project")
mosheng.nodeX = -700
mosheng.nodeY = 350

cam = create(mosheng, "baseCOMP", "01_camera_motion_mask", -1200, 500)
assets = create(mosheng, "baseCOMP", "02_visual_assets", -1200, 80)
ink = create(mosheng, "baseCOMP", "03_ink_reveal_composite", -1200, -340)
audio = create(mosheng, "baseCOMP", "04_audio_reactivity", 100, 500)
ai = create(mosheng, "baseCOMP", "05_ai_generation_bridge", 100, 80)
control = create(mosheng, "baseCOMP", "00_control_panel", 100, -340)

# ---------------------------------------------------------------------------
# 01 Camera motion mask
# ---------------------------------------------------------------------------
vdev = create(cam, "videodeviceinTOP", "camera_640x480", -1000, 100)
level_cam = create(cam, "levelTOP", "level_camera_clean", -780, 100)
flow = create(cam, "opticalflowTOP", "opticalflow_motion", -560, 100)
level_flow = create(cam, "levelTOP", "level_motion_gain", -340, 100)
thresh = create(cam, "thresholdTOP", "threshold_motion", -120, 100)
blur_mask = create(cam, "blurTOP", "blur_mask_soft_edge", 100, 100)
null_mask_raw = create(cam, "nullTOP", "OUT_motion_mask_raw", 320, 100)

connect(level_cam, 0, vdev)
connect(flow, 0, level_cam)
connect(level_flow, 0, flow)
connect(thresh, 0, level_flow)
connect(blur_mask, 0, thresh)
connect(null_mask_raw, 0, blur_mask)

setpar(vdev, ("resmenu", "resolution"), "640x480")
setpar(vdev, ("resx", "w"), 640)
setpar(vdev, ("resy", "h"), 480)
setpar(level_cam, ("blacklevel", "black"), 0.02)
setpar(level_cam, ("brightness", "bright"), 1.0)
setpar(level_flow, ("multiply", "mult"), 5.0)
setpar(thresh, ("threshold",), 0.09)
setpar(blur_mask, ("sizex", "size"), 18)
setpar(blur_mask, ("sizey",), 18)

add_note(
    cam,
    "README_camera",
    "Camera chain: Video Device In -> Level -> Optical Flow -> Level gain -> Threshold -> Blur -> OUT_motion_mask_raw.\n"
    "Set camera resolution to 640x480. Raise threshold in bright/noisy environments; lower it if gestures are missed.",
    -1000,
    -120,
)

# ---------------------------------------------------------------------------
# 02 Visual assets
# ---------------------------------------------------------------------------
mono_fallback = create(assets, "constantTOP", "fallback_mono_xuanpaper", -1100, 210)
color_fallback = create(assets, "constantTOP", "fallback_color_gold_ink", -1100, -80)
safe_color(mono_fallback, (0.82, 0.80, 0.75, 1.0))
safe_color(color_fallback, (0.95, 0.28, 0.12, 1.0))

mono_switch = create(assets, "switchTOP", "switch_mono_season", -250, 210)
color_switch = create(assets, "switchTOP", "switch_color_season", -250, -80)
null_mono = create(assets, "nullTOP", "OUT_mono_top_layer", 0, 210)
null_color = create(assets, "nullTOP", "OUT_color_bottom_layer", 0, -80)
connect(mono_switch, 0, mono_fallback)
connect(color_switch, 0, color_fallback)

seasons = ["spring", "summer", "autumn", "winter"]
for i, season in enumerate(seasons):
    mono = create(assets, "moviefileinTOP", "mono_" + season, -840 + i * 150, 210)
    color = create(assets, "moviefileinTOP", "color_" + season, -840 + i * 150, -80)
    setpar(mono, ("file", "moviefile"), ASSET_DIR + "/images/mono/" + season + "_mono.png")
    setpar(color, ("file", "moviefile"), ASSET_DIR + "/images/color/" + season + "_color.png")
    connect(mono_switch, i + 1, mono)
    connect(color_switch, i + 1, color)

connect(null_mono, 0, mono_switch)
connect(null_color, 0, color_switch)
setpar(mono_switch, ("index",), 0)
setpar(color_switch, ("index",), 0)

add_note(
    assets,
    "README_assets",
    "Put aligned image pairs here:\n"
    "assets/mosheng/images/mono/spring_mono.png ... winter_mono.png\n"
    "assets/mosheng/images/color/spring_color.png ... winter_color.png\n"
    "Both layers must be same resolution and composition. Use switch_mono_season and switch_color_season Index 1-4 to select seasons.",
    -1100,
    -300,
)

# ---------------------------------------------------------------------------
# 03 Ink reveal composite
# ---------------------------------------------------------------------------
mask_in = create(ink, "selectTOP", "IN_motion_mask_from_camera", -1100, 160)
mono_in = create(ink, "selectTOP", "IN_mono_layer", -1100, -60)
color_in = create(ink, "selectTOP", "IN_color_layer", -1100, -280)
feedback = create(ink, "feedbackTOP", "feedback_ink_memory", -860, 240)
decay = create(ink, "levelTOP", "level_decay_092_096", -650, 240)
blur_ink = create(ink, "blurTOP", "blur_ink_bleed", -440, 240)
accumulate = create(ink, "compositeTOP", "composite_accumulate_mask", -220, 160)
mask_final = create(ink, "nullTOP", "OUT_ink_mask_final", 10, 160)
matte_color = create(ink, "matteTOP", "matte_color_by_ink_mask", -220, -120)
over_final = create(ink, "overTOP", "over_color_on_mono", 10, -120)
final_out = create(ink, "nullTOP", "OUT_final_projection", 240, -120)

setpar(mask_in, ("top",), "../01_camera_motion_mask/OUT_motion_mask_raw")
setpar(mono_in, ("top",), "../02_visual_assets/OUT_mono_top_layer")
setpar(color_in, ("top",), "../02_visual_assets/OUT_color_bottom_layer")

connect(feedback, 0, mask_in)
connect(decay, 0, feedback)
connect(blur_ink, 0, decay)
connect(accumulate, 0, mask_in)
connect(accumulate, 1, blur_ink)
connect(mask_final, 0, accumulate)
connect(matte_color, 0, color_in)
connect(matte_color, 1, mask_final)
connect(over_final, 0, matte_color)
connect(over_final, 1, mono_in)
connect(final_out, 0, over_final)

setpar(feedback, ("top", "targettop", "target"), mask_in.path)
setpar(decay, ("opacity", "multiply", "mult"), 0.94)
setpar(blur_ink, ("sizex", "size"), 28)
setpar(blur_ink, ("sizey",), 28)
setpar(accumulate, ("operand", "operation"), "over")
setpar(matte_color, ("mattechannel",), "luminance")

add_note(
    ink,
    "README_ink",
    "Ink reveal: raw motion mask feeds both the current reveal and Feedback memory; Level decay + Blur create lingering ink bleed without targeting a node that depends on feedback.\n"
    "Final composite uses Matte TOP to give the color layer an alpha from the mask, then Over TOP places it over the monochrome layer. Tune level_decay_092_096 opacity/multiply between 0.92 and 0.96.",
    -1100,
    -520,
)

# ---------------------------------------------------------------------------
# 04 Audio reactivity
# ---------------------------------------------------------------------------
bgm = create(audio, "audiofileinCHOP", "bgm_loop", -1000, 140)
fx_light = create(audio, "audiofileinCHOP", "fx_water_light", -1000, -20)
fx_heavy = create(audio, "audiofileinCHOP", "fx_ink_heavy", -1000, -180)
mask_select = create(audio, "selectTOP", "IN_motion_mask_for_strength", -1000, -360)
analyze = create(audio, "analyzeCHOP", "analyze_motion_strength", -750, -360)
math_light = create(audio, "mathCHOP", "motion_to_light_fx_volume", -520, -260)
math_heavy = create(audio, "mathCHOP", "motion_to_heavy_fx_volume", -520, -420)
out_strength = create(audio, "nullCHOP", "OUT_motion_strength", -280, -360)

setpar(bgm, ("file", "audiofile"), ASSET_DIR + "/audio/bgm/bgm_spring.mp3")
setpar(fx_light, ("file", "audiofile"), ASSET_DIR + "/audio/fx/fx_water_01.wav")
setpar(fx_heavy, ("file", "audiofile"), ASSET_DIR + "/audio/fx/fx_ink_heavy.wav")
setpar(mask_select, ("top",), "../03_ink_reveal_composite/OUT_ink_mask_final")
connect(analyze, 0, mask_select)
connect(math_light, 0, analyze)
connect(math_heavy, 0, analyze)
connect(out_strength, 0, analyze)
setpar(analyze, ("function",), "average")
setpar(math_light, ("fromrange1",), 0.03)
setpar(math_light, ("fromrange2",), 0.25)
setpar(math_light, ("torange1",), 0)
setpar(math_light, ("torange2",), 0.55)
setpar(math_heavy, ("fromrange1",), 0.22)
setpar(math_heavy, ("fromrange2",), 0.8)
setpar(math_heavy, ("torange1",), 0)
setpar(math_heavy, ("torange2",), 1)

add_note(
    audio,
    "README_audio",
    "Audio placeholders: put bgm_spring.mp3 and fx wav files under assets/mosheng/audio.\n"
    "OUT_motion_strength is the control signal. Route math_light/math_heavy to Audio Device Out or sampler trigger logic during sound integration.",
    -1000,
    -560,
)

# ---------------------------------------------------------------------------
# 05 AI generation bridge
# ---------------------------------------------------------------------------
web_gemini = create(ai, "webclientDAT", "webclient_gemini_placeholder", -940, 120)
web_pixverse = create(ai, "webclientDAT", "webclient_pixverse_placeholder", -940, -80)
prompt = create(ai, "textDAT", "prompt_template_mosheng", -650, 120)
params = create(ai, "tableDAT", "interaction_params_to_ai", -650, -110)
ai_note = create(ai, "textDAT", "README_ai_bridge", -320, 120)

prompt.text = (
    "Project: 墨·生\n"
    "Generate one aligned Chinese ink artwork pair. Composition must match reference.\n"
    "Mono version: ink wash painting, monochrome, xuan paper, minimal, no color.\n"
    "Color version: vibrant Chinese gongbi color, rich pigment, gold accents.\n"
    "Season: {season}. Interaction emphasis: {element_weights}. Keep slow poetic motion potential."
)
params.clear()
params.appendRow(["key", "value", "source"])
params.appendRow(["season", "spring", "manual / timer"])
params.appendRow(["motion_strength_15s", "0.0", "../04_audio_reactivity/OUT_motion_strength"])
params.appendRow(["element_weights", "water:0.4, flower:0.3, figure:0.3", "future tracking"])
ai_note.text = (
    "API bridge placeholder. Keep realtime show on fallback assets first.\n"
    "When Gemini/Pixverse keys are ready, configure webclient_gemini_placeholder and webclient_pixverse_placeholder.\n"
    "Recommended logic: no interaction for 30s -> request next season image; interaction paths over 15s -> update element weights -> generate detail variation -> fade via ink mask."
)

# ---------------------------------------------------------------------------
# 00 Control panel
# ---------------------------------------------------------------------------
ctrl_table = create(control, "tableDAT", "control_values", -900, 100)
ctrl_table.clear()
ctrl_table.appendRow(["control", "value", "notes"])
ctrl_table.appendRow(["camera_resolution", "640x480", "do not use 1080p for optical flow"])
ctrl_table.appendRow(["motion_threshold", "0.09", "increase in noisy light"])
ctrl_table.appendRow(["ink_decay", "0.94", "target range 0.92-0.96"])
ctrl_table.appendRow(["season_index", "0", "0=fallback, 1=spring, 2=summer, 3=autumn, 4=winter"])
ctrl_table.appendRow(["reset_feedback", "pulse feedback_ink_memory reset", "manual debug"])

add_note(
    control,
    "README_start_here",
    "墨·生工程入口：\n"
    "1. Open 01_camera_motion_mask and confirm camera_640x480 sees motion.\n"
    "2. Put aligned image pairs into assets/mosheng/images, then switch season Index in 02_visual_assets.\n"
    "3. Tune threshold_motion and level_decay_092_096.\n"
    "4. Use 03_ink_reveal_composite/OUT_final_projection as projector output.",
    -900,
    -140,
)

mosheng.current = True

print("Built /mosheng_project pipeline.")
print("Final projection TOP: /mosheng_project/03_ink_reveal_composite/OUT_final_projection")
print("Camera mask TOP: /mosheng_project/01_camera_motion_mask/OUT_motion_mask_raw")
print("Assets folder:", ASSET_DIR)
