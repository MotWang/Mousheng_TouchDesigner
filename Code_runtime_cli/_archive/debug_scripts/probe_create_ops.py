root = op("/")
container = root.op("_create_probe")
if container is not None:
    container.destroy()
container = root.create("baseCOMP", "_create_probe")

names = [
    "videodeviceinTOP",
    "opticalflowTOP",
    "opticalFlowTOP",
    "levelTOP",
    "thresholdTOP",
    "blurTOP",
    "feedbackTOP",
    "compositeTOP",
    "moviefileinTOP",
    "switchTOP",
    "constantTOP",
    "nullTOP",
    "monochromeTOP",
    "transformTOP",
    "fitTOP",
    "cacheTOP",
    "audiofileinCHOP",
    "analyzeCHOP",
    "mathCHOP",
    "nullCHOP",
    "webclientDAT",
    "textDAT",
    "tableDAT",
]
for name in names:
    try:
        node = container.create(name, "probe_" + name.replace("TOP", "").replace("CHOP", "").replace("DAT", ""))
        print(name, "OK", "type=", node.type)
    except Exception as e:
        print(name, "FAIL", str(e))

container.destroy()
