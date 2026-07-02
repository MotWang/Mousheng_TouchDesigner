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
mono = cam.op("mono_camera_for_framediff")
diff = cam.op("composite_frame_difference")
level_gain = cam.op("level_motion_gain")
threshold = cam.op("threshold_motion")
blur = cam.op("blur_mask_soft_edge")
out_mask = cam.op("OUT_motion_mask_raw")

if level_camera is None:
    raise Exception("Missing level_camera_clean")

if mono is None:
    mono = create(cam, "monochromeTOP", "mono_camera_for_framediff", -560, 120)
else:
    mono.nodeX = -560
    mono.nodeY = 120
connect(mono, 0, level_camera)

# Feedback TOP reports "Not enough sources specified" on this TD build.
# Replace it with Cache TOP, which reliably stores previous frames.
old_feedback = cam.op("feedback_prev_frame")
if old_feedback is not None:
    old_feedback.destroy()

cache = create(cam, "cacheTOP", "cache_prev_frame", -560, -40)
connect(cache, 0, mono)
setpar(cache, ("active",), True)
setpar(cache, ("cachesize",), 4)
setpar(cache, ("step",), 1)
setpar(cache, ("outputindexunit",), "indices")
setpar(cache, ("outputindex",), -2)
setpar(cache, ("alwayscook",), True)

if diff is None:
    diff = create(cam, "compositeTOP", "composite_frame_difference", -340, 120)
else:
    diff.nodeX = -340
    diff.nodeY = 120
connect(diff, 0, mono)
connect(diff, 1, cache)
if not setpar(diff, ("operand", "operation"), "difference"):
    setpar(diff, ("operand", "operation"), "subtract")

if level_gain is None:
    raise Exception("Missing level_motion_gain")
connect(level_gain, 0, diff)
setpar(level_gain, ("multiply", "mult"), 6.0)

if threshold is None:
    raise Exception("Missing threshold_motion")
connect(threshold, 0, level_gain)
setpar(threshold, ("threshold",), 0.08)

if blur is None:
    raise Exception("Missing blur_mask_soft_edge")
connect(blur, 0, threshold)
setpar(blur, ("sizex", "size"), 18)
setpar(blur, ("sizey",), 18)

if out_mask is None:
    raise Exception("Missing OUT_motion_mask_raw")
connect(out_mask, 0, blur)

note = cam.op("README_opticalflow_fallback")
if note is None:
    note = cam.create("textDAT", "README_opticalflow_fallback")
note.nodeX = -900
note.nodeY = -260
note.text = (
    "Optical Flow TOP and Feedback previous-frame mode are not used on this system.\\n"
    "Live chain: level_camera_clean -> mono_camera_for_framediff -> cache_prev_frame + composite_frame_difference -> level_motion_gain -> threshold_motion -> blur_mask_soft_edge -> OUT_motion_mask_raw.\\n"
    "cache_prev_frame stores the previous frame. composite_frame_difference compares current vs previous frame to detect motion.\\n"
    "Tune threshold_motion higher if the mask flickers when nobody moves. Tune level_motion_gain higher if gestures are too weak."
)

print("OK: Replaced feedback_prev_frame with cache_prev_frame.")
print("OK: live chain uses Cache TOP frame difference.")
