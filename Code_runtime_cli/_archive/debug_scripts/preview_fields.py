"""Field-only preview of all 4 seasons (sprite scatter on transparent)."""
comp = op('/mosheng_project/09_season_payoff')
field = comp.op('payoff_field')
swt = comp.op('sprite_select')
outp = comp.op('OUT_payoff')
drv = comp.op('payoff_driver')
drv.par.frameend = False
ebak = swt.par.index.expr
swt.par.index.expr = ''
field.par.vec0valuex = 1.0
for s, name in ((1, 'spring'), (2, 'summer'), (3, 'autumn'), (4, 'winter')):
    swt.par.index = s - 1
    field.par.vec0valuey = float(s)
    field.cook(force=True)
    outp.cook(force=True)
    # composite over a neutral grey so we can judge over a paint-like tone
    outp.save(project.folder + '/outputs/pf_%s.png' % name)
    print('saved pf_%s.png' % name)
swt.par.index.expr = ebak
field.par.vec0valuex = 0.0
drv.par.frameend = True
print('PREVIEW_FIELDS_DONE')
