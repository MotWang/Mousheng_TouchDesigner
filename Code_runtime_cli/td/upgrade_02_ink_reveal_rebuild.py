"""Safe L1 tuning: preserve the verified permanent-color reveal pipeline."""

INK = "/mosheng_project/03_ink_reveal_composite"
W, H = 1280, 720


def require(parent, names):
    missing = [name for name in names if parent.op(name) is None]
    if missing:
        raise Exception("upgrade_02 missing stable nodes: " + ", ".join(missing))


def setpar(node, name, value):
    par = getattr(node.par, name, None)
    if par is not None:
        par.val = value


def fullres(node):
    setpar(node, "outputresolution", "custom")
    setpar(node, "resolutionw", W)
    setpar(node, "resolutionh", H)
    setpar(node, "fillmode", "outside")


def connect(dst, index, src):
    try:
        dst.inputConnectors[index].disconnect()
    except Exception:
        pass
    dst.inputConnectors[index].connect(src)


ink = op(INK)
if ink is None:
    raise Exception("upgrade_02 missing " + INK)

required = (
    "glsl_scroll_reveal_mix", "screen_reveal_with_immediate_brush",
    "level_immediate_motion_brush", "composite_accumulate_mask",
    "level_decay_092_096", "blur_ink_bleed", "level_shape_reveal_mask",
    "OUT_ink_mask_final", "OUT_final_projection",
)
require(ink, required)

# Permanent memory until the season controller explicitly resets feedback.
accumulate = ink.op("composite_accumulate_mask")
decay = ink.op("level_decay_092_096")
setpar(accumulate, "operand", "maximum")
setpar(decay, "opacity", 1.0)
setpar(decay, "brightness1", 1.0)
setpar(decay, "gamma1", 1.0)
setpar(ink.op("blur_ink_bleed"), "size", 14)

# Immediate strokes remain responsive, while the shaped accumulated mask keeps
# a restrained organic edge without a decaying gray overlay.
brush = ink.op("level_immediate_motion_brush")
setpar(brush, "inlow", 0.004)
setpar(brush, "inhigh", 0.20)
setpar(brush, "gamma1", 0.48)
setpar(brush, "brightness1", 1.5)
shape = ink.op("level_shape_reveal_mask")
setpar(shape, "inlow", 0.003)
setpar(shape, "inhigh", 0.34)
setpar(shape, "gamma1", 0.62)
setpar(shape, "clamp", True)

for name in (
    "screen_reveal_with_immediate_brush", "level_shape_reveal_mask",
    "glsl_scroll_reveal_mix", "OUT_final_projection",
):
    fullres(ink.op(name))

# Keep feedback at its efficient internal size, but expose a consistent
# 1280x720 public mask for downstream aesthetics and external inspection.
mask_out = ink.op("OUT_ink_mask_final")
mask_res = ink.op("ink_mask_public_1280") or ink.create("resolutionTOP", "ink_mask_public_1280")
mask_res.nodeX, mask_res.nodeY = mask_out.nodeX - 180, mask_out.nodeY
source = mask_out.inputs[0]
if source == mask_res and mask_res.inputs:
    source = mask_res.inputs[0]
if source is None:
    raise Exception("upgrade_02 public ink mask has no source")
fullres(mask_res)
connect(mask_res, 0, source)
connect(mask_out, 0, mask_res)

mix = ink.op("glsl_scroll_reveal_mix")
if len(mix.inputs) < 3:
    raise Exception("upgrade_02 reveal shader must keep mono/color/mask inputs")
if mix.inputs[2] != ink.op("screen_reveal_with_immediate_brush"):
    raise Exception("upgrade_02 refused: reveal shader mask is not the verified immediate+memory mask")

# Existing ink-edge embellishments are kept subtle; no Matte TOP is created.
if ink.op("blur_reveal_gold_dust"):
    setpar(ink.op("blur_reveal_gold_dust"), "size", 7)
if ink.op("level_elegant_paper_finish"):
    setpar(ink.op("level_elegant_paper_finish"), "gamma1", 0.98)

# Ignore the camera's invalid first-frame difference after a cold project load.
# This guarantees a short sealed monochrome introduction before interaction.
controller = op("/mosheng_project/00_control_panel/automation_heartbeat_controller")
if controller is None:
    raise Exception("upgrade_02 requires automation_heartbeat_controller")
