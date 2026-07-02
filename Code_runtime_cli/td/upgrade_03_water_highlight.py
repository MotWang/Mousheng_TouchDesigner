"""Optional L2 wet-ink edge highlight. Default off, 480x270 internal."""

ROOT = "/mosheng_project"
W, H = 1280, 720


def setpar(node, name, value):
    par = getattr(node.par, name, None)
    if par is not None:
        par.val = value


def resolution(node, w, h):
    setpar(node, "outputresolution", "custom")
    setpar(node, "resolutionw", w)
    setpar(node, "resolutionh", h)
    setpar(node, "fillmode", "outside")


def ensure(parent, typ, name, x, y):
    node = parent.op(name) or parent.create(typ, name)
    node.nodeX, node.nodeY = x, y
    return node


def connect(dst, index, src):
    try:
        dst.inputConnectors[index].disconnect()
    except Exception:
        pass
    dst.inputConnectors[index].connect(src)


root = op(ROOT)
ink = op(ROOT + "/03_ink_reveal_composite")
if root is None or ink is None or ink.op("OUT_final_projection") is None or ink.op("OUT_ink_mask_final") is None:
    raise Exception("upgrade_03 requires stable 03 outputs")

water = root.op("06_water_highlight") or root.create("baseCOMP", "06_water_highlight")
try:
    if getattr(water.par, "Waterenable", None) is None:
        water.appendCustomPage("Mosheng").appendToggle("Waterenable", label="Water Enable")
    water.par.Waterenable = 0
except Exception:
    pass

main = ensure(water, "selectTOP", "IN_main", -720, 100)
mask = ensure(water, "selectTOP", "IN_mask", -720, -120)
setpar(main, "top", "../03_ink_reveal_composite/OUT_final_projection")
setpar(mask, "top", "../03_ink_reveal_composite/OUT_ink_mask_final")

mask_lo = ensure(water, "resolutionTOP", "mask_480x270", -520, -120)
resolution(mask_lo, 480, 270)
connect(mask_lo, 0, mask)

edge = ensure(water, "edgeTOP", "wet_ink_edge", -340, -120)
resolution(edge, 480, 270)
connect(edge, 0, mask_lo)
blur = ensure(water, "blurTOP", "wet_ink_edge_soft", -160, -120)
setpar(blur, "size", 5)
resolution(blur, 480, 270)
connect(blur, 0, edge)
level = ensure(water, "levelTOP", "wet_ink_edge_restrained", 20, -120)
setpar(level, "gamma1", 0.72)
setpar(level, "brightness1", 0.22)
setpar(level, "contrast", 1.15)
resolution(level, W, H)
connect(level, 0, blur)

wet = ensure(water, "compositeTOP", "screen_wet_edge_over_main", 200, 100)
setpar(wet, "operand", "screen")
resolution(wet, W, H)
connect(wet, 0, main)
connect(wet, 1, level)

switch = ensure(water, "switchTOP", "switch_water_enable", 390, 100)
resolution(switch, W, H)
connect(switch, 0, main)
connect(switch, 1, wet)
try:
    switch.par.index.expr = "int(parent().par.Waterenable)"
except Exception:
    switch.par.index = 0

out = ensure(water, "nullTOP", "OUT_water_composited", 580, 100)
resolution(out, W, H)
connect(out, 0, switch)
note = ensure(water, "textDAT", "README_water_safe", -720, -300)
note.text = (
    "Optional wet-ink edge highlight. Internal resolution 480x270.\n"
    "Waterenable defaults to Off. Output is always 1280x720."
)
print("UPGRADE_03_OK optional wet edge built; Waterenable=0")
