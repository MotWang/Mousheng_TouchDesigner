"""Season-tinted petal / ink-trace drift driven by hand motion.

08_motion_fx:
  IN_motion(camera motion mask) -> drift_accum(GLSL: emit season-colored specks
  where motion, drift upward + curl sway, decay) <-> drift_fb(feedback)
  -> drift_blur -> OUT_petals
Composited 'over' the scene inside 07_grade_and_frame (before paper/bloom/grade),
so petals also pick up the soft bloom. Season color follows switch_color_season.
Ends with a synthetic-motion preview snapshot. Idempotent.
"""
OUTDIR = project.folder + '/outputs/'
root = op('/mosheng_project')
W, H = 960, 540


def sp(node, name, value):
    p = getattr(node.par, name, None)
    if p is not None:
        try:
            p.val = value
        except Exception:
            pass


def expr(node, name, e):
    p = getattr(node.par, name, None)
    if p is not None:
        p.expr = e


def ensure(parent, typ, name, x, y):
    o = parent.op(name) or parent.create(typ, name)
    o.nodeX, o.nodeY = x, y
    return o


def conn(dst, idx, src):
    try:
        dst.inputConnectors[idx].disconnect()
    except Exception:
        pass
    dst.inputConnectors[idx].connect(src)


fx = root.op('08_motion_fx') or root.create('baseCOMP', '08_motion_fx')
fx.nodeX, fx.nodeY = 100, -1100

inm = ensure(fx, 'selectTOP', 'IN_motion', -700, 100)
sp(inm, 'top', '../01_camera_motion_mask/OUT_motion_mask_raw')

accum = ensure(fx, 'glslTOP', 'drift_accum', -480, 100)
sp(accum, 'outputresolution', 'custom')
sp(accum, 'resolutionw', W)
sp(accum, 'resolutionh', H)
sp(accum, 'format', 'rgba16float')
sp(accum, 'vec0name', 'params')
sp(accum, 'vec0valuex', 0.955)   # decay (trail life)
sp(accum, 'vec0valuey', 0.5)     # drift speed (upward float)
sp(accum, 'vec0valuez', 0.22)    # emit threshold (motion needed)
expr(accum, 'vec0valuew', 'absTime.seconds')
sp(accum, 'vec1name', 'scol')
# Season color follows switch_color_season index (1..4); fractional during turns.
TBL = "[(1.0,0.72,0.80),(0.42,0.80,0.58),(1.0,0.50,0.20),(0.82,0.90,1.0)]"
idx = "min(3,max(0,int(op('/mosheng_project/02_visual_assets/switch_color_season').par.index)-1))"
expr(accum, 'vec1valuex', "%s[%s][0]" % (TBL, idx))
expr(accum, 'vec1valuey', "%s[%s][1]" % (TBL, idx))
expr(accum, 'vec1valuez', "%s[%s][2]" % (TBL, idx))

dat = ensure(fx, 'textDAT', 'drift_accum_pixeldat', -480, -80)
dat.text = '''out vec4 fragColor;
uniform vec4 params;  // x=decay y=driftSpeed z=emitThresh w=time
uniform vec4 scol;    // rgb=season color
float hash21(vec2 p){ return fract(sin(dot(p, vec2(127.1,311.7)))*43758.5453); }
float vnoise(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f);
  return mix(mix(hash21(i),hash21(i+vec2(1,0)),f.x),
             mix(hash21(i+vec2(0,1)),hash21(i+vec2(1,1)),f.x), f.y); }
void main(){
  vec2 uv = vUV.st;
  vec2 ts = 1.0/vec2(textureSize(sTD2DInputs[1],0));
  float t = params.w;
  // Upward float with gentle horizontal sway (curl-ish) -> petals/ink rising.
  float sway = vnoise(uv*5.0 + vec2(0.0, t*0.6)) - 0.5;
  vec2 drift = vec2(sway*0.8, 1.0) * params.y;
  vec4 prev = texture(sTD2DInputs[1], uv - drift*ts*55.0) * params.x;
  // Emit speckled (petal-like) where there is real motion now.
  float m = texture(sTD2DInputs[0], uv).r;
  float speck = step(0.62, hash21(floor(uv*vec2(110.0,72.0) + floor(t*9.0))));
  float emit = (m > params.z) ? speck : 0.0;
  vec4 newc = vec4(scol.rgb, 1.0) * emit;
  fragColor = TDOutputSwizzle(max(prev, newc));
}
'''
sp(accum, 'pixeldat', dat.path)

fb = ensure(fx, 'feedbackTOP', 'drift_fb', -300, 230)
sp(fb, 'top', accum.path)
conn(fb, 0, accum)
conn(accum, 0, inm)
conn(accum, 1, fb)

blur = ensure(fx, 'blurTOP', 'drift_blur', -120, 100)
sp(blur, 'size', 2.0)
conn(blur, 0, accum)

outp = ensure(fx, 'nullTOP', 'OUT_petals', 80, 100)
conn(outp, 0, blur)

# ---- composite into 07 before paper/bloom/grade ----
grade = root.op('07_grade_and_frame')
pre = grade.op('IN_pre')
paper = grade.op('paper_vignette_grade')
inpet = ensure(grade, 'selectTOP', 'IN_petals', pre.nodeX, pre.nodeY - 160)
sp(inpet, 'top', '../08_motion_fx/OUT_petals')
comp = ensure(grade, 'compositeTOP', 'comp_motion_petals', pre.nodeX + 150, pre.nodeY)
sp(comp, 'outputresolution', 'custom')
sp(comp, 'resolutionw', 1280)
sp(comp, 'resolutionh', 720)
sp(comp, 'operand', 'over')
conn(comp, 0, pre)
conn(comp, 1, inpet)
conn(paper, 0, comp)
print('petals layer built + composited into 07 (over, before grade)')

# ---- preview with synthetic moving motion ----
test = fx.op('_test_blob') or fx.create('circleTOP', '_test_blob')
sp(test, 'outputresolution', 'custom')
sp(test, 'resolutionw', W)
sp(test, 'resolutionh', H)
sp(test, 'radiusx', 0.04)
sp(test, 'radiusy', 0.04)
orig = inm.par.top.eval()
conn(accum, 0, test)
import math
for k in range(60):
    sp(test, 'centerx', -0.6 + 1.2 * (k / 59.0))
    sp(test, 'centery', -0.3 + 0.4 * math.sin(k * 0.3))
    accum.cook(force=True)
outp.cook(force=True)
outp.save(OUTDIR + 'petals_preview.png')
print('saved petals_preview.png')
# restore live motion input, remove test blob
conn(accum, 0, inm)
test.destroy()
print('BUILD_MOTION_PETALS_DONE')
