"""Validation report for the safe aesthetic test project."""

import numpy as np

ROOT = "/mosheng_project"
W, H = 1280, 720
failures = []


def check(condition, message):
    if not condition:
        failures.append(message)
    print(("PASS " if condition else "FAIL ") + message)


def image(path):
    node = op(path)
    check(node is not None, "exists " + path)
    if node is None:
        return None
    node.cook(force=True)
    check((node.width, node.height) == (W, H), "%s is %sx%s" % (path, node.width, node.height))
    return node


assets = op(ROOT + "/02_visual_assets")
ink = op(ROOT + "/03_ink_reveal_composite")
water = op(ROOT + "/06_water_highlight")
grade = op(ROOT + "/07_grade_and_frame")
panel = op(ROOT + "/projection_panel")

for season in ("spring", "summer", "autumn", "winter"):
    color = image(ROOT + "/02_visual_assets/fit_%s_color_16x9" % season)
    mono = image(ROOT + "/02_visual_assets/derive_%s_mono_from_color" % season)
    if color is not None:
        arr = color.numpyArray(delayed=False)[:, :, :3]
        border = np.concatenate((arr[0], arr[-1], arr[:, 0], arr[:, -1]))
        ratio = float(np.mean(np.max(border, axis=1) < 0.01))
        check(ratio == 0.0, "%s black border ratio %.4f" % (season, ratio))

for path in (
    ROOT + "/02_visual_assets/OUT_mono_top_layer",
    ROOT + "/02_visual_assets/OUT_color_bottom_layer",
    ROOT + "/03_ink_reveal_composite/OUT_ink_mask_final",
    ROOT + "/03_ink_reveal_composite/OUT_final_projection",
    ROOT + "/06_water_highlight/OUT_water_composited",
    ROOT + "/07_grade_and_frame/OUT_final_projection_graded",
):
    image(path)

check(ink.op("composite_accumulate_mask").par.operand.eval() == "maximum", "mask accumulation is maximum")
check(abs(float(ink.op("level_decay_092_096").par.opacity.eval()) - 1.0) < 0.0001, "mask decay is 1.0")
check(ink.op("glsl_scroll_reveal_mix").inputs[2] == ink.op("screen_reveal_with_immediate_brush"),
      "reveal shader uses immediate+memory mask")
check(not bool(water.par.Waterenable.eval()), "Waterenable defaults off")
check(panel.par.top.eval() == grade.op("OUT_final_projection_graded").path,
      "projection_panel uses graded output")

bad = []
root = op(ROOT)
for node in [root] + root.findChildren(maxDepth=20):
    try:
        if node.errors():
            bad.append(node.path)
    except Exception:
        pass
check(len(bad) == 0, "BAD_COUNT %d" % len(bad))

if failures:
    raise Exception("AESTHETIC_VALIDATION_FAILED: " + "; ".join(failures))
print("AESTHETIC_VALIDATION_OK")
