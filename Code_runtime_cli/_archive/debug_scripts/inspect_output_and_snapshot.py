"""Inspect final output path, window comp, monitors; save a clean frame."""
import os

root = op('/mosheng_project')
pp = op('/mosheng_project/projection_panel')
print('projection_panel:', pp.type if pp else None,
      '| top =', (pp.par.top.eval() if (pp and hasattr(pp.par, 'top')) else 'NA'))

g = op('/mosheng_project/07_grade_and_frame/OUT_final_projection_graded')
core = op('/mosheng_project/03_ink_reveal_composite/OUT_final_projection')
print('07_graded:', (None if g is None else '%dx%d' % (g.width, g.height)))
print('03_core  :', (None if core is None else '%dx%d' % (core.width, core.height)))
finalop = g or core

# Resolve what projection_panel actually displays
disp_top = None
if pp and hasattr(pp.par, 'top'):
    disp_top = op(pp.par.top.eval()) if pp.par.top.eval() else None
if disp_top is not None:
    print('panel shows:', disp_top.path, '%dx%d' % (disp_top.width, disp_top.height))

# Monitors
try:
    print('MONITORS count=', len(monitors))
    for i, m in enumerate(monitors):
        print('  [%d]' % i, '%dx%d' % (m.width, m.height),
              'primary=%s' % m.isPrimary, 'left=%d top=%d' % (m.left, m.top))
except Exception as e:
    print('monitors err:', e)

# Window COMP params
w = op('/mosheng_project/HDMI_fullscreen_output')
if w:
    print('WINDOW COMP pars:')
    for p in w.pars():
        if p.name in ('win', 'winoperator', 'justifyto', 'justify', 'monitor',
                      'display', 'size', 'sizemode', 'opensize', 'borders',
                      'fillmode', 'topfill', 'w', 'h', 'winw', 'winh'):
            print('   ', p.name, '=', p.eval())

# Save a clean snapshot of the true output
out = project.folder + '/outputs/now_output.png'
try:
    finalop.save(out)
    print('SAVED_SNAPSHOT', out)
except Exception as e:
    print('snapshot err:', e)
print('INSPECT_DONE')