marker = "# AESTHETIC_COLD_START_GUARD"
if marker not in controller.text:
    needle = "    motion = _ink_sound(now, parent_comp)\n\n    if state == 'opening':"
    guard = """    motion = _ink_sound(now, parent_comp)

    # AESTHETIC_COLD_START_GUARD
    # The first camera frame differs from an empty previous frame and can look
    # like full-screen motion. Keep the scroll sealed while that frame settles.
    if absTime.seconds < 4.0:
        transition_mask.par.cross = 0
        dim.par.value0 = 1
        _reset_feedback()
        parent_comp.store('auto_state', 'sealed')
        parent_comp.store('state_started', now)
        parent_comp.store('auto_last_motion', now)
        _set_audio_mix(current)
        return

    if state == 'opening':"""
    if needle not in controller.text:
        raise Exception("upgrade_02 could not safely insert cold-start guard")
    controller.text = controller.text.replace(needle, guard)
brush_marker = "# AESTHETIC_COLD_START_BRUSH_GUARD"
if brush_marker not in controller.text:
    controller.text = controller.text.replace(
        "    if absTime.seconds < 4.0:\n",
        "    brush_guard = _node('../03_ink_reveal_composite/level_immediate_motion_brush')\n"
        "    # AESTHETIC_COLD_START_BRUSH_GUARD\n"
        "    if absTime.seconds < 4.0:\n"
        "        if brush_guard:\n"
        "            brush_guard.par.brightness1 = 0\n",
        1,
    )
    controller.text = controller.text.replace(
        "        return\n\n    if state == 'opening':",
        "        return\n\n"
        "    if brush_guard:\n"
        "        brush_guard.par.brightness1 = 1.5\n\n"
        "    if state == 'opening':",
        1,
    )
controller.text = controller.text.replace(
    "if absTime.seconds < 4.0:",
    "if now < parent_comp.fetch('startup_guard_until', 0.0):",
)
shape_marker = "# AESTHETIC_COLD_START_SHAPE_GUARD"
if shape_marker not in controller.text:
    controller.text = controller.text.replace(
        "    # AESTHETIC_COLD_START_BRUSH_GUARD\n",
        "    shape_guard = _node('../03_ink_reveal_composite/level_shape_reveal_mask')\n"
        "    # AESTHETIC_COLD_START_BRUSH_GUARD\n"
        "    # AESTHETIC_COLD_START_SHAPE_GUARD\n",
        1,
    )
    controller.text = controller.text.replace(
        "            brush_guard.par.brightness1 = 0\n",
        "            brush_guard.par.brightness1 = 0\n"
        "        if shape_guard:\n"
        "            shape_guard.par.brightness1 = 0\n",
        1,
    )
    controller.text = controller.text.replace(
        "        brush_guard.par.brightness1 = 1.5\n",
        "        brush_guard.par.brightness1 = 1.5\n"
        "    if shape_guard:\n"
        "        shape_guard.par.brightness1 = 1.0\n",
        1,
    )

# A project-start callback creates a real wall-clock guard every time the .toe
# is opened. Stored component values alone cannot do this because they persist
# inside the saved project.
controls = op("/mosheng_project/00_control_panel")
startup = controls.op("aesthetic_startup_reset") or controls.create("executeDAT", "aesthetic_startup_reset")
startup.par.start = True
startup.text = """import time

def onStart():
    controls = parent()
    controls.store('startup_guard_until', time.time() + 4.0)
    controls.store('auto_state', 'sealed')
    controls.store('auto_current_season', 1)
    controls.store('state_started', time.time())
    controls.store('auto_last_motion', time.time())
    op('../02_visual_assets/switch_mono_season').par.index = 1
    op('../02_visual_assets/switch_color_season').par.index = 1
    op('../03_ink_reveal_composite/season_transition_mask').par.cross = 0
    op('../03_ink_reveal_composite/level_immediate_motion_brush').par.brightness1 = 0
    op('../03_ink_reveal_composite/level_shape_reveal_mask').par.brightness1 = 0
    op('../03_ink_reveal_composite/feedback_ink_memory').par.resetpulse.pulse()
    controls.op('idle_dim_target').par.value0 = 1
    return

def onCreate():
    return

def onExit():
    return

def onFrameStart(frame):
    return

def onFrameEnd(frame):
    return

def onPlayStateChange(state):
    return

def onDeviceChange():
    return

def onProjectPreSave():
    return

def onProjectPostSave():
    return
"""

note = ink.op("README_aesthetic_safe_l1") or ink.create("textDAT", "README_aesthetic_safe_l1")
note.text = (
    "Safe L1: verified GLSL formula and current feedback nodes retained.\n"
    "Maximum accumulation + decay 1.0 means color persists until season reset.\n"
    "No Matte TOP and no fading gray feedback overlay are introduced.\n"
    "A 4-second cold-start guard rejects the camera's invalid first frame."
)
print("UPGRADE_02_OK permanent reveal preserved; no destructive rebuild")
