"""Crisper, longer-flowing ink trails."""
fx = op('/mosheng_project/08_motion_fx')
a = fx.op('drift_accum')
b = fx.op('drift_blur')
a.par.vec0valuex = 0.976   # longer-lasting flowing trails
a.par.vec0valuey = 0.62    # a touch more upward flow
b.par.size = 3.0           # less fog, more defined ink
a.cook(force=True)
print('REFINE_INK_DONE')
