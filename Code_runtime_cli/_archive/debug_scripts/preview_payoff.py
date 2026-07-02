"""Force each season's payoff at full burst and snapshot the composited scene."""
root = op('/mosheng_project')
comp = root.op('09_season_payoff')
ctrl = root.op('00_control_panel')
field = comp.op('payoff_field')
swt = comp.op('sprite_select')
out = op('/mosheng_project/07_grade_and_frame/OUT_final_projection_graded')
drv = comp.op('payoff_driver')
drv.par.frameend = False          # pause the driver so our forced values stick
orig = ctrl.fetch('auto_current_season', 1)
field.par.vec0valuex = 1.0        # full envelope
for s, name in ((1, 'spring'), (2, 'summer'), (3, 'autumn'), (4, 'winter')):
    ctrl.store('auto_current_season', s)
    field.par.vec0valuey = float(s)
    swt.par.index = s - 1
    for _ in range(6):
        field.cook(force=True)
    out.cook(force=True)
    out.save(project.folder + '/outputs/payoff_%s.png' % name)
    print('saved payoff_%s.png' % name)
ctrl.store('auto_current_season', orig)
field.par.vec0valuex = 0.0
drv.par.frameend = True            # resume driver
print('PREVIEW_PAYOFF_DONE')
