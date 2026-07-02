"""Inspect current audio routing in /mosheng_project (read-only)."""
root = op('/mosheng_project')
print('===== OPS WITH AUDIO FILE PARAM =====')
for o in root.findChildren(maxDepth=20):
    fp = getattr(o.par, 'file', None)
    if fp is not None:
        v = str(fp.eval())
        if any(k in v.lower() for k in ('.wav', '.mp3', '/audio/', 'bgm', '/fx/')):
            print(o.path, '|', o.type, '|', v)

print('===== OPS NAMED audio/bgm/ambient/fx/sound/out =====')
for o in root.findChildren(maxDepth=20):
    n = o.name.lower()
    if any(k in n for k in ('bgm', 'audio', 'ambient', 'fx', 'sound', 'devout', 'adout', 'mix')):
        print(o.path, '|', o.type)

c = op('/mosheng_project/00_control_panel/automation_heartbeat_controller')
print('===== CONTROLLER _set_audio_mix =====', c is not None)
if c:
    t = c.text
    i = t.find('def _set_audio_mix')
    print(t[i:i + 1100] if i >= 0 else 'no _set_audio_mix def')
print('===== DONE =====')
