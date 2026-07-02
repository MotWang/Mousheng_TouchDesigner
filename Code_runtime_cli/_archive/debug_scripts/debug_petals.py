"""Numeric debug of the petal layer buffers + uniforms."""
fx = op('/mosheng_project/08_motion_fx')
accum = fx.op('drift_accum')
src = accum.inputs[0] if accum.inputs else None
print('input0 =', src.path if src else None)
try:
    s = src.numpyArray()
    print('  input0 max=%.3f mean=%.4f shape=%s' % (float(s.max()), float(s.mean()), s.shape))
except Exception as e:
    print('  input0 sample err', e)
try:
    a = accum.numpyArray()
    print('accum   max=%.3f mean=%.4f' % (float(a.max()), float(a.mean())))
except Exception as e:
    print('accum sample err', e)
fb = fx.op('drift_fb')
try:
    f = fb.numpyArray()
    print('fb      max=%.3f mean=%.4f' % (float(f.max()), float(f.mean())))
except Exception as e:
    print('fb sample err', e)
print('vec0 params =', accum.par.vec0valuex.eval(), accum.par.vec0valuey.eval(),
      accum.par.vec0valuez.eval(), accum.par.vec0valuew.eval())
print('vec1 scol   =', accum.par.vec1valuex.eval(), accum.par.vec1valuey.eval(),
      accum.par.vec1valuez.eval())
print('DEBUG_PETALS_DONE')
