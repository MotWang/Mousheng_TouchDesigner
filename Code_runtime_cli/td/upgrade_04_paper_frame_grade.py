"""L3 grade: subtle paper, vignette and bloom; no crop, frame or displacement."""

ROOT = "/mosheng_project"
W, H = 1280, 720


def setpar(node, name, value):
    par = getattr(node.par, name, None)
    if par is not None:
        par.val = value


def fullres(node):
    setpar(node, "outputresolution", "custom")
    setpar(node, "resolutionw", W)
    setpar(node, "resolutionh", H)
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
if root is None:
    raise Exception("upgrade_04 missing " + ROOT)
source = "../06_water_highlight/OUT_water_composited"
if root.op("06_water_highlight") is None or root.op("06_water_highlight/OUT_water_composited") is None:
    source = "../03_ink_reveal_composite/OUT_final_projection"

grade = root.op("07_grade_and_frame") or root.create("baseCOMP", "07_grade_and_frame")
src = ensure(grade, "selectTOP", "IN_pre", -700, 100)
setpar(src, "top", source)

# A single restrained shader provides paper grain and vignette without
# no-input generator resolution ambiguity or black/cropped scroll borders.
shader = ensure(grade, "textDAT", "paper_vignette_shader", -500, -160)
shader.text = """layout(location = 0) out vec4 fragColor;
float hash21(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
}
void main() {
    vec2 uv = vUV.st;
    vec4 c = texture(sTD2DInputs[0], uv);
    vec2 q = (uv - 0.5) * vec2(1.0, 0.78);
    float vignette = 1.0 - smoothstep(0.30, 0.72, length(q)) * 0.075;
    float fiber = (hash21(floor(uv * vec2(900.0, 520.0))) - 0.5) * 0.018;
    c.rgb = clamp(c.rgb * vignette + fiber, 0.0, 1.0);
    fragColor = TDOutputSwizzle(c);
}
"""
paper = ensure(grade, "glslTOP", "paper_vignette_grade", -300, 100)
setpar(paper, "pixeldat", shader)
fullres(paper)
connect(paper, 0, src)

bloom = ensure(grade, "bloomTOP", "bloom_restrained", -100, 100)
setpar(bloom, "bloomthreshold", 0.78)
setpar(bloom, "bloomintensity", 0.14)
fullres(bloom)
connect(bloom, 0, paper)

final = ensure(grade, "levelTOP", "level_final_grade", 100, 100)
setpar(final, "gamma1", 0.98)
setpar(final, "contrast", 1.025)
fullres(final)
connect(final, 0, bloom)

out = ensure(grade, "nullTOP", "OUT_final_projection_graded", 300, 100)
fullres(out)
connect(out, 0, final)

panel = root.op("projection_panel")
if panel is None:
    raise Exception("upgrade_04 requires /mosheng_project/projection_panel")
setpar(panel, "top", out.path)
setpar(panel, "topfill", "outside")

note = ensure(grade, "textDAT", "README_grade_safe", -700, -160)
note.text = (
    "Safe final grade: subtle procedural paper + 7.5% vignette + restrained bloom.\n"
    "No crop, black border, hard scroll frame or breathing displacement.\n"
    "projection_panel points to OUT_final_projection_graded."
)
print("UPGRADE_04_OK graded output connected to projection_panel")
