"""Temporarily drive the petal layer with a self-animating blob over real frames."""
fx = op('/mosheng_project/08_motion_fx')
accum = fx.op('drift_accum')
test = fx.op('_test_live') or fx.create('circleTOP', '_test_live')
test.par.outputresolution = 'custom'
test.par.resolutionw = 960
test.par.resolutionh = 540
test.par.radiusx = 0.05
test.par.radiusy = 0.05
test.par.centerx.expr = '0.55*sin(absTime.seconds*2.2)'
test.par.centery.expr = '0.35*sin(absTime.seconds*3.1)'
try:
    accum.inputConnectors[0].disconnect()
except Exception:
    pass
accum.inputConnectors[0].connect(test)
print('TEST_LIVE_ON (let it run ~2s, then run test_petals_live_off.py)')
