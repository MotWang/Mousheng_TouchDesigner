"""Localized static ink source in lower-center -> shows upward flow + diffusion."""
fx = op('/mosheng_project/08_motion_fx')
accum = fx.op('drift_accum')
r = fx.op('_test_spot') or fx.create('rectangleTOP', '_test_spot')
r.par.outputresolution = 'custom'
r.par.resolutionw = 960
r.par.resolutionh = 540
r.par.sizex = 0.16
r.par.sizey = 0.16
r.par.centerx = 0.5
r.par.centery = 0.22
r.par.fillcolorr = 1
r.par.fillcolorg = 1
r.par.fillcolorb = 1
r.par.fillalpha = 1
r.par.bgcolorr = 0
r.par.bgcolorg = 0
r.par.bgcolorb = 0
r.par.bgalpha = 1
r.par.softness = 0.05
try:
    accum.inputConnectors[0].disconnect()
except Exception:
    pass
accum.inputConnectors[0].connect(r)
print('SPOT_ON')
