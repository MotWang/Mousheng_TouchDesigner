"""Snapshot the petal trail, then restore the live camera motion input."""
OUTDIR = project.folder + '/outputs/'
fx = op('/mosheng_project/08_motion_fx')
accum = fx.op('drift_accum')
inm = fx.op('IN_motion')
outp = fx.op('OUT_petals')
outp.cook(force=True)
outp.save(OUTDIR + 'petals_trail.png')
op('/mosheng_project/07_grade_and_frame/OUT_final_projection_graded').save(OUTDIR + 'petals_over_scene.png')
try:
    accum.inputConnectors[0].disconnect()
except Exception:
    pass
accum.inputConnectors[0].connect(inm)
t = fx.op('_test_live')
if t:
    t.destroy()
print('TEST_LIVE_OFF: saved petals_trail.png + petals_over_scene.png; restored camera input')
