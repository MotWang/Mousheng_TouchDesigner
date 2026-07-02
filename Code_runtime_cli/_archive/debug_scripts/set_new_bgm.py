"""Change BGM to 墨醒灵境 (bgm_main.mp3) for all seasons. Safe, idempotent."""
import os

AUD = op('/mosheng_project/04_audio_reactivity')
if AUD is None:
    raise Exception('missing /mosheng_project/04_audio_reactivity')

NEW = project.folder + '/assets/mosheng/audio/bgm/bgm_main.mp3'
print('NEW BGM:', NEW, '| exists:', os.path.isfile(NEW))
if not os.path.isfile(NEW):
    raise Exception('new bgm file not found: ' + NEW)

changed = []
for season in ('spring', 'summer', 'autumn', 'winter'):
    n = AUD.op('bgm_' + season)
    if n is None:
        print('  MISSING bgm_' + season)
        continue
    old = n.par.file.eval()
    n.par.file = NEW
    # Make BGM loop so the 4:55 track never runs out during long idle periods.
    for pname in ('loop', 'repeat'):
        p = getattr(n.par, pname, None)
        if p is not None:
            try:
                p.val = True
            except Exception:
                pass
    # Force the CHOP to re-read the new file.
    rl = getattr(n.par, 'reloadpulse', None) or getattr(n.par, 'reload', None)
    if rl is not None:
        try:
            rl.pulse()
        except Exception:
            try:
                rl.val = True
            except Exception:
                pass
    n.cook(force=True)
    changed.append((n.name, old, n.par.file.eval()))

for name, old, new in changed:
    print('  SET %-12s' % name, '->', new, '(was', old, ')')

# Report any audio errors so we know it loaded cleanly.
bad = [o.path for o in AUD.findChildren(maxDepth=2) if o.errors()]
print('AUDIO_ERRORS:', bad if bad else 'none')
print('SET_NEW_BGM_OK count=%d' % len(changed))
