"""More vivid color + stronger interaction. Reversible; prints old->new values.
Also saves a 'fully-revealed graded' preview before & after by briefly routing
the color layer through the final grade (restored immediately)."""

OUTDIR = project.folder + '/outputs/'


def sp(node, name, value, log):
    if node is None:
        return
    p = getattr(node.par, name, None)
    if p is None:
        return
    old = p.eval()
    try:
        p.val = value
        log.append('  %s.%s : %s -> %s' % (node.name, name, old, value))
    except Exception as e:
        log.append('  %s.%s FAILED %s' % (node.name, name, e))


def first(parent, names):
    for n in names:
        o = parent.op(n)
        if o is not None:
            return o
    return None


root = op('/mosheng_project')
assets = root.op('02_visual_assets')
ink = root.op('03_ink_reveal_composite')
grade = root.op('07_grade_and_frame')
cam = root.op('01_camera_motion_mask')
log = []


def preview(tag):
    """Render the color layer through the final grade to preview a full reveal."""
    if grade is None:
        return
    pre = grade.op('IN_pre')
    out = grade.op('OUT_final_projection_graded')
    color = '../02_visual_assets/OUT_color_bottom_layer'
    if pre is None or out is None:
        return
    orig = pre.par.top.eval()
    try:
        pre.par.top = color
        out.cook(force=True)
        out.save(OUTDIR + 'vivid_preview_%s.png' % tag)
        log.append('  saved vivid_preview_%s.png' % tag)
    finally:
        pre.par.top = orig
        out.cook(force=True)


# ---- BEFORE preview ----
preview('before')

# ================= VIVIDNESS =================
# 1) Color layer: richer pigment.
color_enrich = first(assets, ('hsv_rich_season_pigment', 'hsv_color_rich')) if assets else None
sp(color_enrich, 'saturationmult', 1.30, log)
sp(color_enrich, 'valuemult', 1.04, log)
lvl_color = first(assets, ('level_color_rich',)) if assets else None
sp(lvl_color, 'contrast', 1.08, log)
sp(lvl_color, 'gamma1', 0.95, log)

# 2) Final grade: stronger bloom + a global vibrance pass + a touch more contrast.
if grade is not None:
    bloom = grade.op('bloom_restrained')
    sp(bloom, 'bloomthreshold', 0.66, log)
    sp(bloom, 'bloomintensity', 0.32, log)

    # Insert hsv_vibrance_final between bloom and level_final_grade (idempotent).
    final = grade.op('level_final_grade')
    vib = grade.op('hsv_vibrance_final')
    if vib is None and bloom is not None and final is not None:
        vib = grade.create('hsvadjustTOP', 'hsv_vibrance_final')
        vib.nodeX, vib.nodeY = bloom.nodeX + 60, bloom.nodeY - 140
        vib.par.outputresolution = 'custom'
        vib.par.resolutionw = 1280
        vib.par.resolutionh = 720
        try:
            vib.inputConnectors[0].disconnect()
        except Exception:
            pass
        vib.inputConnectors[0].connect(bloom)
        try:
            final.inputConnectors[0].disconnect()
        except Exception:
            pass
        final.inputConnectors[0].connect(vib)
        log.append('  inserted hsv_vibrance_final between bloom and level_final_grade')
    sp(vib, 'saturationmult', 1.20, log)
    sp(vib, 'valuemult', 1.02, log)
    sp(final, 'contrast', 1.07, log)
    sp(final, 'gamma1', 0.96, log)

# ================= INTERACTION =================
# 3) Reveal brush: brighter + more sensitive so smaller gestures paint more color.
if ink is not None:
    brush = ink.op('level_immediate_motion_brush')
    sp(brush, 'brightness1', 2.4, log)
    sp(brush, 'inhigh', 0.13, log)
    shape = ink.op('level_shape_reveal_mask')
    sp(shape, 'inhigh', 0.26, log)
    sp(shape, 'gamma1', 0.70, log)
    gold = ink.op('blur_reveal_gold_dust')
    sp(gold, 'size', 9, log)

# 4) Camera: a bit more sensitive (tune down if false triggers in busy light).
if cam is not None:
    gain = first(cam, ('level_motion_gain',))
    sp(gain, 'multiply', 24.0, log)
    thr = first(cam, ('threshold_motion',))
    sp(thr, 'threshold', 0.019, log)

# ---- AFTER preview ----
preview('after')

print('===== ENHANCE CHANGES =====')
for line in log:
    print(line)
bad = [o.path for o in root.findChildren(maxDepth=20) if o.errors()]
print('ERRORS:', bad if bad else 'none')
print('ENHANCE_DONE')
