c = op("/mosheng_project/01_camera_motion_mask")
n = c.op("_probe_cache_params")
if n is not None:
    n.destroy()
n = c.create("cacheTOP", "_probe_cache_params")
for p in n.pars():
    print(p.name, "=", p.val)
n.destroy()
