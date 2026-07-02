"""List camera/motion-mask nodes and key params."""
cam = op('/mosheng_project/01_camera_motion_mask')
print('CAM children:')
for o in cam.children:
    keys = []
    for pn in ('threshold', 'multiply', 'mult', 'gain', 'size', 'brightness1', 'inhigh', 'inlow'):
        p = getattr(o.par, pn, None)
        if p is not None:
            keys.append('%s=%s' % (pn, p.eval()))
    print('  %-34s %-16s %s' % (o.name, o.type, ' '.join(keys)))
print('CAM_DONE')
