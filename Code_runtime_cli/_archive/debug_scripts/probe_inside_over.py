c = op("/mosheng_project/03_ink_reveal_composite")
for type_name in ["insideTOP", "overTOP", "matteTOP"]:
    try:
        n = c.create(type_name, "_probe_" + type_name)
        print(type_name, "OK", n.type)
        n.destroy()
    except Exception as e:
        print(type_name, "FAIL", str(e))
