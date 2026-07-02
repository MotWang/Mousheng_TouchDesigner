def create(parent, type_name, name, x, y):
    old = parent.op(name)
    if old is not None:
        old.destroy()
    node = parent.create(type_name, name)
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


def disconnect_input(node, index=0):
    try:
        node.inputConnectors[index].disconnect()
        return
    except Exception:
        pass
    try:
        for conn in list(node.inputConnectors[index].connections):
            conn.disconnect()
    except Exception:
        pass


def connect(dst, index, src):
    disconnect_input(dst, index)
    dst.inputConnectors[index].connect(src)


cam = op("/mosheng_project/01_camera_motion_mask")
if cam is None:
    raise Exception("Cannot find /mosheng_project/01_camera_motion_mask")

level_camera = cam.op("level_camera_clean")
level_gain = cam.op("level_motion_gain")
threshold = cam.op("threshold_motion")
blur = cam.op("blur_mask_soft_edge")
out_mask = cam.op("OUT_motion_mask_raw")
optical = cam.op("opticalflow_motion")

if level_camera is None:
    raise Exception("Missing level_camera_clean")
if level_gain is None:
    raise Exception("Missing level_motion_gain")
if threshold is None:
    raise Exception("Missing threshold_motion")
if blur is None:
    raise Exception("Missing blur_mask_soft_edge")
if out_mask is None:
    raise Exception("Missing OUT_motion_mask_raw")

# Optical Flow TOP is unsupported on this machine. Keep it visible as a note,
# but remove it from the live image-processing chain.
if optical is not None:
    try:
        optical.bypass = True
    except Exception:
        pass
    optical.nodeX = -560
    optical.nodeY = -110
    try:
        optical.color = (0.45, 0.22, 0.22)
    except Exception:
        pass

mono = create(cam, "monochromeTOP", "mono_camera_for_framediff", -560, 120)
prev = create(cam, "feedbackTOP", "feedback_prev_frame", -560, -40)
diff = create(cam, "compositeTOP", "composite_frame_difference", -340, 120)

connect(mono, 0, level_camera)
setpar(prev, ("top", "targettop", "target"), mono.path)
connect(diff, 0, mono)
connect(diff, 1, prev)

# Difference is the intended operation. If a build stores operation labels
# differently, subtract still creates a usable motion signal after thresholding.
if not setpar(diff, ("operand", "operation"), "difference"):
    setpar(diff, ("operand", "operation"), "subtract")

connect(level_gain, 0, diff)
connect(threshold, 0, level_gain)
connect(blur, 0, threshold)
connect(out_mask, 0, blur)

setpar(level_gain, ("multiply", "mult"), 6.0)
setpar(threshold, ("threshold",), 0.08)
setpar(blur, ("sizex", "size"), 18)
setpar(blur, ("sizey",), 18)

note = cam.op("README_opticalflow_fallback")
if note is not None:
    note.destroy()
note = cam.create("textDAT", "README_opticalflow_fallback")
note.nodeX = -900
note.nodeY = -260
note.text = (
    "Optical Flow TOP is not supported on this operating system, so this project uses a frame-difference fallback.\\n"
    "Live chain: level_camera_clean -> mono_camera_for_framediff -> composite_frame_difference -> level_motion_gain -> threshold_motion -> blur_mask_soft_edge -> OUT_motion_mask_raw.\\n"
    "Tune threshold_motion higher if the mask flickers when nobody moves. Tune level_motion_gain higher if gestures are too weak."
)

print("OK: Installed frame-difference fallback for /mosheng_project/01_camera_motion_mask.")
print("OK: opticalflow_motion is bypassed and no longer feeds the live mask.")
print("OK: live mask source =", diff.path)
