comp = op('/mosheng_project/09_season_payoff')
field = comp.op('payoff_field')
swt = comp.op('sprite_select')
drv = comp.op('payoff_driver')
drv.par.frameend = False
op('/mosheng_project/00_control_panel').store('auto_current_season', 3)
swt.par.index = 2
field.par.vec0valuex = 1.0
field.par.vec0valuey = 3.0
field.cook(force=True)
print('field ERR:', list(field.errors()))
print('field WARN:', list(field.warnings()))
try:
    print('sprite_select max=%.3f' % float(swt.numpyArray().max()))
except Exception as e:
    print('sprite err', e)
try:
    a = field.numpyArray()
    print('field max=%.3f mean=%.4f' % (float(a.max()), float(a.mean())))
except Exception as e:
    print('field err', e)
print('field res %dx%d' % (field.width, field.height))
cp = op('/mosheng_project/07_grade_and_frame/comp_payoff')
print('comp_payoff inputs:', [i.path for i in cp.inputs], 'operand', cp.par.operand.eval())
lf = op('/mosheng_project/07_grade_and_frame/level_final_grade')
print('level_final inputs:', [i.path for i in lf.inputs])
print('spr_2 file:', comp.op('spr_2').par.file.eval())
print('DEBUG_PAYOFF_DONE')
