"""Tame the slight over-exposure of revealed color + ready the fullscreen window.
Saves before/after full-reveal previews."""
OUTDIR = project.folder + '/outputs/'
root = op('/mosheng_project')
assets = root.op('02_visual_assets')
grade = root.op('07_grade_and_frame')


def sp(node, name, value):
    if node is None:
        return
    p = getattr(node.par, name, None)
    if p is not None:
        try:
            p.val = value
        except Exception:
            pass


def preview(tag):
    pre = grade.op('IN_pre')
    out = grade.op('OUT_final_projection_graded')
    orig = pre.par.top.eval()
    pre.par.top = '../02_visual_assets/OUT_color_bottom_layer'
    out.cook(force=True)
    out.save(OUTDIR + 'expo_%s.png' % tag)
    pre.par.top = orig
    out.cook(force=True)


preview('before')

# 1) Color enrich: less value/sat so bright pigments stop clipping.
for n in ('hsv_rich_season_pigment', 'hsv_color_rich'):
    o = assets.op(n)
    sp(o, 'saturationmult', 1.16)
    sp(o, 'valuemult', 1.0)
lc = assets.op('level_color_rich')
sp(lc, 'contrast', 1.0)
sp(lc, 'gamma1', 1.0)

# 2) Final grade: pull exposure down ~7%, soften contrast, neutral gamma,
#    compress the top end so highlights don't blow out, gentler bloom.
b = grade.op('bloom_restrained')
sp(b, 'bloomthreshold', 0.85)
sp(b, 'bloomintensity', 0.10)
v = grade.op('hsv_vibrance_final')
sp(v, 'saturationmult', 1.10)
sp(v, 'valuemult', 1.0)
lf = grade.op('level_final_grade')
sp(lf, 'gamma1', 1.0)
sp(lf, 'contrast', 1.0)
sp(lf, 'brightness1', 0.93)   # -7% exposure
sp(lf, 'outhigh', 0.96)       # roll the whites down off 1.0

grade.op('OUT_final_projection_graded').cook(force=True)
preview('after')

# 3) Fullscreen window: borderless, no cursor, fill the chosen display.
w = root.op('HDMI_fullscreen_output')
sp(w, 'borders', False)
sp(w, 'cursorvisible', 'never')
sp(w, 'size', 'fill')
print('exposure pulled back; window set borderless/no-cursor/fill')
print('FIX_EXPOSURE_DONE')
