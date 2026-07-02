"""Dim bloom (safe) + dump sound logic and reveal structure for planning."""
OUTDIR = project.folder + '/outputs/'

# ---- 1. Dim the glow ----
g = op('/mosheng_project/07_grade_and_frame')
if g:
    b = g.op('bloom_restrained')
    if b:
        print('bloom before:', b.par.bloomthreshold.eval(), b.par.bloomintensity.eval())
        b.par.bloomthreshold = 0.82
        b.par.bloomintensity = 0.14
        print('bloom after :', b.par.bloomthreshold.eval(), b.par.bloomintensity.eval())
    v = g.op('hsv_vibrance_final')
    if v:
        v.par.valuemult = 1.0
    out = g.op('OUT_final_projection_graded')
    if out:
        out.cook(force=True)
        out.save(OUTDIR + 'dim_now.png')
        print('saved dim_now.png')

# ---- 2. Audio FX nodes ----
AUD = op('/mosheng_project/04_audio_reactivity')
print('===== FX / motion-sound nodes =====')
for o in AUD.children:
    n = o.name.lower()
    if any(k in n for k in ('fx', 'drop', 'brush', 'flower', 'diffus', 'water', 'gain', 'mix')):
        vol = getattr(o.par, 'volume', None)
        g2 = getattr(o.par, 'gain', None)
        f = getattr(o.par, 'file', None)
        pl = getattr(o.par, 'play', None)
        print('  %-26s %-13s vol=%s gain=%s play=%s file=%s' % (
            o.name, o.type,
            (vol.eval() if vol else '-'),
            (g2.eval() if g2 else '-'),
            (pl.eval() if pl else '-'),
            (f.eval().split('/')[-1] if f else '-')))

# ---- 3. _ink_sound function ----
c = op('/mosheng_project/00_control_panel/automation_heartbeat_controller')
t = c.text
i = t.find('def _ink_sound')
print('===== _ink_sound =====')
print(t[i:i + 1400] if i >= 0 else 'NOT FOUND')
print('INSPECT_SOUND_DONE')
