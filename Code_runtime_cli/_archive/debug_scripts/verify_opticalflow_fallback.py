paths = [
    "/mosheng_project/01_camera_motion_mask/level_camera_clean",
    "/mosheng_project/01_camera_motion_mask/mono_camera_for_framediff",
    "/mosheng_project/01_camera_motion_mask/feedback_prev_frame",
    "/mosheng_project/01_camera_motion_mask/composite_frame_difference",
    "/mosheng_project/01_camera_motion_mask/level_motion_gain",
    "/mosheng_project/01_camera_motion_mask/threshold_motion",
    "/mosheng_project/01_camera_motion_mask/blur_mask_soft_edge",
    "/mosheng_project/01_camera_motion_mask/OUT_motion_mask_raw",
    "/mosheng_project/03_ink_reveal_composite/OUT_final_projection",
]

for path in paths:
    node = op(path)
    if node is None:
        raise Exception("Missing node: " + path)
    try:
        node.cook(force=True)
    except Exception as e:
        print("WARN: cook issue", path, repr(e))
    print("OK node", path, "type=", node.type, "cook=", getattr(node, "cookCount", "n/a"))

level_gain = op("/mosheng_project/01_camera_motion_mask/level_motion_gain")
srcs = []
try:
    for conn in level_gain.inputConnectors[0].connections:
        srcs.append(conn.owner.path)
except Exception:
    pass
print("level_motion_gain input sources:", srcs)
if "/mosheng_project/01_camera_motion_mask/composite_frame_difference" not in srcs:
    raise Exception("level_motion_gain is not connected to composite_frame_difference")

optical = op("/mosheng_project/01_camera_motion_mask/opticalflow_motion")
if optical is not None:
    print("opticalflow_motion bypass =", getattr(optical, "bypass", None))

print("VERIFY_OK")
