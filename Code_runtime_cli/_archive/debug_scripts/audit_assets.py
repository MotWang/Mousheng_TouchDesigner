"""Read-only audit: list every external-file reference in /mosheng_project,
whether it is absolute or relative, and whether the file exists. Also dump
project.folder. No changes made."""
import os
root = op('/mosheng_project')
pf = project.folder.replace('\\', '/')
print('PROJECT.FOLDER =', pf)
print('=' * 60)
rows = []
for o in root.findChildren(maxDepth=20):
    for pname in ('file', 'moviefile', 'audiofile', 'soundfile'):
        p = getattr(o.par, pname, None)
        if p is None:
            continue
        val = p.eval()
        if not val:
            continue
        v = val.replace('\\', '/')
        absp = v if os.path.isabs(v) else os.path.join(pf, v)
        kind = 'ABS' if os.path.isabs(v) else 'rel'
        inside = v.startswith(pf) if os.path.isabs(v) else True
        exists = os.path.exists(absp)
        rows.append((o.path, pname, kind, ('IN' if inside else 'OUTSIDE'),
                     ('ok' if exists else 'MISSING'), val))
absn = sum(1 for r in rows if r[2] == 'ABS')
outn = sum(1 for r in rows if r[3] == 'OUTSIDE')
missn = sum(1 for r in rows if r[4] == 'MISSING')
print('TOTAL file refs: %d | absolute: %d | outside-folder: %d | missing: %d'
      % (len(rows), absn, outn, missn))
print('-' * 60)
for path, pn, kind, inside, ex, val in rows:
    print('[%s|%s|%s] %s.%s = %s' % (kind, inside, ex, path.split('/mosheng_project/')[-1], pn, val))
print('AUDIT_DONE')
