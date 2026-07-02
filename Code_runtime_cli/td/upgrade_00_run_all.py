"""Run the safe aesthetic stages with preflight and fail-fast validation."""

import os

ROOT = "/mosheng_project"
W, H = 1280, 720
BASE = os.path.join(project.folder, "td")
STEPS = (
    ("upgrade_01_true_mono_base.py", "/mosheng_project/02_visual_assets/OUT_mono_top_layer"),
    ("upgrade_02_ink_reveal_rebuild.py", "/mosheng_project/03_ink_reveal_composite/OUT_final_projection"),
    ("optimize_smooth_season_cycle.py", "/mosheng_project/03_ink_reveal_composite/OUT_final_projection"),
    ("upgrade_03_water_highlight.py", "/mosheng_project/06_water_highlight/OUT_water_composited"),
    ("upgrade_04_paper_frame_grade.py", "/mosheng_project/07_grade_and_frame/OUT_final_projection_graded"),
)


def bad_nodes():
    root = op(ROOT)
    bad = []
    for node in ([root] + root.findChildren(maxDepth=20)):
        try:
            errors = node.errors()
        except Exception:
            errors = []
        if errors:
            bad.append((node.path, list(errors)))
    return bad


def validate_output(path):
    node = op(path)
    if node is None:
        raise Exception("missing expected output " + path)
    node.cook(force=True)
    if node.width != W or node.height != H:
        raise Exception("%s is %sx%s, expected %sx%s" % (path, node.width, node.height, W, H))
    bad = bad_nodes()
    if bad:
        raise Exception("BAD_COUNT %d; first=%s %s" % (len(bad), bad[0][0], bad[0][1]))
    print("VALIDATED", path, "%sx%s" % (node.width, node.height), "BAD_COUNT 0")


required = (
    ROOT + "/02_visual_assets/level_mono_deep_ink",
    ROOT + "/03_ink_reveal_composite/glsl_scroll_reveal_mix",
    ROOT + "/03_ink_reveal_composite/screen_reveal_with_immediate_brush",
    ROOT + "/03_ink_reveal_composite/composite_accumulate_mask",
    ROOT + "/03_ink_reveal_composite/level_decay_092_096",
    ROOT + "/projection_panel",
)
missing = [path for path in required if op(path) is None]
if missing:
    raise Exception("run-all preflight failed: " + ", ".join(missing))
if not os.path.isdir(BASE):
    raise Exception("run-all script directory missing: " + BASE)

print("SAFE_AESTHETIC_RUN_ALL", BASE)
for filename, expected in STEPS:
    path = os.path.join(BASE, filename)
    if not os.path.isfile(path):
        raise Exception("missing stage file " + path)
    print("RUNNING", filename)
    with open(path, "r", encoding="utf-8") as handle:
        exec(compile(handle.read(), path, "exec"), globals())
    validate_output(expected)

print("SAFE_AESTHETIC_RUN_ALL_OK")
print("No project.save() was called. Save only the independent test copy after review.")
