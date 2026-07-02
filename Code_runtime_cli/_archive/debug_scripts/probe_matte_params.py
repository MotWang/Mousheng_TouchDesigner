c = op("/mosheng_project/03_ink_reveal_composite")
n = c.op("_probe_matte")
if n is not None:
    n.destroy()
n = c.create("matteTOP", "_probe_matte")
for p in n.pars():
    print(p.name, "=", p.val)
n.destroy()
