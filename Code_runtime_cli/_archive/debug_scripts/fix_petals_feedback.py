"""Break the feedback cook loop: drift_fb gets prev frame via its 'top' param
(delayed), so its INPUT must be disconnected."""
fx = op('/mosheng_project/08_motion_fx')
accum = fx.op('drift_accum')
fb = fx.op('drift_fb')
# Break the same-cook dependency.
try:
    fb.inputConnectors[0].disconnect()
except Exception:
    pass
fb.par.top = accum.path
# Make sure accum still reads fb as input1.
try:
    accum.inputConnectors[1].disconnect()
except Exception:
    pass
accum.inputConnectors[1].connect(fb)
accum.cook(force=True)
print('warnings after fix:', accum.warnings())
print('FIX_PETALS_FEEDBACK_DONE')
