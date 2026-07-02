"""Feed a solid 'all-motion' constant to prove the petal layer renders."""
fx = op('/mosheng_project/08_motion_fx')
accum = fx.op('drift_accum')
c = fx.op('_test_const') or fx.create('constantTOP', '_test_const')
c.par.colorr = 1
c.par.colorg = 1
c.par.colorb = 1
c.par.alpha = 1
c.par.outputresolution = 'custom'
c.par.resolutionw = 960
c.par.resolutionh = 540
try:
    accum.inputConnectors[0].disconnect()
except Exception:
    pass
accum.inputConnectors[0].connect(c)
print('CONST_TEST_ON')
