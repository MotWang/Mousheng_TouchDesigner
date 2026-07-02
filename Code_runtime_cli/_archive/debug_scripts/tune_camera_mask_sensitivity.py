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


def create(parent, type_name, name, x, y):
    old = parent.op(name)
    if old is not None:
        old.destroy()
    node = parent.create(type_name, name)
    node.nodeX = x
    node.nodeY = y
    return node


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
    raise Exception("Cannot find camera module")

camera = cam.op("camera_640x480")
level_camera = cam.op("level_camera_clean")
mono = cam.op("mono_camera_for_framediff")
cache = cam.op("cache_prev_frame")
diff = cam.op("composite_frame_difference")
level_gain = cam.op("level_motion_gain")
threshold = cam.op("threshold_motion")
blur = cam.op("blur_mask_soft_edge")
out_mask = cam.op("OUT_motion_mask_raw")

for node, name in [
    (camera, "camera_640x480"),
    (level_camera, "level_camera_clean"),
    (mono, "mono_camera_for_framediff"),
    (cache, "cache_prev_frame"),
    (diff, "composite_frame_difference"),
    (level_gain, "level_motion_gain"),
    (threshold, "threshold_motion"),
    (blur, "blur_mask_soft_edge"),
    (out_mask, "OUT_motion_mask_raw"),
]:
    if node is None:
        raise Exception("Missing " + name)

# Keep the downstream pipeline light and predictable. The camera source may still
# report a 1920x1080 physical mode, but this forces the TOP output to 640x480.
setpar(camera, ("outputresolution",), "custom")
setpar(camera, ("resolutionw",), 640)
setpar(camera, ("resolutionh",), 480)
setpar(camera, ("limitfps",), True)
setpar(camera, ("limitedfps",), 30)

setpar(level_camera, ("outputresolution",), "useinput")
setpar(mono, ("outputresolution",), "useinput")

# Make frame difference easier to see in normal indoor light.
setpar(cache, ("active",), True)
setpar(cache, ("cachesize",), 8)
setpar(cache, ("outputindexunit",), "indices")
setpar(cache, ("outputindex",), -2)
setpar(cache, ("alwayscook",), True)

if not setpar(diff, ("operand", "operation"), "difference"):
    setpar(diff, ("operand", "operation"), "subtract")

setpar(level_gain, ("multiply", "mult"), 18.0)
setpar(threshold, ("threshold",), 0.025)
setpar(blur, ("sizex", "size"), 22)
setpar(blur, ("sizey",), 22)

# Add a visible grayscale debug output before threshold. If this is black while
# waving, the camera image is not changing enough or the cache is not cooking.
debug = cam.op("OUT_motion_debug_before_threshold")
if debug is None:
    debug = create(cam, "nullTOP", "OUT_motion_debug_before_threshold", -120, -80)
else:
    debug.nodeX = -120
    debug.nodeY = -80
connect(debug, 0, level_gain)

connect(threshold, 0, level_gain)
connect(blur, 0, threshold)
connect(out_mask, 0, blur)

note = cam.op("README_mask_tuning")
if note is not None:
    note.destroy()
note = cam.create("textDAT", "README_mask_tuning")
note.nodeX = -900
note.nodeY = -420
note.text = (
    "Why black? The mask is supposed to be black when no movement is detected.\\n"
    "Check OUT_motion_debug_before_threshold while waving. If it flashes gray/white, detection works.\\n"
    "If OUT_motion_debug_before_threshold stays black, the camera image is static, blocked, too dark, or Cache TOP is not cooking.\\n"
    "If debug flashes but OUT_motion_mask_raw stays black, lower threshold_motion.\\n"
    "Current tuned values: level_motion_gain multiply=18, threshold_motion=0.025, cache outputindex=-2."
)

print("OK: tuned camera output to 640x480/30fps and increased frame-difference sensitivity.")
print("OK: added OUT_motion_debug_before_threshold.")
