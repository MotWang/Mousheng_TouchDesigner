paths = [
    "/project1/bg",
    "/project1/render1",
    "/project1/switch1",
    "/project1/noise1",
    "/project1/phong1",
    "/TDCliServer/handler",
]
for path in paths:
    o = op(path)
    if o is None:
        print(path, "missing")
    else:
        print(path, "type=", o.type, "OPType=", getattr(o, "OPType", None), "class=", type(o).__name__)

print("create accepts string test:")
root = op("/")
tmp = root.op("_td_cli_type_probe")
if tmp is not None:
    tmp.destroy()
try:
    tmp = root.create("baseCOMP", "_td_cli_type_probe")
    print("string create ok", tmp.path, tmp.type)
    tmp.destroy()
except Exception as e:
    print("string create failed", repr(e))
