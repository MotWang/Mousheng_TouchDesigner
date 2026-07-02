n = op("/mosheng_project/01_camera_motion_mask/cache_prev_frame")
print("before", n.par.outputindex.val, n.par.outputindex.eval())
n.par.outputindexunit = "indices"
n.par.cachesize = 8
n.par.alwayscook = True
n.par.active = True
n.par.outputindex = 2
print("after assign", n.par.outputindex.val, n.par.outputindex.eval())
try:
    n.par.outputindex.expr = "2"
    print("after expr", n.par.outputindex.val, n.par.outputindex.eval(), n.par.outputindex.expr)
except Exception as e:
    print("expr failed", repr(e))
