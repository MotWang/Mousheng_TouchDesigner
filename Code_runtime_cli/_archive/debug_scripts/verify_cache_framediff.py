required = [
    "/mosheng_project/01_camera_motion_mask/level_camera_clean",
    "/mosheng_project/01_camera_motion_mask/mono_camera_for_framediff",
    "/mosheng_project/01_camera_motion_mask/cache_prev_frame",
    "/mosheng_project/01_camera_motion_mask/composite_frame_difference",
    "/mosheng_project/01_camera_motion_mask/level_motion_gain",
    "/mosheng_project/01_camera_motion_mask/threshold_motion",
    "/mosheng_project/01_camera_motion_mask/blur_mask_soft_edge",
    "/mosheng_project/01_camera_motion_mask/OUT_motion_mask_raw",
    "/mosheng_project/03_ink_reveal_composite/OUT_final_projection",
]

for path in required:
    node = op(path)
    if node is None:
        raise Exception("Missing node: " + path)
    node.cook(force=True)
    print("OK node", path, "type=", node.type)

if op("/mosheng_project/01_camera_motion_mask/feedback_prev_frame") is not None:
    raise Exception("feedback_prev_frame still exists")

diff = op("/mosheng_project/01_camera_motion_mask/composite_frame_difference")
srcs = []
for i in range(min(2, len(diff.inputConnectors))):
    try:
        srcs.append([conn.owner.path for conn in diff.inputConnectors[i].connections])
    except Exception:
        srcs.append([])
print("diff input sources:", srcs)

if "/mosheng_project/01_camera_motion_mask/cache_prev_frame" not in srcs[1]:
    raise Exception("composite_frame_difference input 1 is not cache_prev_frame")

print("VERIFY_OK_CACHE_FRAMEDIFF")
