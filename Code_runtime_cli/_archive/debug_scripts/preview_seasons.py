"""Snapshot each season's color layer through the final grade (for review)."""
OUTDIR = project.folder + '/outputs/'
grade = op('/mosheng_project/07_grade_and_frame')
pre = grade.op('IN_pre')
out = grade.op('OUT_final_projection_graded')
csw = op('/mosheng_project/02_visual_assets/switch_color_season')
orig_top = pre.par.top.eval()
orig_idx = csw.par.index.eval()
try:
    for i, name in ((1, 'spring'), (2, 'summer'), (3, 'autumn'), (4, 'winter')):
        csw.par.index = i
        pre.par.top = '../02_visual_assets/OUT_color_bottom_layer'
        out.cook(force=True)
        out.save(OUTDIR + 'season_%s.png' % name)
        print('saved season_%s.png' % name)
finally:
    pre.par.top = orig_top
    csw.par.index = orig_idx
    out.cook(force=True)
print('PREVIEW_SEASONS_DONE')
