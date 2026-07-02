"""Noise-robust motion detection. Strength of interaction comes from the reveal
brush (already boosted), NOT from a hair-trigger camera. Re-snapshot rest mask."""
OUTDIR = project.folder + '/outputs/'
cam = op('/mosheng_project/01_camera_motion_mask')
log = []


def sp(name, par, value):
    o = cam.op(name)
    if o is None:
        log.append('  MISSING ' + name); return
    p = getattr(o.par, par, None)
    if p is None:
        log.append('  %s has no %s' % (name, par)); return
    old = p.eval()
    p.val = value
    log.append('  %s.%s : %s -> %s' % (name, par, old, value))


# Reject sensor noise at rest, still responsive to real gestures.
sp('threshold_motion', 'threshold', 0.013)
sp('level_motion_gain', 'brightness1', 3.4)
sp('level_small_gesture_gain', 'brightness1', 2.4)

for line in log:
    print(line)

m = cam.op('OUT_motion_mask_raw')
if m is not None:
    m.cook(force=True)
    m.save(OUTDIR + 'rest_motion_mask2.png')
    # crude white fraction estimate
    print('saved rest_motion_mask2.png')
print('CAMERA_ROBUST_DONE  (hold still -> should be mostly black; wave -> white where hand is)')
