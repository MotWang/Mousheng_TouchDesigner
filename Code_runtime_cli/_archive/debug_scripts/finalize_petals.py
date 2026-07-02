"""Make the ink-flow layer safe & tunable: translucent, screen-blended, toggle.
Then snapshot the LIVE scene to confirm it isn't degrading the painting."""
OUTDIR = project.folder + '/outputs/'
root = op('/mosheng_project')
fx = root.op('08_motion_fx')
accum = fx.op('drift_accum')
blur = fx.op('drift_blur')
outp = fx.op('OUT_petals')

# Only clear, deliberate motion emits ink.
accum.par.vec0valuez = 0.10

# Translucent opacity stage with an enable toggle.
lvl = fx.op('petals_opacity') or fx.create('levelTOP', 'petals_opacity')
lvl.nodeX, lvl.nodeY = blur.nodeX + 80, blur.nodeY
try:
    if not hasattr(fx.par, 'Petalsenable'):
        pg = fx.appendCustomPage('Mosheng')
        pg.appendToggle('Petalsenable', label='Petals Enable')
    fx.par.Petalsenable = 1
    lvl.par.opacity.expr = "0.5 * op('/mosheng_project/08_motion_fx').par.Petalsenable"
except Exception:
    lvl.par.opacity = 0.5
try:
    lvl.inputConnectors[0].disconnect()
except Exception:
    pass
lvl.inputConnectors[0].connect(blur)
try:
    outp.inputConnectors[0].disconnect()
except Exception:
    pass
outp.inputConnectors[0].connect(lvl)

# Screen-blend the ink so it luminously tints the painting instead of sitting on top.
comp = root.op('07_grade_and_frame/comp_motion_petals')
if comp is not None and hasattr(comp.par, 'operand'):
    try:
        comp.par.operand = 'screen'
    except Exception:
        pass

accum.cook(force=True)
op('/mosheng_project/07_grade_and_frame/OUT_final_projection_graded').save(OUTDIR + 'scene_final.png')
print('emitThresh=0.10, opacity stage + Petalsenable toggle, screen blend')
print('FINALIZE_PETALS_DONE')
