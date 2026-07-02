for path in [
    "/mosheng_project/03_ink_reveal_composite/composite_inside_reveal",
]:
    node = op(path)
    if node is not None:
        node.destroy()
        print("Removed stale node", path)
