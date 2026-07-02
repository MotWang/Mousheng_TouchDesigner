for path in [
    "/mosheng_project/02_visual_assets/fallback_mono_xuanpaper",
    "/mosheng_project/02_visual_assets/fallback_color_gold_ink",
]:
    node = op(path)
    if node is not None:
        node.par.outputresolution = "custom"
        node.par.resolutionw = 1280
        node.par.resolutionh = 720
        print("set resolution", path, "1280x720")
