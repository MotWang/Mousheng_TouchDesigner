"""Animated synthetic motion source to co-tune the ink-flow look over real frames."""
fx = op('/mosheng_project/08_motion_fx')
accum = fx.op('drift_accum')
r = fx.op('_cotune') or fx.create('rectangleTOP', '_cotune')
r.par.outputresolution = 'custom'
r.par.resolutionw = 960
r.par.resolutionh = 540
r.par.sizex = 0.10
r.par.sizey = 0.10
r.par.softness = 0.06
r.par.fillcolorr = 1
r.par.fillcolorg = 1
r.par.fillcolorb = 1
r.par.fillalpha = 1
r.par.bgcolorr = 0
r.par.bgcolorg = 0
r.par.bgcolorb = 0
r.par.bgalpha = 1
r.par.centerx.expr = '0.35*sin(absTime.seconds*1.6)'
r.par.centery.expr = '0.30*sin(absTime.seconds*2.3)'
try:
    accum.inputConnectors[0].disconnect()
except Exception:
    pass
accum.inputConnectors[0].connect(r)
print('COTUNE_SOURCE_ON')
