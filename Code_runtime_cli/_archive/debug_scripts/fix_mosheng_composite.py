def create(parent_op, type_name, name, x, y):
    old = parent_op.op(name)
    if old is not None:
        old.destroy()
    node = parent_op.create(type_name, name)
    node.nodeX = x
    node.nodeY = y
    return node


def connect(dst, index, src):
    try:
        dst.inputConnectors[index].connect(src)
        return True
    except Exception as e:
        print("connect failed", dst.path, index, src.path, e)
        return False


ink = op("/mosheng_project/03_ink_reveal_composite")
mono_in = ink.op("IN_mono_layer")
color_in = ink.op("IN_color_layer")
mask_final = ink.op("OUT_ink_mask_final")

matte = create(ink, "matteTOP", "matte_color_by_ink_mask", -220, -120)
over = create(ink, "overTOP", "over_color_on_mono", 10, -120)
final_out = ink.op("OUT_final_projection")
if final_out is not None:
    final_out.destroy()
final_out = create(ink, "nullTOP", "OUT_final_projection", 240, -120)

connect(matte, 0, color_in)
connect(matte, 1, mask_final)
try:
    matte.par.mattechannel = "luminance"
except Exception:
    try:
        matte.par.mattechannel = "red"
    except Exception:
        pass

# In Over TOP, first input is foreground and second input is background.
connect(over, 0, matte)
connect(over, 1, mono_in)
connect(final_out, 0, over)

print("Rebuilt final composite as: color -> Matte(mask luminance) -> Over(mono).")
